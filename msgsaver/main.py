import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

token = ""

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (user_id INTEGER, username TEXT, message TEXT)''')
    conn.commit()
    conn.close()

# Функция для сохранения сообщения в БД
def save_message(user_id, username, message):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (user_id, username, message) VALUES (?, ?, ?)", (user_id, username, message))
    conn.commit()
    conn.close()

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    username = update.effective_user.username
    message = update.message.text
    save_message(user_id, username, message)
    await update.message.reply_text(f"Сообщение '{message}' сохранено!")

# Команда /listmsg для вывода сообщений текущего пользователя
async def list_user_messages(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("SELECT message FROM messages WHERE user_id=?", (user_id,))
    messages = c.fetchall()
    conn.close()

    if not messages:
        await update.message.reply_text("У вас нет сохраненных сообщений.")
    else:
        for msg in messages:
            await update.message.reply_text(msg[0])

# Команда /listmsgall для вывода всех сообщений всех пользователей
async def list_all_messages(update: Update, context: CallbackContext):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("SELECT username, message FROM messages")
    messages = c.fetchall()
    conn.close()

    if not messages:
        await update.message.reply_text("Нет сохраненных сообщений.")
    else:
        for username, msg in messages:
            await update.message.reply_text(f"{username}: {msg}")

def main():
    # Инициализация базы данных
    init_db()

    # Создание экземпляра ApplicationBuilder и передача ему токена бота
    application = ApplicationBuilder().token(token).build()

    # Обработчики команд
    application.add_handler(CommandHandler("listmsg", list_user_messages))
    application.add_handler(CommandHandler("listmsgall", list_all_messages))

    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
