import abc
from aiogram import Bot, Dispatcher
from keyboards import Keyboards
from database import DBManager


class Handler(metaclass=abc.ABCMeta):

    def __init__(self, bot: Bot, dp: Dispatcher) -> None:
        self.bot = bot
        self.dp = dp
        self.keyboards = Keyboards()
        self.BD = DBManager()

    @abc.abstractmethod
    def register_handler(self):
        ...