from contextlib import suppress
from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import MessageNotModified
from handlers import Handler
from config import MESSAGES, KEYBOARD, Utils


class HandlerAllCallback(Handler):
    """Класс обрабатывает входящие callback"""

    def __init__(self, bot: Bot, dp: Dispatcher):
        super().__init__(bot, dp)
        self.step = 0  # шаг в заказе
        self.__AMOUNT_ORDERS = None
        self.utils = Utils(self.BD)

    async def __back_next_step(self, callback: CallbackQuery) -> None:
        with suppress(MessageNotModified):
            count = await self.BD.select_all_product_id()
            quantity_order = await self.BD.select_order_quantity(count[self.step])
            await self.send_callback_order(callback, count[self.step], quantity_order, self.__AMOUNT_ORDERS)

        await callback.answer()

    async def pressed_btn_info(self, callback: CallbackQuery) -> None:
        """
        обрабатывает входящие callback
        от нажатия на кнопоку 'О магазине'
        """
        await callback.message.edit_text(
            MESSAGES.get('trading_store'),
            reply_markup=self.keyboards.back()
        )
        await callback.answer()

    async def pressed_btn_settings(self, callback: CallbackQuery) -> None:
        """
        обрабатывает входящие callback
        от нажатия на кнопоку 'Настройки'
        """
        await callback.message.edit_text(
            MESSAGES.get('settings'),
            reply_markup=self.keyboards.back()
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

        self.__AMOUNT_ORDERS = await self.BD.count_rows_order()

        self.step = 0

        with suppress(IndexError):
            count = await self.BD.select_all_product_id()
            quantity = await self.BD.select_order_quantity(count[self.step])

        if self.__AMOUNT_ORDERS:
            await self.send_callback_order(callback, count[self.step], quantity, self.__AMOUNT_ORDERS)
        else:
            await callback.answer(
                MESSAGES.get('no_orders').
                format(callback.from_user.first_name),
                show_alert=True
            )

    async def send_callback_order(
            self, callback: CallbackQuery, product_id: int, quantity: int,
            amount_orders: int = None
    ) -> None:
        """Отправляет в ответ пользователю его текущий заказ"""
        current_order_product = await self.BD.get_product(product_id)

        await callback.message.edit_text(
            MESSAGES.get('order').format(
                self.step + 1,
                current_order_product.name,
                current_order_product.title,
                current_order_product.price,
                quantity
            ),
            reply_markup=self.keyboards.orders_menu(self.step, quantity, amount_orders)
        )

        await callback.answer()

    async def pressed_btn_up(self, callback: CallbackQuery) -> None:
        """
        Обработка нажатия кнопки увеличения
        количества определенного товара в заказе
        """

        count = await self.BD.select_all_product_id()
        quantity_order = await self.BD.select_order_quantity(count[self.step])

        quantity_product = await self.BD.select_product_quantity(count[self.step])

        if quantity_product > 0:
            quantity_order += 1; quantity_product -= 1

            await self.BD.update_order_value(count[self.step], quantity_order)
            await self.BD.update_product_value(count[self.step], quantity_product)

        await self.send_callback_order(callback, count[self.step], quantity_order, self.__AMOUNT_ORDERS)

    async def pressed_btn_down(self, callback: CallbackQuery) -> None:
        """
        Обработка нажатия кнопки увеличения
        количества определенного товара в заказе
        """

        count = await self.BD.select_all_product_id()
        quantity_order = await self.BD.select_order_quantity(count[self.step])

        quantity_product = await self.BD.select_product_quantity(count[self.step])

        with suppress(MessageNotModified):
            if quantity_product > 0 and quantity_order > 1:
                quantity_order -= 1; quantity_product += 1

                await self.BD.update_order_value(count[self.step], quantity_order)
                await self.BD.update_product_value(count[self.step], quantity_product)

            await self.send_callback_order(callback, count[self.step], quantity_order, self.__AMOUNT_ORDERS)
        await callback.answer()

    async def pressed_btn_x(self, callback: CallbackQuery) -> None:
        """Обрабатывает нажатие кнопки удаления товара в заказе"""

        count = await self.BD.select_all_product_id()

        if len(count) > 0:
            quantity_order = await self.BD.select_order_quantity(count[self.step])
            quantity_product = await self.BD.select_product_quantity(count[self.step])

            quantity_product += quantity_order
            await self.BD.delete_product_order(count[self.step])
            await self.BD.update_product_value(count[self.step], quantity_product)
            self.step -= 1

        count = await self.BD.select_all_product_id()
        if len(count) > 0:
            self.__AMOUNT_ORDERS = await self.BD.count_rows_order()
            quantity_order = await self.BD.select_order_quantity(count[self.step])
            await self.send_callback_order(callback, count[self.step], quantity_order, self.__AMOUNT_ORDERS)
        else:
            await callback.answer(
                MESSAGES.get('no_orders').
                format(callback.from_user.first_name),
                show_alert=True
            )
            await self.all_category(callback)

    async def pressed_btn_back_step(self, callback: CallbackQuery) -> None:
        """
        Обрабатывает нажатие кнопки перемещения
        на предыдущую позицию товара в заказе
        """
        if self.step > 0: self.step -= 1

        await self.__back_next_step(callback)

    async def pressed_btn_next_step(self, callback: CallbackQuery) -> None:
        """
        Обрабатывает нажатие кнопки перемещения
        на следующую позицию товара в заказе
        """
        if self.step < self.__AMOUNT_ORDERS - 1: self.step += 1

        await self.__back_next_step(callback)

    async def pressed_btn_apply(self, callback: CallbackQuery) -> None:
        """
        Oбрабатывает нажатия на кнопку 'Оформить заказ'
        """
        await callback.message.edit_text(
            MESSAGES.get('apply').format(
                await self.utils.get_total_coast(),
                await self.utils.get_total_quantity()
            ), reply_markup=self.keyboards.back()
        )
        await self.BD.delete_order_all()

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
        self.dp.register_callback_query_handler(self.pressed_btn_down, lambda c: c.data == 'down')
        self.dp.register_callback_query_handler(self.pressed_btn_x, lambda c: c.data == 'remove')
        self.dp.register_callback_query_handler(self.pressed_btn_back_step, lambda c: c.data == 'back_step')
        self.dp.register_callback_query_handler(self.pressed_btn_next_step, lambda c: c.data == 'next_step')
        self.dp.register_callback_query_handler(self.pressed_btn_apply, lambda c: c.data == 'apply')
