import os
import time
import sqlite3
import requests
from collections import defaultdict
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from google import genai

# ================== KEYS ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

# ================== DATABASE ==================
conn = sqlite3.connect("business.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    role TEXT DEFAULT 'free',
    messages INTEGER DEFAULT 0
)
""")
conn.commit()

# ================== MEMORY ==================
memory = defaultdict(list)
last_msg = {}

# ================== ADMIN ID (تو بزن) ==================
ADMIN_ID = 123456789  # 👈 آیدی خودت را اینجا بگذار

# ================== GOLD ==================
def gold_price():
    try:
        r = requests.get("https://api.tgju.org/v1/data/sana/json").json()
        return f"💰 طلا 18: {r['data']['geram18']} تومان"
    except:
        return "❌ خطا در قیمت طلا"

# ================== USER ==================
def get_user(user_id):
    cursor.execute("SELECT role, messages FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if not row:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return ("free", 0)

    return row

def add_msg(user_id):
    cursor.execute("UPDATE users SET messages = messages + 1 WHERE user_id=?", (user_id,))
    conn.commit()

# ================== AI ==================
def ai(user_id, text):
    history = memory[user_id][-6:]
    prompt = "\n".join(history + [text])

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

    memory[user_id].append(text)
    memory[user_id].append(response.text)

    return response.text

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 GOD BUSINESS BOT فعال شد\n\n"
        "💬 چت کن\n💰 طلا بنویس\n📊 /panel برای ادمین"
    )

# ================== PANEL ==================
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ فقط ادمین")

    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    await update.message.reply_text(
        f"👑 پنل ادمین\n\n"
        f"👤 کاربران: {users}\n"
        f"💎 سیستم فعال است"
    )

# ================== BAN ==================
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        await update.effective_chat.ban_member(user_id)
        await update.message.reply_text("🚫 بن شد")

# ================== MAIN ==================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    role, msg_count = get_user(user_id)

    # ================== ANTI SPAM ==================
    now = time.time()
    if user_id in last_msg and now - last_msg[user_id] < 1.2:
        return
    last_msg[user_id] = now

    # ================== LIMIT FREE ==================
    if role == "free" and msg_count >= 25:
        await update.message.reply_text("❌ محدودیت تموم شد → VIP بگیر")
        return

    add_msg(user_id)

    # ================== GOLD ==================
    if "طلا" in text:
        await update.message.reply_text(gold_price())
        return

    # ================== AI ==================
    try:
        reply = ai(user_id, text)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ================== APP ==================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("panel", panel))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

app.run_polling()
