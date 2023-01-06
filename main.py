import telebot
from telebot import types
import random
import settingsBot
import db
import sqlite3

#  Передача индификатора бота
bot = telebot.TeleBot(settingsBot.API)


@bot.message_handler(commands=['start'])
def start(message):
    """
    Вывод приветственного сообщения и
    подэкранных кнопок в начале использования бота.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Присваивание текста кнопок
    item1 = types.KeyboardButton("Прочитать лекции")
    item2 = types.KeyboardButton("Пройти тест")
    item3 = types.KeyboardButton("Администрирование")
    markup.add(item1, item2, item3)  # Создание маркупа
    bot.send_message(message.chat.id, settingsBot.greetings,
                     reply_markup=markup)  # Вывод кнопок на экран


@bot.message_handler(content_types=['text'])
def select(message):
    """
    Обработка кнопок "Прочитать лекции"
                     "Пройти тест"
                     "Администрирование"
    """
    if message.chat.type == 'private':

        if message.text == "Пройти тест":
            test(message, num=0, sco=0)

        if message.text == "Прочитать лекции":
            bot.send_message(message.chat.id, 'Вот все доступные лекции:',
                             # Скрытие подэкранных кнопок
                             reply_markup=telebot.types.ReplyKeyboardRemove())
            for articl in show_articl():  # Пробежка по списку
                bot.send_message(message.chat.id, articl)  # ввывод элемента

        if message.text == "Администрирование":
            send = bot.send_message(message.chat.id, 'Введите пароль')
            # Ожидание ответа пользователя
            bot.register_next_step_handler(send, admin_panel)
        if message.text == 'Пройти тест':
            bot.send_message(message.chat.id,
                             'Внимательно читайте вопросы! Удачи!')

        else:
            # Если пользователь ввел нечто другое
            # выводиться соотвествующее сообщение
            bot.send_message(message.chat.id,
                             settingsBot.explanatory_message)


def test(message, num, sco):
    """
    Пробежка по таблице, вывод вопросов с подкрепленными
    кнопками с ответами, вызов функции проверки правильности
    выбранного ответа
    """
    # Проверка личностного обращения к боту
    if message.chat.type == 'private':
        # Подсчет количества строк в таблице "quiz"
        amount = db.cur.execute("""SELECT COUNT(*) FROM quiz""")
        amount = db.cur.fetchone()
        # Ввод ограничения на цикл
        if num < settingsBot.number_of_questions:
            # Выбор из таблице "quiz" вопроса по рандомному ID
            quiz = db.cur.execute(f"""SELECT * FROM quiz WHERE ID IN
                                  ({random.randint(1, amount[0])})""")
            quiz = db.cur.fetchone()
            # Создание подэкранной клавиатуры
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            # Присваивание текста кнопок
            item1 = types.KeyboardButton(quiz[2])
            item2 = types.KeyboardButton(quiz[3])
            item3 = types.KeyboardButton(quiz[4])
            markup.add(item1, item2, item3)  # Создание маркупа
            bot.send_message(message.chat.id,
                             quiz[1],
                             reply_markup=markup)  # Вывод данных
            # Вызов функции передав информацию о последнем сообщении
            bot.register_next_step_handler(message, processing, quiz, num, sco)
        else:
            bot.send_message(message.chat.id,
                             "Тест закончен! Вы ответили на " + str(sco) +
                             " вопроса/ов правильно. Продолжайте в том "
                             " же духе Чтобы вернутся нажмите на /start")
            # Отправка стикера пользователю
            bot.send_sticker(message.chat.id,
                             "CAACAgIAAxkBAAEHJDxjt6VIJtoj79nG9VGyPgQZHBn"
                             "yoAACJxgAAvycyUvTXLcOLd5s3y0E")


def processing(message, quiz, num, sco):
    """
    Провека выбранного ответа
    """
    if message.text == quiz[5]:
        bot.send_message(message.chat.id, '✅')
        test(message, num + 1, sco + 1)
    else:
        bot.send_message(message.chat.id, '❌')
        test(message, num + 1, sco)


def show_articl():
    """
    Вывод "link" из таблицы "articles"
    """
    articles = []
    # Пробежка по всеей таблице articles
    for article in db.cur.execute("""SELECT link FROM articles"""):
        articles.append(article)  # Создание списка
    return articles  # передача значений


@bot.message_handler(content_types=['text'])
def admin_panel(message):
    """
    Вывод всех кнопок из административного окна
    """
    # Проверка личностного обращения к боту
    if message.chat.type == 'private':
        # Провека правильности введенного пароля
        if message.text == settingsBot.password:
            # создание клавиатуры под сообщением
            markup = types.InlineKeyboardMarkup(row_width=2)
            # Первое значение - текст, втророе - то, что кнопка ворачивает
            item1 = types.InlineKeyboardButton("Добавить вопрос",
                                               callback_data='newQuiz')
            item2 = types.InlineKeyboardButton("Добавить лекцию",
                                               callback_data='newArcticle')
            item3 = types.InlineKeyboardButton("Удалить вопрос",
                                               callback_data='delQuiz')
            item4 = types.InlineKeyboardButton("Удалить лекцию",
                                               callback_data='delArcticle')
            item5 = types.InlineKeyboardButton("Просмотреть все вопросы",
                                               callback_data='showQuiz')
            markup.add(item1, item2, item3, item4, item5)  # Создание маркупа
            bot.send_message(message.chat.id,
                             "Здравствуйте, выберите действие:",
                             reply_markup=markup)
        else:
            # Вывод сообщения в случае неправильного введенного паролья
            bot.send_message(message.chat.id, "Неверный пароль")


@bot.callback_query_handler(func=lambda call: True,)
def callback_inline(call):
    """
    Обработка всех кнопок с административной панели
    """
    if call.message:
        # Обработка кнопки "Добавить вопрос"
        if call.data == "newQuiz":
            bot.send_message(call.message.chat.id,
                             'Чтобы добавить вопрос нужно через через знак '
                             '"/" и без пробелов ввести номер, текст, первый '
                             'ответ, второй ответ, третий ответ, '
                             'правильный ответ')
            bot.register_next_step_handler(call.message, new_quiz)
        # Обработка кнопки "Добавить лекцию"
        if call.data == "newArcticle":
            bot.send_message(call.message.chat.id,
                             'Чтобы добавить лекцию введите номер лекции и '
                             'ссылку на неё через запятую, НЕ используя '
                             'пробел. Чтобы отменить действие введите '
                             '""ОТМЕНА"" ')
            bot.register_next_step_handler(call.message, new_articl)
        # Обработка кнопки "Удалить статью"
        if call.data == "delArcticle":
            bot.send_message(call.message.chat.id,
                             "Введите номер лекции, которую желаете удалить")
            bot.register_next_step_handler(call.message, del_articl)
        # Обработка кнопки "Удалить вопрос"
        if call.data == "delQuiz":
            bot.send_message(call.message.chat.id,
                             "Введите номер вопроса, который желаете удалить")
            bot.register_next_step_handler(call.message, del_quiz)
        # Обработка кнопки "Посмотреть все вопросы"
        if call.data == "showQuiz":
            bot.send_message(call.message.chat.id,
                             'Вот все доступные вопросы:')
            for question in show_quiz():
                bot.send_message(call.message.chat.id,
                                 f" ({question[0]})  {question[1]}")


def new_quiz(message):
    """
    Проверка и запись в БД вопроса
    """
    text = message.text
    # Подсчет количества знаков для определения правильности
    # введенных данных пользователем
    if text.count("/") != 5:
        bot.send_message(message.chat.id, settingsBot.wrong_mess)

    # Отработка команды "ОТМЕНА"
    if text == "ОТМЕНА":
        bot.send_message(message.chat.id, "Вы отменили действие")

    if text.count("/") == 5:
        text = (text.split("/"))  # присвоение списку строк отделяемых запятой
        # Подсчет количество полученных элементов
        if len(text) == 6:
            try:
                # Запись в таблицу articles значений в списке
                db.cur.execute(f""" INSERT INTO quiz
                    (ID, Text, FAn,
                    SAn, TAn, RAn)
                    VALUES({text[0]}, '{text[1]}', '{text[2]}',
                        '{text[3]}', '{text[4]}', '{text[5]}');""")
                db.con.commit()  # Запись в таблицу
                bot.send_message(message.chat.id, "Вопрос успешно добавлен")
            except sqlite3.IntegrityError:
                bot.send_message(message.chat.id,
                                 "Упс... Видимо, запись с таким ID уже есть")
        else:
            bot.send_message(message.chat.id, settingsBot.wrong_mess)


def new_articl(message):
    text = message.text
    # Подсчет количества знаков для определения правильности
    # введенных данных пользователем
    if text.count(",") != 1:
        bot.send_message(message.chat.id, settingsBot.wrong_mess)
    # Отработка команды "ОТМЕНА"
    if message == "ОТМЕНА":
        bot.send_message(message.chat.id, "Вы отменили действие")

    if text.count(",") == 1:  # проверка на наличие запятых
        try:
            # присвоение списку строк отделяемых запятой
            text = (text.split(","))
            db.cur.execute(f""" INSERT INTO articles
                (ID, link)
                VALUES({text[0]}, '{text[1]}');""")  # Запись в таблицу
            db.con.commit()  # Подтвержение на изменение таблицы
            bot.send_message(message.chat.id, "Лекция успешно добавлена")
        except sqlite3.IntegrityError:
            bot.send_message(message.chat.id,
                             "Упс... Видимо, запись с таким ID уже есть")


def del_articl(message):
    """
    Удаление лекции по его ID
    """
    try:
        text = message.text
        db.cur.execute(f""" DELETE FROM articles WHERE ID = {text}""")
        db.con.commit()
        bot.send_message(message.chat.id, "Лекция удалена")
    except sqlite3.ProgrammingError:
        bot.send_message(message.chat.id,
                         "Упс... Видимо нет лекции с таким ID")


def del_quiz(message):
    """
    Удаление вопроса по его ID
    """
    try:
        text = message.text
        db.cur.execute(f""" DELETE FROM quiz WHERE ID = {text}""")
        db.con.commit()
        bot.send_message(message.chat.id, "Вопрос удален")
    except sqlite3.ProgrammingError:
        bot.send_message(message.chat.id,
                         "Упс... Видимо нет лекции с таким ID")


def show_quiz():
    """
    Вывод "ID"  из таблицы "quiz"
          "Text"
    """
    question = []
    # Пробежка по всеей таблице quiz
    for quiz in db.cur.execute("""SELECT ID, Text FROM quiz"""):
        question.append(quiz)  # Создание списка
    return question  # передача значений


# RUN
bot.polling(none_stop=True)
