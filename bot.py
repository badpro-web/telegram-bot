import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import asyncio
from datetime import datetime, time

# .env dan token yuklash
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Conversation bosqichlari
ASK_NAME, ASK_TIME, ASK_WORD = range(3)

# Foydalanuvchilar ma'lumotlari
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! Bezovta botga xush kelibsiz.\n"
        "Iltimos, ismingiz va familiyangizni yozing:"
    )
    return ASK_NAME

async def ask_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    full_name = update.message.text
    user_data[update.effective_user.id] = {"name": full_name}
    await update.message.reply_text(
        "Men sizni soat nechada bezovta qilishimni tanlang (masalan: 14:30):"
    )
    return ASK_TIME

async def ask_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        hour, minute = map(int, update.message.text.split(":"))
        user_data[update.effective_user.id]["time"] = time(hour, minute)
        await update.message.reply_text(
            "Men sizni qanday so‘z bilan bezovta qilay? (o‘zingiz hohlagan so‘zni yozing)"
        )
        return ASK_WORD
    except:
        await update.message.reply_text("Iltimos, vaqtni to‘g‘ri formatda kiriting. Masalan: 14:30")
        return ASK_TIME

async def save_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text
    user_data[update.effective_user.id]["word"] = word
    await update.message.reply_text("Sozlamalar saqlandi! Bot sizni belgilangan vaqtda bezovta qiladi.")

    asyncio.create_task(schedule_message(update, context))
    return ConversationHandler.END

async def schedule_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_info = user_data[user_id]
    while True:
        now = datetime.now().time()
        if now.hour == user_info["time"].hour and now.minute == user_info["time"].minute:
            await context.bot.send_message(chat_id=user_id, text=user_info["word"])
            await asyncio.sleep(60)
        await asyncio.sleep(10)

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_time)],
            ASK_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_word)],
            ASK_WORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_word)],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
