import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = 123456789  # 👈 آی‌دی خودت

client = genai.Client(api_key=GEMINI_API_KEY)

# ================= DATABASE ساده =================
users = {}
vip_users = set()

# ================= MENU =================
menu = ReplyKeyboardMarkup([
    ["🤖 AI", "💰 قیمت طلا"],
    ["🌍 ترجمه", "⭐ خرید VIP"],
    ["ℹ️ درباره ما"]
], resize_keyboard=True)

# ================= GOLD PRICE =================
def gold_price():
    try:
        r = requests.get("https://api.tgju.org/v1/data/price/index?key=mesghal")
        data = r.json()
        return f"💰 قیمت طلا: {data['data']['price']} تومان"
    except:
        return "❌ خطا در دریافت قیمت"

# ================= AI =================
def ai(text):
    try:
        res = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=text
        )
        return res.text
    except:
        return "❌ خطا در AI"

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users[user_id] = users.get(user_id, 0) + 1

    await update.message.reply_text(
        "👨‍💻 خوش آمدید به ربات حرفه‌ای\n\n"
        "✔ AI\n✔ قیمت طلا\n✔ VIP\n✔ ترجمه\n\n"
        "👑 سازنده: امیر علی فروزان اصل\n"
        "📢 @amirforozanasl",
        reply_markup=menu
    )

# ================= MESSAGE HANDLER =================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # VIP check
    if text == "⭐ خرید VIP":
        await update.message.reply_text(
            "💎 برای خرید VIP از لینک پرداخت استفاده کن:\n\n"
            "🔗 (اینجا درگاه خودت را قرار بده)\n\n"
            "بعد از پرداخت به ادمین پیام بده."
        )
        return

    # AI (VIP یا رایگان)
    if text == "🤖 AI":
        if user_id not in vip_users and user_id != ADMIN_ID:
            await update.message.reply_text("🔒 این بخش فقط برای VIP است")
            return

        await update.message.reply_text("✍️ سوالت را بفرست:")
        return

    # GOLD
    if text == "💰 قیمت طلا":
        await update.message.reply_text(gold_price())
        return

    # TRANSLATE
    if text == "🌍 ترجمه":
        await update.message.reply_text("✍️ متن را بفرست برای ترجمه:")
        return

    # AI RESPONSE
    if user_id in vip_users or user_id == ADMIN_ID:
        await update.message.reply_text(ai(text))
    else:
        await update.message.reply_text("🔒 برای استفاده کامل VIP شو")

# ================= ADMIN =================
async def addvip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        uid = int(context.args[0])
        vip_users.add(uid)
        await update.message.reply_text("✅ VIP فعال شد")
    except:
        await update.message.reply_text("❌ /addvip user_id")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        f"👥 کاربران: {len(users)}\n⭐ VIP: {len(vip_users)}"
    )

# ================= RUN =================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addvip", addvip))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()
