from openai import OpenAI
import telebot
from gtts import gTTS
import os

# токен телеграма
TOKEN = ""
bot = telebot.TeleBot(TOKEN)

# Инициализация клиента OpenAI с ключом
client = OpenAI(
    api_key="",
    base_url="https://api.proxyapi.ru/openai/v1",
)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Добро пожаловать! Я ваш новый Telegram-бот.\nВведите /help для списка доступных команд.")

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "Доступные команды:\n"
        "/start - приветственное сообщение\n"
        "/help - список команд\n"
        "/perevorot <текст> - перевернуть текст\n"
        "/ucode <текст> - Получить юникод-номер каждого символа в тексте\n"
        "/chat <текст> - отправить текст модели OpenAI для получения ответа\n"
        "/chatv <текст> - отправить текст модели OpenAI для получения ответа голосом\n"
    )
    bot.reply_to(message, help_text)

# Обработчик команды /perevorot
@bot.message_handler(commands=['perevorot'])
def reverse_text(message):
    text_to_reverse = message.text[len('/perevorot '):]
    if text_to_reverse:
        reversed_text = text_to_reverse[::-1]
        bot.reply_to(message, f"Перевернутый текст: {reversed_text}")
    else:
        bot.reply_to(message, "Пожалуйста, укажите текст для переворота после команды /perevorot.")

# Обработчик команды /ucode
@bot.message_handler(commands=['ucode'])
def unicode_number(message):
    text = message.text[len('/ucode '):]
    if not text:
        bot.reply_to(message, "Пожалуйста, укажите текст после команды /ucode.")
        return

    unicode_list = [f"{char} - U+{ord(char):04X}" for char in text]
    unicode_message = "\n".join(unicode_list)
    bot.reply_to(message, unicode_message)

# Обработчик команды /chat
@bot.message_handler(commands=['chat'])
def chat_with_model(message):
    user_input = message.text[len('/chat '):]

    if not user_input:
        bot.reply_to(message, "Пожалуйста, укажите текст для отправки модели после команды /chat.")
        return

    try:
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        # Извлечение и отправка ответа от модели
        response = chat_completion.choices[0].message.content
        bot.reply_to(message, f"Модель: {response}")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при обращении к модели: {e}")

# Обработчик команды /chatv
@bot.message_handler(commands=['chatv'])
def chat_with_model(message):
    user_input = message.text[len('/chatv '):]

    if not user_input:
        bot.reply_to(message, "Пожалуйста, укажите текст для отправки модели после команды /chatv.")
        return

    try:
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        response = chat_completion.choices[0].message.content
        
        # Преобразование текста в голосовое сообщение
        tts = gTTS(text=response, lang='ru')
        audio_file = "response.ogg"
        tts.save(audio_file)

        # Отправка голосового сообщения
        with open(audio_file, 'rb') as voice:
            bot.send_voice(message.chat.id, voice)

        # Удаление временного аудиофайла
        os.remove(audio_file)

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при обращении к модели: {e}")

# Запуск бота
if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)
