from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response = model.generate_content(text)
    await update.message.reply_text(response.text)

app = Application.builder().token("8764803349:AAGKSOGGgXKRSp0W0i0Tte8qIqUt1a9Z8w0").build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

app.run_polling()
