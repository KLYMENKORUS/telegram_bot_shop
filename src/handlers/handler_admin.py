import logging
from functools import wraps
from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher.filters.state import StatesGroup, State
from sqlalchemy.exc import IntegrityError

from handlers import Handler
from config import MESSAGES, IS_ADMIN_ID


# ********** FSM Aiogram **********
class AddCategory(StatesGroup):
    category_name = State()


class AddProduct(StatesGroup):
    category_id = State()
    name = State()
    title = State()
    price = State()
    quantity = State()


# ********** DECORATORS **********
def is_admin(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if str(args[1].from_user.id) == IS_ADMIN_ID:
            return await func(*args, **kwargs)
        else:
            await args[1].answer(MESSAGES.get('not_admin'))
            await args[1].answer(MESSAGES.get('start').format(args[1].from_user.first_name),
                                 reply_markup=args[0].keyboards.start_menu())
    return wrapper


class HandlerAdmin(Handler):
    """Класс обрабатывает входящие callback админа"""
    def __init__(self, bot: Bot, dp: Dispatcher):
        super().__init__(bot, dp)
        self.__data_product = {}

    # ********* OTHER FUNCTIONS *********

    async def __cancel_answer(self, callback: CallbackQuery | Message, message: str, action: str):
        """Метод для отправки ответа при отмене операции добавления"""

        if isinstance(callback, CallbackQuery):
            await callback.message.edit_text(
                message.format(callback.from_user.first_name),
                reply_markup=self.keyboards.cancel_inline_btn(action=action)
            )
        else:
            await callback.answer(
                message.format(callback.from_user.first_name),
                reply_markup=self.keyboards.cancel_inline_btn(action=action)
            )

    @is_admin
    async def pressed_start_admin(self, message: Message | CallbackQuery) -> None:
        """Старт команды для админа"""

        if isinstance(message, Message):
            await message.answer(
                MESSAGES.get('start_admin').format(message.from_user.first_name),
                reply_markup=self.keyboards.start_admin_menu()
            )
            await message.delete()
        else:
            await message.message.edit_text(
                MESSAGES.get('start_admin').format(message.from_user.first_name),
                reply_markup=self.keyboards.start_admin_menu()
            )
            await message.answer()

    async def cancel_all_operation(self, callback: CallbackQuery,
                                   state: FSMContext) -> None:
        """Отмена всех операций"""

        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()

        if callback.data.split('_', maxsplit=1)[1] == 'add_category':
            await callback.answer('Добавление категории отменено')
            await self.pressed_start_admin(callback)

        elif callback.data.split('_', maxsplit=1)[1] == 'add_product':
            await callback.answer('Добавление товара отменено')
            await self.pressed_start_admin(callback)

    async def pressed_back_btn(self, callback: CallbackQuery) -> None:
        """Реализует возврат"""

        if callback.data == 'back_to_admin':
            await self.pressed_start_admin(callback)
        elif callback.data == 'back_to_category_list':
            await self.view_all_categories(callback)

        await callback.answer()

    # ********** START ADD CATEGORY ****************
    async def start_add_new_category(self, callback: CallbackQuery) -> None:
        """Старт команды для добавления новой категории"""

        await AddCategory.category_name.set()
        await self.__cancel_answer(
            callback, MESSAGES.get('add_category'), 'add_category')

        await callback.answer()

    async def add_category(self, message: Message, state: FSMContext) -> None:
        """Добавление новой категории в бд"""

        async with state.proxy() as data:
            data.setdefault('category_name', message.text)

        try:
            await self.BD.add_category(name=data.get('category_name'))

            await message.answer(
                MESSAGES.get('add_category_success').format(message.from_user.first_name,
                                                            data.get('category_name')),
                reply_markup=self.keyboards.start_admin_menu()
            )
        except IntegrityError as e:
            logging.error(f'failed to add category: {e}')
            await message.answer(
                MESSAGES.get('add_category_failed').format(message.from_user.first_name,
                                                           data.get('category_name')),
                reply_markup=self.keyboards.start_admin_menu()
            )

        await state.finish()

    # ********** END ADD CATEGORY ****************

    # ********** START View All CATEGORY **********

    async def view_all_categories(self, callback: CallbackQuery) -> None:
        """Просмотр всех категорий"""

        categories = await self.BD.all_categories()

        if categories:
            await callback.message.edit_text(
                MESSAGES.get('choices_category').format(callback.from_user.first_name),
                reply_markup=self.keyboards.category_menu(*categories, role='admin')
            )
        else:
            await callback.message.edit_text(
                MESSAGES.get('no_categories').format(callback.from_user.first_name),
                reply_markup=self.keyboards.start_admin_menu()
            )
        await callback.answer()

    async def view_only_category(self, callback: CallbackQuery) -> None:
        """Просмотр информации о категории а также ряд действий над ней"""

        category_id = int(callback.data.split('_')[-1])
        count_products = await self.BD.get_count_products()
        category = await self.BD.get_category(category_id)

        await callback.message.edit_text(
            MESSAGES.get('view_category').format(
                category_name=category.name,
                category_id=category.id,
                category_is_active=category.is_active,
                category_count=count_products
            ),
            reply_markup=self.keyboards.view_only_category_menu(category_id)
        )
        await callback.answer()

    # ********** END View All CATEGORY **********

    # ********** DELETE CATEGORY **********

    async def delete_category(self, callback: CallbackQuery) -> None:
        """Удаление категории"""

        category_id = int(callback.data.split('_')[-1])

        try:
            await self.BD.delete_category(category_id)
            await callback.answer(MESSAGES.get('delete_category'))
            await self.view_all_categories(callback)

        except IntegrityError as e:
            logging.error(f'Error deleted category {e}')
            await callback.answer(MESSAGES.get('delete_category_failed'))
            await self.view_all_categories(callback)

    # ********** END DELETE CATEGORY **********

    # ********** START ADD NEW PRODUCT **********
    async def start_add_product(self, callback: CallbackQuery) -> None:
        """Старт для добавления нового товара"""
        await AddProduct.category_id.set()
        categories = await self.BD.all_categories()

        await callback.message.edit_text(
            MESSAGES.get('select_category').format(callback.from_user.first_name),
            reply_markup=self.keyboards.category_menu(*categories, role='admin', action='cancel')
        )
        await callback.answer()

    async def write_product_category_id(self, callback: CallbackQuery,
                                        state: FSMContext) -> None:
        """Запись выбранной категории"""

        category_id = int(callback.data.split('_')[-1])

        async with state.proxy() as data:
            data.setdefault('category_id', category_id)

        await self.__cancel_answer(
            callback, MESSAGES.get('write_name'), 'add_product')

        await AddProduct.next()

    async def write_product_name(self, message: Message, state: FSMContext) -> None:
        """Запись полного названия товара"""

        async with state.proxy() as data:
            data.setdefault('name', message.text)

        await self.__cancel_answer(
            message, MESSAGES.get('write_title'), 'add_product')

        await AddProduct.next()

    async def write_product_title(self, message: Message, state: FSMContext) -> None:
        """Запись сокрашенного названия товара"""

        async with state.proxy() as data:
            data.setdefault('title', message.text)

        await self.__cancel_answer(
            message, MESSAGES.get('write_price'), 'add_product'
        )

        await AddProduct.next()

    async def write_price(self, message: Message, state: FSMContext) -> None:
        """Запись цены товара"""

        async with state.proxy() as data:
            data.setdefault('price', message.text)

        await self.__cancel_answer(
            message, MESSAGES.get('write_quantity'), 'add_product'
        )

        await AddProduct.next()

    async def write_quantity(self, message: Message, state: FSMContext) -> None:
        """Запись количества товара"""

        async with state.proxy() as data:
            data.setdefault('quantity', message.text)

        category = await self.BD.get_category(int(data.get('category_id')))

        await message.answer(
            MESSAGES.get('preview_product').format(
                title=data['title'],
                category_name=category.name,
                name=data['name'],
                price=float(data['price']),
                quantity=data['quantity']
            ),
            reply_markup=self.keyboards.preview_product()
        )

        self.__data_product.update(title=data.get('title'), category_id=int(data.get('category_id')),
                                   name=data.get('name'), price=float(data.get('price')),
                                   quantity=int(data.get('quantity')))

        await state.finish()

    async def save_or_cancel_product(self, callback: CallbackQuery) -> None:
        """Сохранение либо отмена добавления товара в бд"""

        if callback.data == 'repeal_save_product':
            await callback.answer('Добавление товара отменено')
            await self.pressed_start_admin(callback)
        else:
            try:
                await self.BD.add_product(**self.__data_product)
                await callback.answer('Товар успешно добавлен в бд')
                await self.pressed_start_admin(callback)
            except IntegrityError as e:
                logging.error(f'Error saving product: {e}')
                await callback.message.edit_text(
                    MESSAGES.get('failed_to_save_product').format(
                        callback.from_user.first_name
                    ),
                    reply_markup=self.keyboards.start_admin_menu()
                )

    # ********** END ADD NEW PRODUCT **********

    # ********** VIEW PRODUCT **********

    async def view_all_products(self):
        # сделать пагинацию категорий и товаров
        # сделать команду на просмотр всех товаров через категорию и
        # просмотр одного товара
        ...

    def register_handler(self):

        # ********** OTHER FUNCTIONS **********

        self.dp.register_message_handler(self.pressed_start_admin, commands=['admin'])
        self.dp.register_callback_query_handler(self.cancel_all_operation,
                                                lambda c: c.data.startswith('cancel'),
                                                state='*')
        self.dp.register_callback_query_handler(self.pressed_back_btn,
                                                lambda c: c.data.startswith('back'))

        # ********** OPERATIONS WITH CATEGORIES **********

        self.dp.register_callback_query_handler(self.start_add_new_category,
                                                lambda c: c.data == 'add_category',
                                                state=None)
        self.dp.register_message_handler(self.add_category, state=AddCategory.category_name)

        self.dp.register_callback_query_handler(self.view_all_categories,
                                                lambda c: c.data == 'list_category')
        self.dp.register_callback_query_handler(self.view_only_category,
                                                lambda c: c.data.startswith('only_cat'))
        self.dp.register_callback_query_handler(self.delete_category,
                                                lambda c: c.data.startswith('delete_category'))

        # ********** OPERATIONS WITH PRODUCTS **********

        self.dp.register_callback_query_handler(self.start_add_product,
                                                lambda c: c.data == 'add_product',
                                                state=None)
        self.dp.register_callback_query_handler(self.write_product_category_id,
                                                state=AddProduct.category_id)
        self.dp.register_message_handler(self.write_product_name,
                                         state=AddProduct.name)
        self.dp.register_message_handler(self.write_product_title,
                                         state=AddProduct.title)
        self.dp.register_message_handler(self.write_price,
                                         state=AddProduct.price)
        self.dp.register_message_handler(self.write_quantity,
                                         state=AddProduct.quantity)
        self.dp.register_callback_query_handler(
            self.save_or_cancel_product,
            lambda c: c.data.startswith('repeal_save') | c.data.startswith('save'))
