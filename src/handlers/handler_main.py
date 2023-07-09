from aiogram import Bot, Dispatcher
from handlers.handler_command import HandlerCommand
from handlers.handler_all_callback import HandlerAllCallback
from handlers.handler_admin import HandlerAdmin
from handlers.handler_inline_query import HandlerInlineQuery


class HandlerMain:
    """Класс компоновщик"""

    def __init__(self, bot: Bot, dp: Dispatcher):
        self.bot = bot
        self.dp = dp
        # инициализация обработчиков
        self.handler_command = HandlerCommand(self.bot, self.dp)
        self.handler_all_callback = HandlerAllCallback(self.bot, self.dp)
        self.handler_admin = HandlerAdmin(self.bot, self.dp)
        self.handler_inline_query = HandlerInlineQuery(self.bot, self.dp)

    def handle(self):
        """Запуск обработчиков"""
        self.handler_command.register_handler()
        self.handler_all_callback.register_handler()
        self.handler_admin.register_handler()
        self.handler_inline_query.register_handler()