import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import google.generativeai as genai

# ====== API KEYS ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


# ====== START ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 سلام! من ربات هوش مصنوعی هستم\n\n"
        "💬 چت کن\n"
        "💰 بنویس: طلا\n"
        "🌍 بنویس: ترجمه Hello\n"
    )


# ====== GOLD PRICE ======
def get_gold_price():
    try:
        url = "https://api.tgju.org/v1/data/sana/json"
        res = requests.get(url).json()
        gold = res["data"]["geram18"]
        return f"💰 قیمت طلا 18 عیار: {gold} تومان"
    except:
        return "❌ خطا در دریافت قیمت طلا"


# ====== MAIN CHAT ======
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    # --- GOLD ---
    if "طلا" in text:
        await update.message.reply_text(get_gold_price())
        return

    # --- TRANSLATE ---
    if text.startswith("ترجمه"):
        prompt = f"Translate this to Persian or English depending on language: {text}"
    else:
        prompt = text

    try:
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")


# ====== GROUP MANAGEMENT ======
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        await update.message.reply_text(f"👋 خوش آمدی {user.first_name}!")


# ====== APP ======
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

app.run_polling()
