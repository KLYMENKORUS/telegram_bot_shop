from datetime import datetime
from typing import List

from sqlalchemy.ext.asyncio import create_async_engine, \
    async_sessionmaker, AsyncSession
from sqlalchemy import insert, select, func, delete, update
from src.config import DATABASE_URL
from src.database.tables import Category, Product, Order


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

    async def select_order_quantity(self, **kwargs) -> Order:
        """Возвращает количество товара в заказе"""
        async with self.db_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(Order).
                    filter_by(product_id=kwargs.get('product_id'))
                )
                return result.scalars().first()

    async def update_order_value(self, **kwargs):
        """
        Обновляет данные указанной позиции заказа
        в соответствии с номером товара - rownum
        """
        async with self.db_session() as session:
            async with session.begin():
                await session.execute(
                    update(Order).filter_by(product_id=kwargs.get('product_id')).
                    values(quantity=kwargs.get('quantity'))
                )

    async def update_product_value(self, **kwargs):
        """
        Обновляет количество товара на складе
        в соответствии с номером товара - rownum
        """
        async with self.db_session() as session:
            async with session.begin():
                await session.execute(
                    update(Product).filter_by(id=kwargs.get('id')).
                    values(quantity=kwargs.get('quantity'))
                )


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

    async def delete_product(self, product_id: int) -> Product:
        """Удаление товара с бд"""
        return await self.__crud_db.delete_obj(Product, id=product_id)

    # ********** END OPERATIONS WITH PRODUCTS **********

    # ********** OPERATIONS WITH ORDERS **********
    async def add_orders(self, quantity: int, product_id: int, user_id: int):
        """Метод заполнения заказа"""

        all_id_products = await self.__crud_db.get_all_obj(Order)

        if product_id in [product.product_id for product in all_id_products]:
            quantity_order = await self.__crud_db.select_order_quantity(product_id=product_id)
            quantity_order = quantity_order.quantity + 1
            await self.__crud_db.update_order_value(product_id=product_id, quantity=quantity_order)

            quantity_product = await self.get_product(product_id)
            quantity_product = quantity_product.quantity - 1
            await self.__crud_db.update_product_value(id=product_id, quantity=quantity_product)

        else:
            await self.__crud_db.add(
                Order,
                quantity=quantity,
                product_id=product_id,
                user_id=user_id,
                data=datetime.now()
            )

            quantity_product = await self.get_product(product_id)
            quantity_product = quantity_product.quantity - 1
            await self.__crud_db.update_product_value(id=product_id, quantity=quantity_product)





