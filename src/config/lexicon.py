from emoji import emojize

COUNT = 0

# кнопки управления
KEYBOARD: dict[str, str] = {
    'CHOOSE_GOODS': emojize(':open_file_folder: Выбрать товар'),
    'INFO': emojize(':speech_balloon: О магазине'),
    'SETTINGS': emojize('⚙️ Настройки'),
    'SEMIPRODUCT': emojize(':pizza: Полуфабрикаты'),
    'GROCERY': emojize(':bread: Бакалея'),
    'ICE_CREAM': emojize(':shaved_ice: Мороженое'),
    '<<': emojize('⏪'),
    '>>': emojize('⏩'),
    'BACK_STEP': emojize('◀️'),
    'NEXT_STEP': emojize('▶️'),
    'ORDER': emojize('✅ ЗАКАЗ'),
    'X': emojize('❌'),
    'DOUWN': emojize('🔽'),
    'AMOUNT_PRODUCT': COUNT,
    'AMOUNT_ORDERS': COUNT,
    'UP': emojize('🔼'),
    'APPLAY': '✅ Оформить заказ',
    'COPY': '©️',
    'MAIN_MENU': 'Назад в главное меню',
    'HELP': emojize(':person_facepalming: Помощь'),
    'ADD_CATEGORY': 'Добавить категорию',
    'DELETE_CATEGORY': emojize('❌ Удалить категорию'),
    'LIST_CATEGORY': emojize('📋 Список категорий'),
    'ADD_PRODUCT': 'Добавить товар',
    'LIST_PRODUCT': emojize('📋 Список товаров'),
    'SAVE_PRODUCT': emojize('✅ Сохранить'),
    'DELETE_PRODUCT': emojize('❌ Удалить товар'),
    'CANCEL': emojize('❌ Отменить')
}


# названия команд
COMMANDS: dict[str, str] = {
    '/start': 'Перезапуск бота'
}


# ********** Ответы для клиентов ***********

start = '{}, Здравствуйте! Жду дальнейших задач.'
choices_category = '{}, Выберите категорию продуктов'

# ответ пользователю при посещении блока "О магазине"
trading_store = """

<b>Добро пожаловать в приложение
            GroceryStore !!!</b>

Данное приложение разработано 
специально для торговых представителей,
далее <i>(ТП/СВ)</i>,а также для кладовщиков, 
коммерческих организаций осуществляющих
оптово-розничную торговлю.

ТП используя приложение GroceryStore,
в удобной интуитивной форме смогут без
особого труда принять заказ от клиента.
GroceryStore поможет сформировать заказ
и в удобном виде адресует кладовщику 
фирмы для дальнейшего комплектования заказа. 

"""
# ответ пользователю при посещении блока "Настройки"
settings = """
<b>Общее руководство приложением:</b>

<i>Навигация:</i>

-<b>({}) - </b><i>назад</i>
-<b>({}) - </b><i>вперед</i>
-<b>({}) - </b><i>увеличить</i>
-<b>({}) - </b><i>уменьшить</i>
-<b>({}) - </b><i>следующий</i>
-<b>({}) - </b><i>предыдующий</i>

<i>Специальные кнопки:</i>

-<b>({}) - </b><i>удалить</i>
-<b>({}) - </b><i>заказ</i>
-<b>({}) - </b><i>Оформить заказ</i>

""".format(
    KEYBOARD['<<'],
    KEYBOARD['>>'],
    KEYBOARD['UP'],
    KEYBOARD['DOUWN'],
    KEYBOARD['NEXT_STEP'],
    KEYBOARD['BACK_STEP'],
    KEYBOARD['X'],
    KEYBOARD['ORDER'],
    KEYBOARD['APPLAY'],
    KEYBOARD['COPY'],
)

# ответ пользователю при добавлении товара в заказ
product_order = """
Выбранный товар:

{name}
{title}
Cтоимость: {price} uah

добавлен в заказ!!!

На складе осталось {quantity} ед. 
"""

# ответ пользователю при посещении блока с заказом
order = """

<i>Название:</i> <b>{}</b>

<i>Описание:</i> <b>{}</b>

<i>Cтоимость:</i> <b>{} руб за 1 ед.</b>

<i>Количество позиций:</i> <b>{} ед.</b> 
"""

order_number = """

<b>Позиция в заказе № </b> <i>{}</i>

"""

# ответ пользователю, когда заказа нет
no_orders = """
<b>Заказ отсутствует !!!</b>
"""

# ответ пользователю при подтверждении оформления заказа
applay = """
<b>Ваш заказ оформлен !!!</b>

<i>Общая стоимость заказа составляет:</i> <b>{} руб</b>

<i>Общее количнсктво пзиций составляет:</i> <b>{} ед.</b>

<b>ЗАКАЗ НАПРАВЛЕН НА СКЛАД,
ДЛЯ ЕГО КОМПЛЕКТОВКИ !!!</b>
"""

# ********** Ответы для админов ***********
start_admin = 'Привет, админ {} ожидаю дальнейших команд!'
not_admin = 'В этот раздел разрешено только админам 🤷'

# ********** Ответы в разделе категории **********
add_category = '{}, введи название новой категории!'
add_category_success = '{}, категория <b>{}</b> успешно добавлена!'
add_category_failed = '{}, категория <b>{}</b> не была добавлена, т.к. уже существует'
no_categories = '{}, категорий нет, нужно их добавить!'
view_category = """
<b>Категория: {category_name}</b>
<b>ID категории</b>: {category_id}
<b>Активность категории</b>: {category_is_active}
<b>Количество наименований</b>: {category_count}
"""
delete_category = 'Категория, успешно удалена!'
delete_category_failed = 'Ошибка удаления категории!'

# ********** Ответы в разделе продукты **********
add_product = ''
select_category = '{}, выбери категорию к которой хочешь добавить продукт!'
write_name = '{}, укажи пожалуйста полное название продукта!'
write_title = '{}, теперь введи название товара для заголовка!(т.е. сокращенное)'
write_price = '{}, теперь введи цену товара'
write_quantity = '{}, теперь введи количество товара'
preview_product = """
<b>Товар: {title}</b>
<b>Категория: {category_name}</b>
<b>Полное название</b>: {name}
<b>Цена товара</b>: {price}
<b>Количество ед. на складе</b>: {quantity}
"""
failed_to_save_product = '{}, возникла ошибка при добавлении товара 🤷'
delete_product = 'Товар, успешно удален с бд!'
delete_product_failed = 'Ошибка удаления товара!'


MESSAGES: dict[str, str] = {
    'start': start,
    'start_admin': start_admin,
    'not_admin': not_admin,
    'add_category': add_category,
    'add_category_success': add_category_success,
    'add_category_failed': add_category_failed,
    'help': '{}, Здравствуйте! Жду дальнейших задач.',
    'choices_category': choices_category,
    'no_categories': no_categories,
    'view_category': view_category,
    'delete_category': delete_category,
    'delete_category_failed': delete_category_failed,
    'select_category': select_category,
    'write_name': write_name,
    'write_title': write_title,
    'write_price': write_price,
    'write_quantity': write_quantity,
    'preview_product': preview_product,
    'failed_to_save_product': failed_to_save_product,
    'delete_product': delete_product,
    'delete_product_failed': delete_product_failed,
    'trading_store': trading_store,
    'product_order': product_order,
    'order': order,
    'order_number': order_number,
    'no_orders': no_orders,
    'applay': applay,
    'settings': settings
}
