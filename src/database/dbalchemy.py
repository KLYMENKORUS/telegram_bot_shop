from typing import List

from sqlalchemy.ext.asyncio import create_async_engine, \
    async_sessionmaker, AsyncSession
from sqlalchemy import insert, select, func, delete
from src.config import DATABASE_URL
from src.database.tables import Category, Product


class Singleton(type):
    """
    Патерн Singleton предоставляет механизм создания одного
    и только одного объекта класса,
    и предоставление к нему глобальную точку доступа.
    """
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs, **kwargs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class DBMethods:
    """Интерфейс для реализации работы с данными в бд"""

    def __init__(self, db_session) -> None:
        self.db_session = db_session

    async def add(self, model, **kwargs):
        """Добавление новой записи в бд"""
        async with self.db_session() as session:
            async with session.begin():
                new_object = await session.execute(insert(model).values(kwargs))
                return new_object.scalars().first()

    async def get_obj(self, model, **kwargs):
        """Получение текущего объекта с бд"""
        async with self.db_session() as session:
            async with session.begin():
                get_object = await session.execute(select(model).filter_by(id=kwargs.get('id')))
                return get_object.scalars().first()

    async def get_all_obj(self, model):
        """Получение всех объектов с бд по данной модели"""
        async with self.db_session() as session:
            async with session.begin():
                all_objects = await session.execute(select(model))
                return [obj[0] for obj in all_objects.fetchall()]

    async def filter_all_obj(self, model, **kwargs):
        """ПОлучение всех объектов с бд по данной модели по фильтру"""
        async with self.db_session() as session:
            async with session.begin():
                filtered_objects = await session.execute(
                    select(model).filter_by(category_id=kwargs.get('category_id'))
                )
                return [obj[0] for obj in filtered_objects.fetchall()]

    async def get_count_obj(self, model, **kwargs):
        """Получение количества объектов"""
        async with self.db_session() as session:
            async with session.begin():
                count = await session.execute(
                    select(func.count(model.id)).
                    filter_by(category_id=kwargs.get('category_id')))
                return count.scalars().first()

    async def delete_obj(self, model, **kwargs):
        """Удаление объектов с бд"""
        async with self.db_session() as session:
            async with session.begin():
                category = await session.execute(
                    delete(model).filter_by(id=kwargs.get('id')).returning(model.id))
                return category.scalars().first()


class DBManager(metaclass=Singleton):
    """
    Класс менеджер для работы с БД
    """
    def __init__(self):
        self.engine = create_async_engine(DATABASE_URL, future=True, echo=True)
        self.async_session_maker = async_sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession)
        self.__crud_db = DBMethods(self.async_session_maker)

    # ********** OPERATIONS WITH CATEGORIES **********

    async def add_category(self, name: str) -> Category:
        """Добавление новой категории"""
        return await self.__crud_db.add(Category, name=name)

    async def get_category(self, category_id: int) -> Category:
        """Получение конкретной категории"""
        return await self.__crud_db.get_obj(Category, id=category_id)

    async def delete_category(self, category_id: int) -> Category:
        """Удаление категории"""
        return await self.__crud_db.delete_obj(Category, id=category_id)

    async def all_categories(self) -> List[Category]:
        """Вывод всех категорий"""
        return await self.__crud_db.get_all_obj(Category)

    async def get_count_products(self, category_id: int) -> int:
        """Получение количества продуктов"""
        return await self.__crud_db.get_count_obj(Product, category_id=category_id)

    # ********** END OPERATIONS WITH CATEGORIES **********

    # ********** OPERATIONS WITH PRODUCTS **********
    async def add_product(self, **kwargs) -> Product:
        """Добавление нового товара"""
        return await self.__crud_db.add(
            Product,
            name=kwargs.get('name'),
            title=kwargs.get('title'),
            price=kwargs.get('price'),
            quantity=kwargs.get('quantity'),
            category_id=kwargs.get('category_id')
        )

    async def all_products(self, category_id: int) -> List[Product]:
        """Вывод всех категорий"""
        return await self.__crud_db.filter_all_obj(
            Product, category_id=category_id)

    async def get_product(self, product_id: int) -> Product:
        return await self.__crud_db.get_obj(Product, id=product_id)


