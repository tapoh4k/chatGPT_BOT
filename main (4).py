import random
import openai
import vk_api
import sqlite3
from langdetect import detect
from datetime import datetime
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

# Токен ВК необходим для связи бота с Вконтакте

VK_token = "vk1.a.mSnOxf521Eb-eUXTnlsopdrL3Q8Yzds_RgMhxdI4ZZNciAS07MqOHjSwz6ZEXSDwbM4Fr1CP7fmdYrRGh83WUScaGIO3fP9O3OKnCEzosRhNmqFuddl1VS0BeHoTxiPjrVDNmviJi_5CtOk1r8XAGQWWEMiVyb8WhWHMKEkLwx7O9DtA1bLRmVFPEtlORbcdOlfgvfU-fWAIv8FQBeY-LA"

database = None
cursor = None
vk_session = None
longpoll = None

# Подключение базы данных

# database = sqlite3.connect("gpt_database.db")

# Подключение курсора базы данных

# cursor = database.cursor()

# Функция создания таблицы в базе данных

# cursor.execute("CREATE TABLE messages(userid, message, answer, time)")

# Ключ openai - это ключ доступа к нейросети

openai.api_key = "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"

# Engine - используемый для получения ответов движок, всего таких движков около 10

engine = "text-davinci-003"

# Подключение в Вконтакте с помощью токена

# vk_session = vk_api.VkApi(token=VK_token)

# Получение событий из группы Вконтакте

# longpoll = VkBotLongPoll(vk_session, group_id=219866377)

# Создание списка с сообщениями

messages = []

# Создание списка со временем сообщений

times = []

# Создание списка с ответами на сообщения

answers = []

# Предыдущее сообщение бота

previous_message = ''

# Флаг перевода

translate = False

# Сообщение для перевода

message_to_translate = ''


# Функция получения ответа от нейросети

def gpt_callback(text):
    prompt = text
    completion = openai.Completion.create(engine=engine,
                                          prompt=prompt,
                                          temperature=0.5,
                                          max_tokens=1000)
    return completion.choices[0]['text']


# Функция создания базы данных
def create_database():
    cursor.execute("CREATE TABLE messages(userid, message, answer, time)")


# Функция инициализации базы данных

def init_database():
    global database, cursor
    database = sqlite3.connect("gpt_database.db")
    cursor = database.cursor()


# Функция инициализации подключения к вк

def init_VK():
    global vk_session, longpoll
    vk_session = vk_api.VkApi(token=VK_token)
    longpoll = VkBotLongPoll(vk_session, group_id=220062995)


# Функция инициализации бота

def init_bot():
    global translate, message_to_translate
    for event in longpoll.listen():
        # Прослушивание события присоединения нового пользователя к группе

        if event.type == VkBotEventType.GROUP_JOIN:
            joined = event.obj.message
            user_id = joined['from_id']

            vk_session.method('messages.send', {'user_id': user_id, 'random_id': random.randrange(0, 16), 'message':
                'Добро пожаловать в группу! Я бот GPT Вконтакте. Можете задать мне любой вопрос и '
                'я попытаюсь дать на него корректный ответ. Чем я могу вам помочь?'})

        # Прослушивание события получения нового сообщения

        if event.type == VkBotEventType.MESSAGE_NEW:
            # Получение данных из сообщения

            message = event.obj.message
            user_id = message['from_id']
            text = message['text']

            vk_session.method('messages.send', {'user_id': user_id, 'random_id': random.randrange(0, 16), 'message':
                'Секунду, ваш запрос обрабатывается.'})

            # Перевод сообщения, если пользователь утвердительно ответил на вопрос о переводе

            if text.lower() == "да" and translate:
                vk_session.method('messages.send', {'user_id': user_id, 'random_id': random.randrange(0, 16), 'message':
                    f'Переведи на русский язык сообщение: {gpt_callback(message_to_translate)}'})
                translate = False
            else:
                if detect_language(text) == "en":
                    message_to_translate = text
                    translate = True
                # Обработка некоторых зафиксированных запросов и отправление ответов на них
                if text.lower() == 'помощь':
                    vk_session.method('messages.send',
                                      {'user_id': user_id, 'random_id': random.randrange(0, 16), 'message':
                                          'Список доступных команд: Принцип работы, Возможности, Ограничения, Средняя длина сообщений,'
                                          'Средняя длина ответов.'
                                          'Для вызова команды напишите соответствующее сообщение в чате.'})
                    previous_message = 'Список доступных команд: Принцип работы, Возможности, Ограничения, Средняя длина сообщений,' \
                                       'Средняя длина ответов.' \
                                       'Для вызова команды напишите соответствующее сообщение в чате.'
                elif text.lower() == 'принцип работы':
                    vk_session.method('messages.send',
                                      {'user_id': user_id, 'random_id': random.randrange(0, 16), 'message':
                                          'Данный бот работает при помощи взаимодействия с нейросетью ChatGPT. При вводе в чат команды '
                                          'отправляется соответствующий запрос, ответом на который является выводимый текст. '
                                          'Точность ответа на вопрос может настраивать владелец бота, однако, при более точных ответах '
                                          'время получения ответа на запрос значительно увеличивается'})
                    previous_message = 'Данный бот работает при помощи взаимодействия с нейросетью ChatGPT. При вводе в чат команды ' \
                                       'отправляется соответствующий запрос, ответом на который является выводимый текст. ' \
                                       'Точность ответа на вопрос может настраивать владелец бота, однако, при более точных ответах ' \
                                       'время получения ответа на запрос значительно увеличивается'
                elif text.lower() == 'возможности':
                    vk_session.method('messages.send',
                                      {'user_id': user_id, 'random_id': random.randrange(0, 16), 'message':
                                          'Я способен ответить на большинство запросов, которые могут быть заданы. '
                                          'В качестве ответа может выступать не только текст сообщения, но и, например, код для программы,'
                                          'если задан такой запрос.'})
                    previous_message = 'Я способен ответить на большинство запросов, которые могут быть заданы. ' \
                                       'В качестве ответа может выступать не только текст сообщения, но и, например, код для программы,' \
                                       'если задан такой запрос.'
                elif text.lower() == 'ограничения':
                    vk_session.method('messages.send',
                                      {'user_id': user_id, 'random_id': random.randrange(0, 16), 'message':
                                          'Я способен ответить на большинство вопросов, но не на все. '
                                          'Если данные, необходимые для ответа на запрос не находятся в открытом доступе, '
                                          'у меня может не получиться найти ответ. Также я не могу дать ответ на события из реального мира, '
                                          'которые произошли после 2020 года, поскольку я обучался до 2020 года.'})
                    previous_message = 'Я способен ответить на большинство вопросов, но не на все. ' \
                                       'Если данные, необходимые для ответа на запрос не находятся в открытом доступе, ' \
                                       'у меня может не получиться найти ответ. Также я не могу дать ответ на события из реального мира, ' \
                                       'которые произошли после 2020 года, поскольку я обучался до 2020 года.'
                elif text.lower() == 'средняя длина сообщений':
                    get_messages(user_id)
                    average_message_length(user_id)
                elif text.lower() == 'средняя длина ответов':
                    get_answers(user_id)
                    average_answer_length(user_id)
                else:
                    vk_session.method('messages.send',
                                      {'user_id': user_id, 'random_id': random.randrange(0, 16), 'message':
                                          gpt_callback(text)})
                    previous_message = gpt_callback(text)

                # Если сообщение на английском - задается вопрос о переводе
                if translate:
                    vk_session.method('messages.send',
                                      {'user_id': user_id, 'random_id': random.randrange(0, 16), 'message':
                                          'Похоже, ваше сообщение, как и ответ на него, написаны на английском языке, желаете перевести?'})


# Функция получения всех сообщений пользователя из базы данных и добавление их в массив

def get_messages(userid):
    get_data = cursor.execute(f"SELECT message FROM messages WHERE userid = {userid}")
    for data in get_data.fetchall():
        messages.append(data)


# Функция получения времени отправки всех сообщений

def get_messages_times(userid):
    get_data = cursor.execute(f"SELECT time FROM messages WHERE userid = {userid}")
    for data in get_data.fetchall():
        times.append(data)


# Функция получения всех ответов на сообщения пользователя из базы данных и добавление их в массив

def get_answers(userid):
    get_data = cursor.execute(f"SELECT answer FROM messages WHERE userid = {userid}")
    for data in get_data.fetchall():
        answers.append(data)


# Функция определения средней длины сообщений пользователя

def average_message_length(userid):
    temp = [len(data) for data in messages]
    result = 0 if len(temp) == 0 else (float(sum(temp)) / len(temp))
    vk_session.method('messages.send', {'user_id': userid, 'random_id': random.randrange(0, 16), 'message':
        f'Средняя длина сообщений: {result}'})


# Функция определения средней длины ответов на сообщения пользователей

def average_answer_length(userid):
    temp = [len(data) for data in messages]
    result = 0 if len(temp) == 0 else (float(sum(temp)) / len(temp))
    vk_session.method('messages.send', {'user_id': userid, 'random_id': random.randrange(0, 16), 'message':
        f'Средняя длина ответов на сообщения: {result}'})


# Функция добавления новой записи в базу данных

def add_message_in_database(userid, message, answer):
    cursor.execute(f"""INSERT INTO messages VALUES 
                    ({userid}, {message}, {answer}, {datetime.now()})""")


# Функция определения языка сообщения

def detect_language(message):
    return detect(message)


# Функция запуска программы

if __name__ == "__main__":
    init_VK()
    init_database()
    init_bot()
