from typing import Optional
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import KEYBOARD
from database import DBManager


class Keyboards:
    """
    Класс Keyboards предназначен для создания и разметки интерфейса бота
    """

    def __init__(self):
        self.markup: Optional[InlineKeyboardMarkup] = None
        self.DB = DBManager()

    def set_inline_btn(self, name: str, callback: str, step: int = 0, quantity: int = 0) -> InlineKeyboardButton:
        """
        Создает и возвращает кнопку по входным параметрам
        """
        _ = KEYBOARD.update({name: name}) if name not in KEYBOARD.keys()\
            else KEYBOARD.get(f'{name}')

        return InlineKeyboardButton(text=KEYBOARD.get(f'{name}'), callback_data=callback)

    # ********** Client keyboard **********

    def start_menu(self) -> InlineKeyboardMarkup:
        """Создает разметку кнопок в основном меню и возвращает разметку"""

        self.markup = InlineKeyboardMarkup()
        itm_btn_1 = self.set_inline_btn('CHOOSE_GOODS', callback='choose_goods')
        itm_btn_2 = self.set_inline_btn('INFO', callback='info')
        itm_btn_3 = self.set_inline_btn('SETTINGS', callback='settings')
        itm_btn_4 = self.set_inline_btn('HELP', callback='help')

        self.markup.row(itm_btn_1)
        self.markup.row(itm_btn_2, itm_btn_3).row(itm_btn_4)

        return self.markup

    def info_menu(self) -> InlineKeyboardMarkup:
        """Создает разметку кнопок в меню 'О магазине'"""

        self.markup = InlineKeyboardMarkup()
        itm_btn_1 = self.set_inline_btn('<<', callback='back')
        return self.markup.row(itm_btn_1)

    def settings_menu(self) -> InlineKeyboardMarkup:
        """Создает разметку кнопок в меню 'Настройки'"""

        self.markup = InlineKeyboardMarkup()
        itm_btn_1 = self.set_inline_btn('<<', callback='back')
        return self.markup.row(itm_btn_1)

    def category_menu(self, *categories, role: str = None, action: str = None) -> InlineKeyboardMarkup:
        """Создает разметку кнопок в меню категорий товара и возвращает разметку"""

        self.markup = InlineKeyboardMarkup()
        callback = 'back_to_admin' if action is None else 'cancel_add_product'

        for category in categories:
            self.markup.add(self.set_inline_btn(category.name,
                                                callback=f'only_cat_{category.name}_{category.id}'))

        if role is None:
            self.markup.row(self.set_inline_btn('<<', callback='back'),
                            self.set_inline_btn('ORDER', callback='order'))
        else:
            self.markup.row(self.set_inline_btn('<<', callback=callback))

        return self.markup

    def back_main_menu(self) -> InlineKeyboardMarkup:
        """Создает кнопку для возврата в главное меню"""

        self.markup = InlineKeyboardMarkup()
        itm_btn_1 = self.set_inline_btn('<<', callback='main_menu')
        self.markup.row(itm_btn_1)

        return self.markup

    # ********** Admin keyboard **********
    def start_admin_menu(self) -> InlineKeyboardMarkup:
        """Создает разметку кнопок для админа"""

        self.markup = InlineKeyboardMarkup()
        self.markup.add(
            self.set_inline_btn('ADD_CATEGORY', callback='add_category'),
            self.set_inline_btn('LIST_CATEGORY', callback='list_category'),
        )
        self.markup.row(
            self.set_inline_btn('ADD_PRODUCT', callback='add_product'),
            self.set_inline_btn('LIST_PRODUCT', callback='list_product'),
        )
        self.markup.row(self.set_inline_btn('<<', callback='back'))

        return self.markup

    def view_only_category_menu(self, category_id: int) -> InlineKeyboardMarkup:
        """Создает разметки кнопок для подменю категории"""

        self.markup = InlineKeyboardMarkup()
        self.markup.add(
            self.set_inline_btn('DELETE_CATEGORY', callback=f'delete_category_{category_id}'),
        )
        self.markup.row(self.set_inline_btn('<<', callback='back_to_category_list'))

        return self.markup

    def preview_product(self) -> InlineKeyboardMarkup:
        """Создает разметки кнопок для сохранения/отмены в бд продукта"""

        self.markup = InlineKeyboardMarkup()
        self.markup.add(
            self.set_inline_btn('SAVE_PRODUCT', callback='save_product'),
            self.set_inline_btn('CANCEL', callback='repeal_save_product'),
        )
        return self.markup

    def cancel_inline_btn(self, action: str = None) -> InlineKeyboardMarkup:
        """Создает разметку кнопки для отмены"""

        self.markup = InlineKeyboardMarkup()
        self.markup.add(self.set_inline_btn('CANCEL', callback=f'cancel_{action}'))

        return self.markup




