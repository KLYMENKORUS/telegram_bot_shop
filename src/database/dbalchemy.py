import array as arr
from datetime import datetime
from functools import wraps
from typing import List
from sqlalchemy.ext.asyncio import create_async_engine, \
    async_sessionmaker, AsyncSession
from sqlalchemy import insert, select, func, delete, update
from src.config import DATABASE_URL
from src.database.tables import Category, Product, Order


# ********** DECORATORS **********
def connect_session_to_database(db_session):
    def connect(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with db_session() as session:
                async with session.begin():
                    return await func(*args, session, **kwargs)

        return wrapper
    return connect


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

    # ********** CONNECT TO DB ********
    __engine = create_async_engine(DATABASE_URL, future=True, echo=True)
    __async_session_maker = async_sessionmaker(
        __engine, expire_on_commit=False, class_=AsyncSession
    )

    # ********** ALL OPERATIONS **********

    @connect_session_to_database(__async_session_maker)
    async def add(self, model, session: AsyncSession, **kwargs):
        """Добавление новой записи в бд"""
        new_object = await session.execute(insert(model).values(kwargs))
        return new_object.scalars().first()

    @connect_session_to_database(__async_session_maker)
    async def get_obj(self, model, session: AsyncSession, **kwargs):
        """Получение текущего объекта с бд"""
        get_object = await session.execute(
            select(model).filter_by(id=kwargs.get('id')))
        return get_object.scalars().first()

    @connect_session_to_database(__async_session_maker)
    async def get_all_obj(self, model, session: AsyncSession):
        """Получение всех объектов с бд по данной модели"""
        all_objects = await session.execute(select(model))
        return [obj[0] for obj in all_objects.fetchall()]

    @connect_session_to_database(__async_session_maker)
    async def filter_all_obj(self, model, session: AsyncSession, **kwargs):
        """Пoлучение всех объектов с бд по данной модели по фильтру"""
        filtered_objects = await session.execute(
            select(model).filter_by(category_id=kwargs.get('category_id'))
            )
        return [obj[0] for obj in filtered_objects.fetchall()]

    @connect_session_to_database(__async_session_maker)
    async def get_count_obj(self, model, session: AsyncSession, **kwargs):
        """Получение количества объектов"""
        count = await session.execute(
            select(func.count(model.id)).
            filter_by(category_id=kwargs.get('category_id'))
        )
        return count.scalars().first()

    @connect_session_to_database(__async_session_maker)
    async def delete_obj(self, model, session: AsyncSession, **kwargs):
        """Удаление объектов с бд"""
        category = await session.execute(
            delete(model).filter_by(id=kwargs.get('id')).returning(model.id))
        return category.scalars().first()

    # ********** ORDERS OPERATIONS **********
    @connect_session_to_database(__async_session_maker)
    async def select_order_quantity(self, session: AsyncSession, **kwargs) -> Order:
        """Возвращает количество товара в заказе"""
        result = await session.execute(
            select(Order).filter_by(product_id=kwargs.get('product_id'))
            )
        return result.scalars().first()

    @connect_session_to_database(__async_session_maker)
    async def update_order_value(self, session: AsyncSession, **kwargs) -> None:
        """
        Обновляет данные указанной позиции заказа
        в соответствии с номером товара - rownum
        """
        await session.execute(
            update(Order).filter_by(product_id=kwargs.get('product_id')).
            values(quantity=kwargs.get('quantity'))
        )

    @connect_session_to_database(__async_session_maker)
    async def update_product_value(self, session: AsyncSession, **kwargs) -> None:
        """
        Обновляет количество товара на складе
        в соответствии с номером товара - rownum
        """
        await session.execute(
            update(Product).filter_by(id=kwargs.get('id')).
            values(quantity=kwargs.get('quantity'))
        )

    @connect_session_to_database(__async_session_maker)
    async def count_rows_order(self, session: AsyncSession) -> int:
        """Возвращает количество позиций в заказе"""
        result = await session.execute(
            select(func.count(Order.product_id))
        )
        return result.scalars().first()


class DBManager(metaclass=Singleton):
    """
    Класс менеджер для работы с БД
    """
    def __init__(self):
        self.__crud_db = DBMethods()

    # ********** OTHER OPERATIONS WITH DATABASE **********
    async def __update_product_quantity(self, product_id: int):
        """Обновление количества товара в бд"""

        quantity_product = await self.get_product(product_id)
        quantity_product = quantity_product.quantity - 1
        await self.__crud_db.update_product_value(
            id=product_id, quantity=quantity_product)

    async def __search_product_in_order(self, all_products: arr.array, product_id: int,
                                        left: int, right: int) -> bool | None:
        """Поиск товара в заказе"""
        midd = (left + right) // 2

        if all_products[midd] == product_id:
            return True
        elif product_id < all_products[midd]:
            await self.__search_product_in_order(all_products, product_id, left, midd - 1)
        else:
            await self.__search_product_in_order(all_products, product_id, midd + 1, right)

    async def __update_quantity_product_in_order(self, product_id: int):
        """Обновление количества товара в заказе"""
        quantity_order = await self.select_order_quantity(product_id)
        quantity_order += 1
        await self.__crud_db.update_order_value(
            product_id=product_id, quantity=quantity_order)

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
        """Вывод всех продуктов"""
        return await self.__crud_db.filter_all_obj(
            Product, category_id=category_id)

    async def get_product(self, product_id: int) -> Product:
        return await self.__crud_db.get_obj(Product, id=product_id)

    async def delete_product(self, product_id: int) -> Product:
        """Удаление товара с бд"""
        return await self.__crud_db.delete_obj(Product, id=product_id)

    # ********** END OPERATIONS WITH PRODUCTS **********

    # ********** OPERATIONS WITH ORDERS **********
    async def add_orders(self, quantity: int, product_id: int, user_id: int) -> None:
        """Метод заполнения заказа"""

        all_id_products = await self.select_all_product_id()
        left, right = (0, len(all_id_products) - 1)
        search_product = await self.__search_product_in_order(
            all_id_products, product_id, left, right
        )

        if search_product:
            await self.__update_quantity_product_in_order(product_id)
            await self.__update_product_quantity(product_id)

        else:
            await self.__crud_db.add(
                Order,
                quantity=quantity,
                product_id=product_id,
                user_id=user_id,
                data=datetime.now()
            )
            await self.__update_product_quantity(product_id)

    async def count_rows_order(self) -> int:
        """Возвращает количество позиций в заказе"""
        return await self.__crud_db.count_rows_order()

    async def select_all_product_order(self) -> List[Order]:
        """получаем список всех товаров в заказе"""
        return await self.__crud_db.get_all_obj(Order)

    async def select_all_product_id(self) -> arr.array:
        """Получение со списка товаров в заказе, список id товаров"""
        all_products = await self.select_all_product_order()
        return arr.array('i', (product.product_id for product in all_products))

    async def select_order_quantity(self, product_id: int) -> int:
        """
        Возвращает количество товара из заказа
        в соответствии с номером товара - rownum
        """
        select_order = await self.__crud_db.select_order_quantity(
            product_id=product_id)
        return select_order.quantity





