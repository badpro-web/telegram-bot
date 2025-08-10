import os
from telegram.ext import Application

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

app = Application.builder().token(TOKEN).build()
