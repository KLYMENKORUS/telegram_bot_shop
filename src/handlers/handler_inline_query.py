import logging

from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery
from handlers import Handler
from config import MESSAGES, KEYBOARD


class HandlerInlineQuery(Handler):
    """
    Класс обрабатывает входящие текстовые
    сообщения от нажатия на инлайн-кнопоки
    """

    def __init__(self, bot: Bot, dp: Dispatcher):
        super().__init__(bot, dp)

    async def pressed_btn_product(self, callback: CallbackQuery) -> None:
        """
        Обрабатывает входящие запросы на нажатие inline-кнопок товара
        """
        product_id = int(callback.data.split('_')[-1])
        user_id = int(callback.from_user.id)
        await self.BD.add_orders(1, product_id, user_id)

        product = await self.BD.get_product(product_id)
        logging.info(f'Added product with order: {product.name}')

        await callback.answer(
            MESSAGES.get('product_order').format(
                name=product.name,
                title=product.title,
                price=product.price,
                quantity=product.quantity
            ),
            show_alert=True
        )

    def register_handler(self):
        self.dp.register_callback_query_handler(self.pressed_btn_product, lambda c: True)