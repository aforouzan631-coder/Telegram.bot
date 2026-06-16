import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text

        response = model.generate_content(text)

        await update.message.reply_text(response.text)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


app = Application.builder().token(os.getenv("BOT_TOKEN")).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

app.run_polling()
