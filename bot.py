import os
from telegram.ext import Application, CommandHandler

# Tokenni environment'dan olish
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# /start komandasi uchun funksiya
async def start(update, context):
    await update.message.reply_text("Salom! Bot ishlayapti ✅")

# Asosiy ishga tushirish qismi
def main():
    app = Application.builder().token(TOKEN).build()

    # Handler qo‘shish
    app.add_handler(CommandHandler("start", start))

    # Polling rejimida ishlash
    app.run_polling()

if __name__ == "__main__":
    main()
