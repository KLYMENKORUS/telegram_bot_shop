import logging

from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery
from contextlib import suppress
from handlers import Handler
from config import MESSAGES, KEYBOARD


class HandlerAllCallback(Handler):
    """Класс обрабатывает входящие callback"""
    def __init__(self, bot: Bot, dp: Dispatcher):
        super().__init__(bot, dp)
        self.step = 0  # шаг в заказе
        self.__PRODUCT_ID = None

    async def pressed_btn_info(self, callback: CallbackQuery) -> None:
        """
        обрабатывает входящие callback
        от нажатия на кнопоку 'О магазине'
        """
        await callback.message.edit_text(
            MESSAGES.get('trading_store'),
            reply_markup=self.keyboards.info_menu()
        )
        await callback.answer()

    async def pressed_btn_settings(self, callback: CallbackQuery) -> None:
        """
        обрабатывает входящие callback
        от нажатия на кнопоку 'Настройки'
        """
        await callback.message.edit_text(
            MESSAGES.get('settings'),
            reply_markup=self.keyboards.settings_menu()
        )
        await callback.answer()

    async def pressed_btn_back(self, callback: CallbackQuery) -> None:
        """
        обрабатывает входящие callback
        от нажатия на кнопоку 'Назад'
        """
        await callback.message.edit_text(
            MESSAGES.get('start').format(callback.from_user.first_name),
            reply_markup=self.keyboards.start_menu()
        )
        await callback.answer('Вы вернулись назад')

    async def all_category(self, callback: CallbackQuery) -> None:
        """
        Обработка события нажатия на кнопку 'Выбрать товар'. А точне
        это выбор категории товаров
        """
        categories = await self.BD.all_categories()

        await callback.message.edit_text(
            MESSAGES.get('choices_category').format(callback.from_user.first_name),
            reply_markup=self.keyboards.category_menu(*categories)
        )
        await callback.answer()

    async def view_all_product(self, callback: CallbackQuery) -> None:
        """
        Обработка события нажатия на кнопку 'Выбрать товар'. А точнее
        это выбор товара из категории
        """
        category_id = int(callback.data.split('_')[-1])
        all_products = await self.BD.all_products(category_id)

        await callback.message.edit_text(
            'Категория ' + KEYBOARD.get(f'{callback.data.split("_")[2]}'),
            reply_markup=self.keyboards.view_all_products(*all_products, role='client')
        )
        await callback.answer()

    # ********** ORDERS **********
    async def pressed_btn_order(self, callback: CallbackQuery) -> None:
        """Обрабатывает входящие нажатия на кнопку 'Заказ'"""

        self.step = 0

        with suppress(IndexError):
            count = await self.BD.select_all_product_id()
            quantity = await self.BD.select_order_quantity(count[self.step])

        if await self.BD.count_rows_order():
            await self.send_callback_order(callback, count[self.step], quantity)
        else:
            await callback.answer(
                MESSAGES.get('no_orders').
                format(callback.from_user.first_name),
                show_alert=True
            )

    async def send_callback_order(
            self, callback: CallbackQuery, product_id: int, quantity: int
    ) -> None:
        """Отправляет в ответ пользователю еготекущий заказ"""
        current_order_product = await self.BD.get_product(product_id)

        await callback.message.edit_text(
            MESSAGES.get('order').format(
                self.step + 1,
                current_order_product.name,
                current_order_product.title,
                current_order_product.price,
                quantity
            ),
            reply_markup=self.keyboards.orders_menu(self.step, quantity)
        )

    async def pressed_btn_up(self, callback: CallbackQuery) -> None:
        """
        Обработка нажатия кнопки увеличения
        количества определенного товара в заказе
        """

        count = await self.BD.select_all_product_id()
        quantity_order = await self.BD.select_order_quantity(count[self.step])

        product = await self.BD.get_product(count[self.step])
        quantity_product = product.quantity

        if quantity_product > 0:
            quantity_order += 1; quantity_product -= 1

            await self.BD.update_order_value(count[self.step])
            await self.BD.update_product_value(count[self.step])

        await self.send_callback_order(callback, count[self.step], quantity_order)

    def register_handler(self):
        # *********** Главное меню **********
        self.dp.register_callback_query_handler(
            self.pressed_btn_info, lambda c: c.data == 'info'
        )
        self.dp.register_callback_query_handler(
            self.pressed_btn_settings, lambda c: c.data == 'settings'
        )
        self.dp.register_callback_query_handler(
            self.pressed_btn_back, lambda c: c.data == 'back'
        )
        self.dp.register_callback_query_handler(
            self.all_category, lambda c: c.data == 'choose_goods'
        )

        # ********** меню категории товара **********

        self.dp.register_callback_query_handler(
            self.view_all_product,
            lambda c: c.data.startswith('select_cat')
        )
        self.dp.register_callback_query_handler(self.pressed_btn_order, lambda c: c.data == 'order')
        self.dp.register_callback_query_handler(self.pressed_btn_up, lambda c: c.data == 'up')