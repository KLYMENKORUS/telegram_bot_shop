from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery
from handlers import Handler
from config import MESSAGES, KEYBOARD


class HandlerAllCallback(Handler):
    """Класс обрабатывает входящие callback"""
    def __init__(self, bot: Bot, dp: Dispatcher):
        super().__init__(bot, dp)
        self.step = 0  # шаг в заказе

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