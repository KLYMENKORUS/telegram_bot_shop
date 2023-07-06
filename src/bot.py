import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.types import BotCommand, ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN, COMMANDS
from handlers import HandlerMain


class AioBot:
    """
    Основной класс телеграмм бота (сервер), в основе которого
    используется библиотека Aiogram
    """

    def __init__(self) -> None:
        self.token = TOKEN
        self.bot = Bot(self.token, parse_mode=ParseMode.HTML)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=self.storage)
        self.handler = HandlerMain(self.bot, self.dp)

    async def on_startup(self, _):
        logging.info('Бот в работе')
        await self.set_main_menu(self.bot)

    async def set_main_menu(self, bot: Bot):
        main_menu_commands = [BotCommand(
            command=command,
            description=description
        ) for command, description in COMMANDS.items()]
        await bot.set_my_commands(main_menu_commands)

    def start(self) -> None:
        """Метод предназначен для старта обработчика событий"""

        self.handler.handle()

    def run_bot(self):
        """Метод запускает основные события сервера"""
        self.start()

        executor.start_polling(
            dispatcher=self.dp, on_startup=self.on_startup,
            skip_updates=True
        )


if __name__ == '__main__':
    logging.basicConfig(
        level='DEBUG'.upper(),
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    bot = AioBot()
    bot.run_bot()




