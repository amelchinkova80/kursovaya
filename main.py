# < Зависимости >

import random

import telebot
from telebot.types import KeyboardButton

from config import *
from database import Database

# < Константы >

bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')
db = Database(DB_PATH)

interests = db.get_all_categories()
interests_dict = {name.lower(): id for id, name in interests}

start_commands = ['/start', 'привет', 'кто ты?', 'кто ты', 'старт']

select_interests_commands = [
    '/add', 'выбрать категории', 'выбрать категории ⚙️', 'категории']

help_commands = ['/help', 'помощь 💊', 'помоги мне',
                 'помоги', 'как с тобой работать', 'что мне делать']

get_info_commands = ['/info', 'узнать интересную информацию 👀',
                     'интересная информация', 'интересные факты', 'информация',
                     'факты', 'получить факты']

reset_commands = ['/reset', 'сбросить категории', 'сбросить']

admins_commands = ['Посмотреть список информации', 'Посмотреть категории',
          §         'Показать описание информации',
                   'Добавить информацию', 'Добавить категорию',
                   'Удалить информацию', 'Удалить категорию',
                   'Добавить категорию у информации',
                   'Сбросить категории у информации', 'Назад']


# < Callback - Функции бота >


@bot.message_handler(commands=['start'])
def start_bot(message):
    log.info(f'Start chatting with ({message.from_user.username})')

    if not db.is_user_in_db(message.from_user.username):
        keyboard = get_main_keyboard()
        bot.send_message(message.chat.id,
                         f'*Здравствуйте, {message.from_user.username}!* 🙃  '
                         f'\n\nЯ смотрю, Вы здесь первый раз.\n '>>
                         f'Давайте я Вам все расскажу! \n\nЯ - бот, который '
                         f'помогает найти интересную информацию для Вас на '
                         f'основе ваших категорий. \n\nДля начала мне нужно '
                         f'узнать категории. Нажимайте кнопочки под чатом, '
                         f'чтобы выбрать интересующую Вас категорию. \nПосле '
                         f'выбора всех интересующих Вас категорий нажмите '
                         f'кнопку "Закончить выбор", чтобы я начал вам '
                         f'выдавать интересную информацию. \n\nТакже '
                         f'перечисляю ниже свои команды: \n1. /info - Выдать '
                         f'интересную информацию \n2. /add - Добавить '
                         f'интересы\n3. /help - Помощь\n4. /reset - '
                         f'Перевыбрать интересы\n 5. /admin - '
                         f'Администрирование',
                         reply_markup=keyboard)

        db.add_user(message.from_user.username)
    else:
        send_main_message(message)


@bot.message_handler(commands=['help'])
def get_help_bot(message):
    log.info(f'Send help to ({message.from_user.username})')

    bot.send_message(message.chat.id,
                     'Я - бот, который помогает найти интересную информацию '
                     'для Вас на основе ваших категорий.\nЯ обладаю '
                     'следующими командами:\n1. /start - Начать диалог\n2. '
                     '/help - Помощь по боту\n3. /info - Выдать интересную '
                     'информацию\n4. /reset - Перевыбрать интересы \n5. '
                     '/admin – Администрирование')


@bot.message_handler(commands=['reset'])
def reset_categories_bot(message):
    log.info(f'Reset categories of ({message.from_user.username})')

    db.remove_all_categories(message.from_user.username)
    db.remove_user_info_provided(message.from_user.username)

    bot.send_message(message.chat.id, 'Ваши категории успешно сброшены!')


@bot.message_handler(commands=['add'])
def select_categories_bot(message):
    categories = db.get_no_user_categories(message.from_user.username)
    if len(categories) > 0:
        keyboard = get_keybord_with_categories(categories)
        bot.send_message(
            message.chat.id,
            'Выберите соответствущие категории, которые Вам подходят, нажимая '
            'на кнопки.',
            reply_markup=keyboard)
    else:
        send_all_categories_added(message)


@bot.message_handler(commands=['admin'])
def show_admin_panel(message):
    keyboard = get_admin_keyboard()
    bot.send_message(
        message.chat.id,
        'Для администрирования выберите одну из функций с помощью кнопок.',
        reply_markup=keyboard)


@bot.message_handler(commands=['info'])
def get_info_bot(message):
    log.info(f'Send some info to ({message.from_user.username})')

    info = get_list_info(message.from_user.username)
    no_shown = [i for i in info if not i[2]]

    if len(no_shown):
        info_id = no_shown[0][0]
    else:
        info_id = info[random.randint(0, len(info) - 1)][0]

    info = db.get_info(info_id)

    bot.send_message(
        message.chat.id, f'{info[0]}\n\n{info[1]}')

    db.insert_provided_info(message.from_user.username, info_id)


# < Дополнительные функции для упрощения работы с ботом >


def show_categories_admin(message):
    categories = db.get_all_categories()
    msg = 'Список категорий (индентификаторы и названия): \n\n'
    for idx, teg in enumerate(categories):
        msg += f'{idx+1}. {teg[1]}\n'
    bot.send_message(message.chat.id, msg)


def show_info_admin(message):
    info = db.get_all_info()
    msg = 'Список информации (индентификаторы, названия и теги): \n\n'
    for doc in info:
        tegs = ', '.join(doc[2])
        msg += f'{doc[0]}. {doc[1]} '
        if len(tegs) > 0:
            msg += f'({tegs}) \n'
        else:
            msg += '\n'
    bot.send_message(message.chat.id, msg)


def show_desc_of_info_admin(message):
    bot.send_message(
        message.chat.id,
        'Напишите идентификатор информации, о котором хотите получить '
        'описание. \nДля отмены действия напишите команду /break')
    bot.send_message(
        message.chat.id,
        'Введите название информации, а затем с новой строки его описание.')
    bot.register_next_step_handler_by_chat_id(
        message.chat.id, c_show_desc_of_info_admin)


def c_show_desc_of_info_admin(message):
    if message.text not in ['/break', 'Назад']:
        if message.text.isdigit():
            desc = db.get_info_for_admin(int(message.text))[1]
            bot.send_message(message.chat.id, f'{desc}')
        else:
            bot.send_message(message.chat.id, 'Некорректный ввод данных!')
    else:
        bot.send_message(message.chat.id, 'Действие успешно отменено!')


def add_info_admin(message):
    bot.send_message(message.chat.id,
                     'Давайте добавим новую информацию! \nОбратите внимание, '
                     'если название совпадет с названием уже существующей '
                     'информации, то таким образом вы лишь обновите '
                     'существующую информацию \nДля отмены действия напишите '
                     'команду /break')
    bot.send_message(
        message.chat.id,
        'Введите название информации, а затем с новой строки ее описание.')
    bot.register_next_step_handler_by_chat_id(
        message.chat.id, c_add_info_admin)


def c_add_info_admin(message):
    if message.text not in ['/break', 'Назад']:
        try:
            title, desc = message.text.split('\n', maxsplit=1)
            db.add_info(title, desc)
            bot.send_message(message.chat.id, 'Информация успешно добавлена!')
        except Exception as e:
            bot.send_message(message.chat.id, 'Некорректный ввод данных!')
    else:
        bot.send_message(message.chat.id, 'Действие успешно отменено!')


def add_category_user(message):
    is_added = db.add_user_category(
        message.from_user.username, interests_dict.get(message.text.lower()))
    if is_added:
        send_added_category_message(message)
    else:
        send_no_added_category_message(message.chat.id)


def add_category_admin(message):
    bot.send_message(
        message.chat.id,
        'Давайте добавим новую категорию! \nДля отмены действия напишите '
        'команду /break')
    bot.send_message(
        message.chat.id, 'Введите название категории.')
    bot.register_next_step_handler_by_chat_id(
        message.chat.id, c_add_category_admin)


def c_add_category_admin(message):
    if message.text not in ['/break', 'Назад']:
        db.add_category(message.text)
        bot.send_message(
            message.chat.id, 'Категория успешно добавлена!')
    else:
        bot.send_message(message.chat.id, 'Действие успешно отменено!')


def remove_info_admin(message):
    bot.send_message(
        message.chat.id,
        'Введите уникальный идентификатор информации. \nДля отмены действия '
        'напишите команду /break')
    bot.register_next_step_handler_by_chat_id(
        message.chat.id, c_remove_info_admin)


def c_remove_info_admin(message):
    if message.text not in ['/break', 'Назад']:
        if message.text.isdigit():
            db.remove_info(int(message.text))
            bot.send_message(message.chat.id, 'Информация успешно удалена!')
        else:
            bot.send_message(message.chat.id, 'Некорректный ввод данных!')
    else:
        bot.send_message(message.chat.id, 'Действие успешно отменено!')


def remove_category_admin(message):
    bot.send_message(
        message.chat.id,
        'Введите уникальный идентификатор категории. \nДля отмены действия '
        'напишите команду /break')
    bot.register_next_step_handler_by_chat_id(
        message.chat.id, c_remove_category_admin)


def c_remove_category_admin(message):
    if message.text not in ['/break', 'Назад']:
        if message.text.isdigit():
            remove_category_id = int(message.text) - 1
            categories = db.get_all_categories()
            if 0 <= remove_category_id < len(categories):
                db_category_id = categories[remove_category_id][0]
                db.remove_category(db_category_id)
                bot.send_message(
                    message.chat.id, 'Категория успешно удалена!')
            else:
                bot.send_message(message.chat.id, 'Произошла ошибка!')
        else:
            bot.send_message(message.chat.id, 'Произошла ошибка!')
    else:
        bot.send_message(message.chat.id, 'Действие успешно отменено!')


def add_categories_to_info_admin(message):
    bot.send_message(
        message.chat.id,
        'Введите через пробел идентификатор информации и идентификатор '
        'категории, которую хотите присвоить факту. \nДля отмены действия '
        'напишите команду /break')
    bot.register_next_step_handler_by_chat_id(
        message.chat.id, c_add_categories_to_info_admin)


def c_add_categories_to_info_admin(message):
    if message.text not in ['/break', 'Назад']:
        try:
            info_id, category_id = message.text.split(' ', 1)
            db.add_category_to_info(info_id, category_id)
            bot.send_message(
                message.chat.id, 'Категория у информации успешно удалена!')
        except Exception as e:
            bot.send_message(message.chat.id, 'Произошла ошибка!')
    else:
        bot.send_message(message.chat.id, 'Действие успешно отменено!')


def reset_categories_of_info_admin(message):
    bot.send_message(
        message.chat.id,
        'Введите идентификатор информации, у которого Вы хотите сбросить '
        'категории. \nДля отмены действия напишите команду /break')
    bot.register_next_step_handler_by_chat_id(
        message.chat.id, c_reset_categories_of_info_admin)


def c_reset_categories_of_info_admin(message):
    if message.text not in ['/break', 'Назад']:
        if message.text.isdigit():
            db.reset_categories_of_info(int(message.text))
            bot.send_message(
                message.chat.id, 'Категория интереса у факта успешно удалена!')
        else:
            bot.send_message(message.chat.id, 'Произошла ошибка!')
    else:
        bot.send_message(message.chat.id, 'Действие успешно отменено!')


def send_main_message(message):
    keyboard = get_main_keyboard()
    bot.send_message(
        message.chat.id,
        'Для того, чтобы начать работать, выберите одну из функций с помощью '
        'кнопок.',
        reply_markup=keyboard)


def send_no_added_category_message(message):
    bot.send_message(message.chat.id, f'Вы уже добавили данную категорию!')


def send_added_category_message(message):
    keyboard = get_keybord_with_categories(
        db.get_no_user_categories(message.from_user.username))
    bot.send_message(
        message.chat.id,
        f'Вы успешно выбрали новую категорию – {message.text}!\nВы можете '
        f'продолжить выбор категорий, либо перейти в главное меню нажатием '
        f'кнопки "Назад".',
        reply_markup=keyboard)


def send_all_categories_added(message):
    bot.send_message(
        message.chat.id,
        'Вы выбрали все доступные категории!\nСбросьте свой список интересов '
        '(/reset), чтобы выбрать их заново.')


def send_error(message):
    bot.send_message(message.chat.id,
                     'Я не знаю такую команду! 🙁\nВоспользуйтесь командой '
                     '/help для того, чтобы узнать мои команды.\n')


def get_main_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    main_list = ['Выбрать категории ⚙️', 'Сбросить категории',
                 'Помощь 💊', 'Узнать интересную информацию 👀',
                 'Администрирование']
    btns = [KeyboardButton(name) for name in main_list]
    keyboard.add(*btns)
    return keyboard


def get_keybord_with_categories(categories):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    btns = [KeyboardButton(item[1]) for item in categories]
    btns.append(get_back_button())
    keyboard.add(*btns)
    return keyboard


def get_admin_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(True, row_width=2)
    _btns = [KeyboardButton(command) for command in admins_commands]
    keyboard.add(*_btns)
    return keyboard


def get_back_button():
    return KeyboardButton('Назад')


def get_list_info(username):
    unprovided = db.get_unprovided_info(username)
    provided = db.get_provided_info(username)

    result = []

    for id in unprovided:
        result.append((id, db.get_similarity_categories(username, id), False))

    for id in provided:
        result.append((id, db.get_similarity_categories(username, id), True))

    result.sort(key=lambda x: x[1], reverse=True)
    return result


# < Массив: [команды], функция >


admin_triggers = [
    ('Посмотреть список информации', show_info_admin),
    ('Посмотреть категории', show_categories_admin),
    ('Показать описание информации', show_desc_of_info_admin),
    ('Добавить информацию', add_info_admin),
    ('Добавить категорию', add_category_admin),
    ('Удалить информацию', remove_info_admin),
    ('Удалить категорию', remove_category_admin),
    ('Добавить категории у информации', add_categories_to_info_admin),
    ('Сбросить категории у информации', reset_categories_of_info_admin),
    ('Назад', send_main_message)
]


@bot.message_handler(commands=['admin'])
def admin_panel_bot(message):
    text = message.text.lower()
    for command, func in admin_triggers:
        if text == command.lower():
            func(message)


triggers = [
    (start_commands, start_bot),
    (select_interests_commands, select_categories_bot),
    (help_commands, get_help_bot),
    (get_info_commands, get_info_bot),
    (reset_commands, reset_categories_bot),
    ([command.lower() for command in admins_commands], admin_panel_bot),
    (['назад'], send_main_message),
    (['администрирование'], show_admin_panel),
]


@bot.message_handler(content_types=['text'])
def process_triggers_bot(message):
    log.info(
        f'Got a message from ({message.from_user.username}) : ({message.text})')

    text = message.text.lower()

    for commands, func in triggers:
        if text in commands:
            func(message)
            return

    if interests_dict.get(text) is not None:
        add_category_user(message)
    else:
        send_error(message)


bot.polling()
