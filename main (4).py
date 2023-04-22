import random
import openai
import vk_api
import sqlite3
from langdetect import detect
from datetime import datetime
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

# Токен ВК необходим для связи бота с Вконтакте

VK_token = "vk1.a.g2UQKpyQWvru8RYpCmRl8UPnt-cs_hIpNzHkG69cNsyDWtfOb2vslflAGqyXHJS81tfIcXeWx" \
           "-zMGqJ8zbyXBXElHnEoLxzumEv_tr27K7Xspl 6tyUIk3W32zhb_EEFsOyp5itnkciqRpn" \
           "-K5VIGPa2iUOquAwSvpMSZj_OvrN8NTUrT0Sek5XpuLy4vQt0RSzcDkpy6VJypHys5JIVaAg"

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
