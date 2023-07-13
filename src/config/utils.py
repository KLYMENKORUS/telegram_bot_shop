import abc


class Total(metaclass=abc.ABCMeta):

    def __init__(self, DB):
        self.DB = DB

    @abc.abstractmethod
    async def total_coast(self, list_quantity: list, list_price: list):
        ...

    @abc.abstractmethod
    async def total_quantity(self, list_quantity: list):
        ...


class Utils(Total):

    def __init__(self, DB):
        super().__init__(DB)

    async def total_coast(self, list_quantity: list, list_price: list) -> int:
        """Считает общую сумму заказа и возвращает результат"""

        result = sum(list_quantity[index] * list_price[index]
                     for index, _ in enumerate(list_price))
        return result

    async def total_quantity(self, list_quantity: list) -> int:
        """Считает общее количество заказанной единицы товара и возвращает результат"""

        quantity_finish = sum(item for item in list_quantity)

        return quantity_finish

    async def get_total_coast(self) -> int:
        """Возвращает общую стоимость товара"""

        all_product_id = await self.DB.select_all_product_id()
        all_product = [await self.DB.get_product(product) for product in all_product_id]
        all_product_price = [product.price for product in all_product]

        all_quantity = [
            await self.DB.select_order_quantity(product) for product in all_product_id
        ]

        return await self.total_coast(all_quantity, all_product_price)

    async def get_total_quantity(self) -> int:
        """Возвращает общее количество заказанной единицы товара"""

        all_product_id = await self.DB.select_all_product_id()
        all_quantity = [
            await self.DB.select_order_quantity(product) for product in all_product_id
        ]
        return await self.total_quantity(all_quantity)

