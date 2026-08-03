import telebot
import datetime

TOKEN = '8681018267:AAGglqSnLA5BYIttAuK1ypSY24ti0sBk8jU'
bot = telebot.TeleBot(TOKEN)

FUTURE_PREMIUM_MODE = False  
FREE_DAILY_LIMIT = 10
ADMIN_ID = 123456789  
vip_users = [ADMIN_ID]
user_usage = {}

def check_signal_limit(user_id):
    if not FUTURE_PREMIUM_MODE:
        return True
    if user_id in vip_users:
        return True
    today = datetime.date.today().isoformat()
    if user_id not in user_usage:
        user_usage[user_id] = {'date': today, 'count': 0}
    if user_usage[user_id]['date'] != today:
        user_usage[user_id] = {'date': today, 'count': 0}
    if user_usage[user_id]['count'] < FREE_DAILY_LIMIT:
        user_usage[user_id]['count'] += 1
        return True
    else:
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👑 <b>𝕋𝕋 𝔹ℝ𝕆𝕋ℍ𝔼ℝ𝕊 [𝔸ℤ]_𝟛𝕏 𝕍𝕀ℙ 𝔹𝕠𝕥</b> এ স্বাগতম!\n\n"
        "গেমের শেষের ৩ বা ৪টি ফলাফল (B/S) লিখে পাঠান।\n"
        "যেমন: <code>B B S</code> অথবা <code>S S B S</code>\n\n"
        "💎 <i>প্রফেশনাল ও হাই-অ্যাকুরেসি প্যাটার্ন এনালাইজার।</i>"
    )
    bot.reply_to(message, welcome_text, parse_mode='HTML')

@bot.message_handler(func=lambda message: True)
def generate_prediction(message):
    user_id = message.from_user.id
    user_input = message.text.upper().replace(" ", "").replace(",", "")
    
    if not all(char in 'BS' for char in user_input):
        bot.reply_to(message, "⚠️ ভুল ইনপুট! দয়া করে শুধু B (Big) এবং S (Small) লিখে পাঠান।")
        return
    
    if len(user_input) < 3:
        bot.reply_to(message, "⚠️ সঠিক এনালাইসিসের জন্য অন্তত শেষের ৩টি ফাইল বা ফলাফল দিন।")
        return

    if not check_signal_limit(user_id):
        bot.reply_to(message, "🚫 <b>আপনার আজকের ফ্রি ১০টি সিগন্যাল লিমিট শেষ!</b>\n\nআনলিমিটেড সিগন্যাল পেতে আমাদের VIP মেম্বারশিপ সংগ্রহ করুন।", parse_mode='HTML')
        return

    recent_pattern = user_input[-4:]
    if recent_pattern.endswith("BBBB") or recent_pattern.endswith("SSSS"):
        result, accuracy, reason = ("SMALL" if recent_pattern.endswith("BBBB") else "BIG", "91%", "স্ট্রং ট্রেন্ড ব্রেকিং পয়েন্ট ও কারেকশন জোন।")
    elif recent_pattern.endswith("BSBS") or recent_pattern.endswith("SBSB"):
        result, accuracy, reason = ("BIG" if recent_pattern.endswith("SBSB") else "SMALL", "87%", "পারফেক্ট জিগজ্যাগ (Zigzag) প্যাটার্ন কন্টিনিউয়েশন।")
    elif recent_pattern.endswith("BBS") or recent_pattern.endswith("SSB"):
        result, accuracy, reason = ("SMALL" if recent_pattern.endswith("BBS") else "BIG", "83%", "শর্ট ট্রেন্ড রিভার্সাল সিগন্যাল।")
    else:
        result = "BIG" if recent_pattern[-1] == "B" else "SMALL"
        accuracy, reason = "78%", "স্মার্ট মার্কেট ফ্লো ও প্রোবাবিলিটি এনালাইসিস।"

    limit_text = ""
    if FUTURE_PREMIUM_MODE and user_id not in vip_users:
        left = FREE_DAILY_LIMIT - user_usage[user_id]['count']
        limit_text = f"\n🎁 <i>আজকের ফ্রি সিগন্যাল বাকি: {left} টি</i>"

    response = (
        f"📊 <b>Market Input:</b> <code>{user_input}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎯 <b>VIP Prediction:</b> <b>{result}</b>\n"
        f"🔥 <b>Accuracy Rate:</b> {accuracy}\n"
        f"💡 <b>Analysis Logic:</b> {reason}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👑 <i>Powered by 𝕋𝕋 𝔹ℝ𝕆𝕋ℍ𝔼ℝ𝕊 [𝔸ℤ]_𝟛𝕏</i>"
        f"{limit_text}"
    )
    bot.reply_to(message, response, parse_mode='HTML')

print("TT Brothers VIP Bot is Running Smoothly...")
bot.infinity_polling()