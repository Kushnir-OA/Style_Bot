# Бот-стилист:
# 1. подбирает цвет дня
# 2. подбирает комплект одежды на день
# 3. отвечает на текстовый вопрос по стилю (AI - ChatGPT)
# 4. отвечает на голосовой вопрос по стилю (AI - ChatGPT)

import asyncio
import requests
from bs4 import BeautifulSoup
import telebot
from openai import OpenAI
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
import os
import subprocess
import random
from telebot import types

# Инициализация клиента OpenAI
client = OpenAI(
    api_key="my_key",
    base_url="https://api.proxyapi.ru/openai/v1",
)

# Инициализация Telegram-бота
API_TOKEN = 'BOT_API_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

# Список цветов
colors = [
    "🌸 Нежно-голубой 🌸", "🍯 Сливочное масло 🍯", "🌷 Свежий персик 🌷",
    "🍇 Темный виноград 🍇", "🌺 Лавандовый бриз 🌺", "🍃 Лесная зелень 🍃",
    "🌻 Солнечный закат 🌻", "🍑 Персиковый пудинг 🍑", "🌸 Розовый кварц 🌸",
    "🍂 Осенний лист 🍂", "🌊 Морская волна 🌊", "🍋 Лимонный свет 🍋",
    "🌷 Орхидея в тумане 🌷", "🍇 Вишневый пирог 🍇", "🌺 Сиреневый туман 🌺",
    "🍃 Изумрудный лес 🍃", "🌻 Золотая пыль 🌻", "🍑 Абрикосовый рассвет 🍑",
    "🌸 Розовая дымка 🌸", "🍂 Золотая осень 🍂", "🌊 Океанская гладь 🌊",
    "🍋 Солнечный лимон 🍋", "🌷 Лавандовое поле 🌷", "🍇 Винный бархат 🍇",
    "🪩 Серебряный дождь 💍"
]

# Списки предметов одежды
tops = ["Футболка", "Рубашка", "Свитер", "Топ", "Блузка", "Туника", "Кардиган", "Джемпер", "Худи", "Жилет"]
bottoms = ["Джинсы", "Брюки", "Шорты", "Юбка", "Легинсы", "Капри", "Бриджи", "Сарафан", "Комбинезон", "Штаны"]
shoes = ["Кроссовки", "Туфли", "Сандалии", "Ботинки", "Балетки", "Сапоги", "Шлепанцы", "Босоножки", "Мокасины", "Кеды"]
headwear = ["Кепка", "Шляпа", "Берет", "Панама", "Бейсболка", "Бандана", "Платок", "Шапка", "Капюшон", "Тюрбан"]
accessories = ["Сумка", "Рюкзак", "Очки", "Шарф", "Браслет", "Колье", "Серьги", "Перчатки", "Часы"]

# Функция для получения ответа от нейросети
def get_chat_response(messages):
    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return chat_completion.choices[0].message.content

# Словарь для хранения истории сообщений каждого чата
chat_histories = {}

# Функция для получения последней новости с веб-страницы канала
def get_latest_news():
    url = 'https://www.buro247.ru/news'  # Указать нужный URL веб-страницы с новостями
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Найдите элементы с последними новостями
    news_items = soup.find_all('div', class_='newsPreviewPhoto')
    if news_items:
        latest_news = news_items[0]
        title = latest_news.find('h4').get_text(strip=True)
        link = latest_news.find('a', class_='image-wrap')['href']
        full_link = f"https://www.buro247.ru{link}"
        return f"{title}\n{full_link}"
    else:
        return "Новостей нет."

# Функция для преобразования голосового сообщения в текст
def transcribe_audio(audio_path):
    # Конвертируем OGG в WAV
    wav_path = audio_path.replace(".ogg", ".wav")
    ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe" # путь до ffmpeg.exe в явном виде
    subprocess.run([ffmpeg_path, '-i', audio_path, wav_path])

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio, language="ru-RU")
        except sr.UnknownValueError:
            return "Распознавание не удалось"
        except sr.RequestError:
            return "Ошибка сервиса распознавания"

# Создание клавиатуры с кнопками
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton('Цвет дня'))
    markup.row(types.KeyboardButton('Комплект на сегодня'))
    markup.row(types.KeyboardButton('Текстовый диалог'))
    markup.row(types.KeyboardButton('Голосовой диалог'))
    markup.row(types.KeyboardButton('Последние новости'))
    return markup

# Обработчик команд /start и /help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Привет! Я твой бот-стилист. Выбери одну из опций ниже:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id

    if message.text == 'Цвет дня':
        selected_color = random.choice(colors)
        bot.send_message(chat_id, f"Сегодня тебя украсит цвет: {selected_color}")

    elif message.text == 'Комплект на сегодня':
        selected_top = random.choice(tops)
        selected_bottom = random.choice(bottoms)
        selected_shoes = random.choice(shoes)
        selected_headwear = random.choice(headwear)
        selected_accessory = random.choice(accessories)

        clouth_message = (
            f"Твой комплект одежды на сегодня:\n"
            f"Верх: {selected_top}\n"
            f"Низ: {selected_bottom}\n"
            f"Обувь: {selected_shoes}\n"
            f"Головной убор: {selected_headwear}\n"
            f"Аксессуар: {selected_accessory}"
        )
        bot.send_message(chat_id, clouth_message)

    elif message.text == 'Текстовый диалог':
        bot.send_message(chat_id, "Напиши мне, что хочешь узнать:")
        bot.register_next_step_handler(message, handle_text_message)

    elif message.text == 'Голосовой диалог':
        bot.send_message(chat_id, "Отправь мне свой вопрос голосовым сообщением:")
        bot.register_next_step_handler(message, handle_voice_message)

    elif message.text == 'Последние новости с сайта BURO.':
        news = get_latest_news()
        bot.send_message(chat_id, news)

    else:
        bot.send_message(chat_id, "Пожалуйста, выбери одну из опций:", reply_markup=get_main_keyboard())

# Обработчик текстовых сообщений
def handle_text_message(message):
    chat_id = message.chat.id
    user_message = message.text

    # Инициализация истории сообщений для нового чата
    # Задаю TOV для текстовых сообщений AI стилиста
    if chat_id not in chat_histories:
        chat_histories[chat_id] = [{"role": "system", "content": \
            "Отвечай как известная модная стилистка и близкая подруга, \
            давай четкие и КРАТКИЕ рекомендации по стилю в одежде и аксессуарах. \
            Не используй нумерацию в ответах."}]

    # Добавляем сообщение пользователя в историю
    chat_histories[chat_id].append({"role": "user", "content": user_message})

    # Получаем ответ от нейросети
    response = get_chat_response(chat_histories[chat_id])

    # Отправляем ответ пользователю как текст
    if response is not None:
        bot.reply_to(message, response)

    # Добавляем ответ нейросети в историю
    chat_histories[chat_id].append({"role": "assistant", "content": response})

# Обработчик голосовых сообщений
def handle_voice_message(message):
    chat_id = message.chat.id

    bot.send_message(chat_id, "Ожидай, записываю тебе ответ!")

    # Скачиваем голосовое сообщение
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Сохраняем аудиофайл
    audio_path = f"voice_message_{chat_id}.ogg"
    with open(audio_path, 'wb') as f:
        f.write(downloaded_file)

    # Преобразуем голосовое сообщение в текст
    user_message = transcribe_audio(audio_path)

    # Удаляем временные аудиофайлы
    os.remove(audio_path)
    os.remove(audio_path.replace(".ogg", ".wav"))

    # Инициализация истории сообщений для нового чата
    # Задаю TOV для голосовых сообщений AI стилиста (отдельно от текстовых - может отличаться!)
    if chat_id not in chat_histories:
        chat_histories[chat_id] = [{"role": "system", "content": \
            "Отвечай как известная модная стилистка и близкая подруга, \
            давай четкие и КРАТКИЕ рекомендации по стилю в одежде и аксессуарах. \
            Не используй нумерацию в ответах."}]

    # Добавляем сообщение пользователя в историю
    chat_histories[chat_id].append({"role": "user", "content": user_message})

    # Получаем ответ от нейросети
    response = get_chat_response(chat_histories[chat_id])

    # Отправляем ответ пользователю только как голосовое сообщение
    if response is not None:
        # Преобразование текста в речь
        tts = gTTS(text=response, lang='ru')
        audio = BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)

        # Отправка голосового сообщения
        bot.send_voice(chat_id, audio)

    # Добавляем ответ нейросети в историю
    chat_histories[chat_id].append({"role": "assistant", "content": response})

# Запуск бота
if __name__ == "__main__":
    bot.polling()
