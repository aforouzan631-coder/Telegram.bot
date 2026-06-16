import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# گرفتن API از Railway Variables
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

# جواب دادن به پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("خطا رخ داد ❌")

# ساخت ربات
app = Application.builder().token(os.getenv("8962829320:AAHz3zbqOxSXpM-I_MU0LEVTpzr9eZvKyCc")).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot started...")

app.run_polling()
