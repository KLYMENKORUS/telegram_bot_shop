from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from handlers import Handler
from config import MESSAGES


class HandlerCommand(Handler):
    """Класс обрабатывает входящие команды /start и т.п."""

    def __init__(self, bot: Bot, dp: Dispatcher) -> None:
        super().__init__(bot, dp)

    async def pressed_btn_start(self, message: Message | CallbackQuery) -> None:
        """Oбрабатывает входящие /start команды"""

        if isinstance(message, Message):
            await message.answer(
                MESSAGES.get('start').format(message.from_user.first_name),
                reply_markup=self.keyboards.start_menu()
            )
        else:
            await message.message.edit_text(
                MESSAGES.get('start').format(message.from_user.first_name),
                reply_markup=self.keyboards.start_menu()
            )

    async def pressed_btn_help(self, callback: CallbackQuery) -> None:
        """Oбрабатывает входящие callback для help команды"""

        await callback.message.edit_text(
            MESSAGES.get('help'),
            reply_markup=self.keyboards.back_main_menu()
        )
        await callback.answer()

    async def pressed_btn_back_main_menu(self, callback: CallbackQuery) -> None:
        """Oбрабатывает входящие callback для возврата в главное меню"""
        await self.pressed_btn_start(callback)
        await callback.answer()

    def register_handler(self):
        self.dp.register_message_handler(self.pressed_btn_start, commands=['start'])
        self.dp.register_callback_query_handler(self.pressed_btn_help,
                                                lambda c: c.data == 'help')
        self.dp.register_callback_query_handler(self.pressed_btn_back_main_menu,
                                                lambda c: c.data == 'main_menu')





