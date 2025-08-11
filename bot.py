import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔹 Logging sozlash
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 🔹 Tokenni olish
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN topilmadi! Railway Variables ichida BOT_TOKEN ni qo‘sh!")

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Bot ishlayapti 🚀 (faqat bitta marta)")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # 🔹 Faqat bitta marta ishlaydigan handler
    app.add_handler(CommandHandler("start", start))

    app.run_polling(drop_pending_updates=True)
