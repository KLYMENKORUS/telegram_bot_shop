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

    def set_inline_btn(
            self, name: str, callback: str, step: int = 0, quantity: int = 0,
            amount_orders: int = None
    ) -> InlineKeyboardButton:
        """
        Создает и возвращает кнопку по входным параметрам
        """
        _ = KEYBOARD.update({name: name}) if name not in KEYBOARD.keys()\
            else KEYBOARD.get(f'{name}')

        match name:
            case 'AMOUNT_PRODUCT':
                KEYBOARD.update({'AMOUNT_PRODUCT': f'{quantity}'})
            case 'AMOUNT_ORDERS':
                KEYBOARD.update({'AMOUNT_ORDERS': f'{step + 1} из {str(amount_orders)}'})

        return InlineKeyboardButton(
            text=KEYBOARD.get(f'{name}'), callback_data=callback
        )

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

    def back(self) -> InlineKeyboardMarkup:
        """Создает разметку кнопки для возвращения"""
        self.markup = InlineKeyboardMarkup()
        return self.markup.row(self.set_inline_btn('<<', callback='back'))

    def category_menu(self, *categories, role: str = None, action: str = None) -> InlineKeyboardMarkup:
        """Создает разметку кнопок в меню категорий товара и возвращает разметку"""

        self.markup = InlineKeyboardMarkup()
        callback = 'back_to_admin' if action is None else 'cancel_add_product'
        callback_cat = 'select_cat' if role is None else 'only_cat'

        for category in categories:
            self.markup.add(self.set_inline_btn(
                category.name,
                callback=f'{callback_cat}_{category.name}_{category.id}'))

        if role is None:
            self.markup.row(self.set_inline_btn('<<', callback='back'),
                            self.set_inline_btn('ORDER', callback='order'))
        else:
            self.markup.row(self.set_inline_btn('<<', callback=callback))

        return self.markup

    def orders_menu(self, step: int, quantity: int, amount_orders: int = None) -> InlineKeyboardMarkup:
        """
        Создает разметку кнопок в заказе товара и возвращает разметку
        """

        self.markup = InlineKeyboardMarkup()
        itm_btn_1 = self.set_inline_btn('X', 'remove', step, quantity)
        itm_btn_2 = self.set_inline_btn('DOWN', 'down', step, quantity)
        itm_btn_3 = self.set_inline_btn('AMOUNT_PRODUCT', 'amount_product', step, quantity)
        itm_btn_4 = self.set_inline_btn('UP', 'up', step, quantity)

        itm_btn_5 = self.set_inline_btn('BACK_STEP', 'back_step', step, quantity)
        itm_btn_6 = self.set_inline_btn('AMOUNT_ORDERS', 'amount_orders', step, quantity, amount_orders)
        itm_btn_7 = self.set_inline_btn('NEXT_STEP', 'next_step', step, quantity)
        itm_btn_8 = self.set_inline_btn('APPLY', 'apply', step, quantity)
        itm_btn_9 = self.set_inline_btn('<<', 'back', step, quantity)
        # рассположение кнопок в меню
        self.markup.row(itm_btn_1, itm_btn_2, itm_btn_3, itm_btn_4)
        self.markup.row(itm_btn_5, itm_btn_6, itm_btn_7)
        self.markup.row(itm_btn_9, itm_btn_8)

        return self.markup

    def view_all_products(self, *products, role: str = None) -> InlineKeyboardMarkup:
        """Создает разметку кнопок для вывода всех товаров и возвращает её"""

        self.markup = InlineKeyboardMarkup()

        call_product = 'client_product' if role == 'client' else 'product'
        for product in products:
            if product.quantity > 0:
                self.markup.add(self.set_inline_btn(
                    product.name, callback=f'{call_product}_{product.name}_{product.id}'))

        match role:
            case 'client':
                self.markup.row(self.set_inline_btn('<<', callback='back'))
            case 'admin':
                self.markup.row(self.set_inline_btn('<<', callback='list_category'))

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

    def set_view_only_item(
            self, value_btn: str, callback_id: str,
            callback_back: str, value_btn_back: str
    ) -> InlineKeyboardMarkup:
        """Создает разметки кнопок для отображения подменю"""

        self.markup = InlineKeyboardMarkup()
        self.markup.add(
            self.set_inline_btn(value_btn, callback=callback_id)
        )
        self.markup.row(
            self.set_inline_btn(value_btn_back, callback=callback_back)
        )
        return self.markup

    def view_only_category_menu(self, category_id: int) -> InlineKeyboardMarkup:
        """Создает разметки кнопок для подменю категории"""

        return self.set_view_only_item(
            value_btn='DELETE_CATEGORY', callback_id=f'delete_category_{category_id}',
            callback_back='back_to_category_list', value_btn_back='<<'
        )

    def view_only_product(self, product_id) -> InlineKeyboardMarkup:
        """Создает разметки кнопок для подменю товара"""

        return self.set_view_only_item(
            value_btn='DELETE_PRODUCT', callback_id=f'delete_product_{product_id}',
            callback_back='back_to_product_list', value_btn_back='<<'
        )

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




