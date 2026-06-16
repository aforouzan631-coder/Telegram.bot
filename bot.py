import os
import time
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from google import genai

# ================== KEYS ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ درست و تمیز (هیچ string نباید بشه)
client = genai.Client(api_key=GEMINI_API_KEY)

# ================== ANTI SPAM ==================
last_msg_time = {}

# ================== GOLD ==================
def gold_price():
    try:
        r = requests.get("https://api.tgju.org/v1/data/sana/json").json()
        return f"💰 طلا 18: {r['data']['geram18']} تومان"
    except:
        return "❌ خطا در دریافت قیمت طلا"

# ================== AI ==================
def ai_answer(text):
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=text
    )
    return response.text

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ربات فعال شد\n\n"
        "💬 پیام بده\n💰 طلا\n🌍 ترجمه: translate hello"
    )

# ================== MAIN ==================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # 🔥 ضد اسپم ساده
    now = time.time()
    if user_id in last_msg_time and now - last_msg_time[user_id] < 1.5:
        return
    last_msg_time[user_id] = now

    # 💰 طلا
    if "طلا" in text:
        await update.message.reply_text(gold_price())
        return

    # 🌍 ترجمه ساده
    if text.lower().startswith("translate"):
        text = "Translate: " + text

    # 🤖 AI
    try:
        reply = ai_answer(text)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

# ================== APP ==================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
