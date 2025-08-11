import os
import re
from datetime import datetime, time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

# Bosqichlar
ASK_NAME, ASK_TIME, ASK_PHRASE, MENU = range(4)

# Foydalanuvchi ma'lumotlarini saqlash
user_data = {}

# Token olish
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu aleykum! Bezovta botga xush kelibsiz.\n\nIltimos, ism va familiyangizni kiriting:"
    )
    return ASK_NAME

# Ism familiya so‘rash
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    full_name = update.message.text.strip()
    context.user_data["name"] = full_name
    await update.message.reply_text(
        f"Rahmat, {full_name}!\nEndi meni sizni soat nechada bezovta qilishimni tanlang (HH:MM formatida):"
    )
    return ASK_TIME

# Soatni tekshirish va so‘rash
async def ask_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time_text = update.message.text.strip()
    if not re.match(r"^\d{2}:\d{2}$", time_text):
        await update.message.reply_text("Qayta soatni tanlang (_ _:_ _)")
        return ASK_TIME

    try:
        hour, minute = map(int, time_text.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
        context.user_data["time"] = time(hour, minute)
    except ValueError:
        await update.message.reply_text("Qayta soatni tanlang (_ _:_ _)")
        return ASK_TIME

    await update.message.reply_text("Endi meni qanday so‘z bilan bezovta qilishimni yozing:")
    return ASK_PHRASE

# Bezovta so‘zi so‘rash
async def ask_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phrase = update.message.text.strip()
    context.user_data["phrase"] = phrase

    user_id = update.effective_user.id
    name = context.user_data["name"]
    alarm_time = context.user_data["time"]

    user_data[user_id] = {
        "name": name,
        "time": alarm_time,
        "phrase": phrase
    }

    await update.message.reply_text(
        f"✅ Sozlamalar saqlandi!\n\n⏰ Vaqt: {alarm_time.strftime('%H:%M')}\n💬 So‘z: {phrase}",
        reply_markup=ReplyKeyboardMarkup(
            [["⏰ Vaqtni o‘zgartirish", "💬 So‘zni o‘zgartirish"]],
            resize_keyboard=True
        )
    )
    return MENU

# Menyuda vaqt o‘zgartirish
async def change_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yangi vaqtni kiriting (HH:MM):")
    return ASK_TIME

# Menyuda so‘z o‘zgartirish
async def change_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yangi bezovta so‘zini kiriting:")
    return ASK_PHRASE

# Har daqiqa tekshirib, xabar yuborish
async def alarm_checker(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().time()
    for user_id, info in user_data.items():
        if info["time"].hour == now.hour and info["time"].minute == now.minute:
            await context.bot.send_message(chat_id=user_id, text=info["phrase"])

# Bot ishga tushirish
def main():
    # job_queue ni qo‘shish uchun builderda .job_queue(True) ishlatiladi
    app = Application.builder().token(TOKEN).job_queue(True).build()

    # Har daqiqada alarm_checker ishlatish
    app.job_queue.run_repeating(alarm_checker, interval=60, first=0)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_time)],
            ASK_PHRASE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phrase)],
            MENU: [
                MessageHandler(filters.Regex("^⏰ Vaqtni o‘zgartirish$"), change_time),
                MessageHandler(filters.Regex("^💬 So‘zni o‘zgartirish$"), change_phrase),
            ]
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
