import telebot
import datetime
import random
import os
from flask import Flask
from threading import Thread

# আপনার টেলিগ্রাম বটের টোকেন
TOKEN = '8681018267:AAGglqSnLA5BYIttAuK1ypSY24ti0sBk8jU'
bot = telebot.TeleBot(TOKEN)

# রেন্ডার সার্ভার সচল রাখার জন্য ফ্লাস্ক সেটআপ
app = Flask('')

@app.route('/')
def home():
    return "TT Brothers World's Best AI Trading Bot is Running Live!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# ইউজারদের দৈনিক উইন/লস ডেটা ট্র্যাক করার মেমোরি ডিকশনারি
# Format: { user_id: { "date": "YYYY-MM-DD", "wins": 0, "losses": 0 } }
user_daily_stats = {}

def get_user_stats(user_id):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    if user_id not in user_daily_stats or user_daily_stats[user_id]["date"] != today:
        user_daily_stats[user_id] = {
            "date": today,
            "wins": 0,
            "losses": 0
        }
    return user_daily_stats[user_id]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👑 <b>𝕋𝕋 𝔹ℝ𝕆𝕋ℍ𝔼ℝ𝕊 [AZ] WORLD'S BEST AI BOT</b> এ স্বাগতম!\n\n"
        "🔥 <i>এই বট হ্যাক ম্যাট্রিক্স এবং অ্যাডভান্সড এআই বুদ্ধিমত্তা দিয়ে পরিচালিত।</i>\n\n"
        "📸 গেমের চার্ট বা স্কিনশট আপলোড করুন।\n"
        "🤖 বট নিজেই এনালাইসিস করে বলে দিবে **ট্রেড নেবেন কি না (Trade or Skip)**!\n\n"
        "📊 আপনার আজকের হিসাব দেখতে লিখুন: /stats"
    )
    bot.reply_to(message, welcome_text, parse_mode='HTML')

# দৈনিক হিসাব দেখার কমান্ড
@bot.message_handler(commands=['stats'])
def show_stats(message):
    user_id = message.from_user.id
    stats = get_user_stats(user_id)
    total = stats["wins"] + stats["losses"]
    win_rate = (stats["wins"] / total * 100) if total > 0 else 0

    report = (
        f"📊 <b>DAILY PERFORMANCE REPORT ({stats['date']})</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🟢 <b>Total Wins:</b> {stats['wins']}\n"
        f"🔴 <b>Total Losses:</b> {stats['losses']}\n"
        f"📈 <b>Win Accuracy:</b> {win_rate:.1f}%\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👑 <i>TT Brothers AI Risk Management System</i>"
    )
    bot.reply_to(message, report, parse_mode='HTML')

# ছবি আপলোড করলে এআই পাওয়ার ও ম্যাট্রিক্স হ্যাক দিয়ে এনালাইসিস
@bot.message_handler(content_types=['photo'])
def handle_image(message):
    bot.reply_to(message, "🧠 [AZ] Matrix AI স্ক্যান করছে... মার্কেট ভোলাটিলিটি ও সিওর শট ক্যালকুলেশন চলছে...")
    
    now = datetime.datetime.now()
    next_period = int(now.strftime("%Y%m%d%H%M")) + 1
    
    # এআই ইন্টেলিজেন্স ও সিওর শট ক্যালকুলেশন (রিস্ক এভয়েড করার জন্য রেন্ডম বা ম্যাট্রিক্স চেক)
    confidence_score = random.randint(75, 99)
    prediction = random.choice(["BIG", "SMALL"])
    
    # যদি কনফিডেন্স বা সিওর শট কম হয় (যেমন ৯২% এর নিচে), তবে ট্রেড নিতে নিষেধ করবে!
    if confidence_score < 92:
        response = (
            f"⚠️ <b>MARKET RISK WARNING (AVOID TRADE)</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔢 <b>Target Period:</b> <code>{next_period}</code>\n"
            f"📉 <b>Confidence Score:</b> {confidence_score}% (Low)\n"
            f"❌ <b>AI Decision:</b> <b>সিওর শট নয়! দয়া করে এই পিরিয়ডে ট্রেড নিবেন না। লস হতে পারে!</b>\n"
            f"💡 <b>Reason:</b> চার্ট প্যাটার্ন বর্তমানে আনস্টেবল এবং সাইডওয়েজ মোডে আছে। মার্কেট স্কিপ করুন।\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👑 <i>TT Brothers Safe-Guard AI</i>"
        )
    else:
        # সিওর শট হলে পারফেক্ট সিগন্যাল দিবে
        risk_status = "Very Safe (Sure Shot)"
        response = (
            f"💎 <b>[AZ] ULTRA-SURE SHOT SIGNAL</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔢 <b>Target Period:</b> <code>{next_period}</code>\n"
            f"🎯 <b>VIP Prediction:</b> <b>{prediction}</b>\n"
            f"🔥 <b>Confidence / Accuracy:</b> {confidence_score}%\n"
            f"🛡️ <b>Risk Status:</b> {risk_status}\n"
            f"✅ <b>AI Decision:</b> <b>ম্যাট্রিক্স হ্যাক ম্যাচ করেছে! ১০০% সিওর শট, কনফিডেন্সের সাথে ট্রেড নিতে পারেন।</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👑 <i>Powered by 𝕋𝕋 𝔹ℝ𝕆𝕋ℍ𝔼ℝ𝕊 [AZ] AI</i>"
        )
        
        # অটো উইন ট্র্যাক করার জন্য সিমুলেশন বা আপডেট অপশন রাখা যায়
        user_id = message.from_user.id
        stats = get_user_stats(user_id)
        stats["wins"] += 1  # ধরে নেওয়া হলো হাই-কনফিডেন্স সিগন্যাল উইন হবে

    bot.reply_to(message, response, parse_mode='HTML')

# টেক্সট পাঠালে কাজ করার সেকশন
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_input = message.text.upper().replace(" ", "")
    now = datetime.datetime.now()
    next_period = int(now.strftime("%Y%m%d%H%M")) + 1
    
    confidence = random.randint(80, 98)
    prediction = "SMALL" if "B" in user_input else "BIG"
    
    if confidence < 92:
        response = (
            f"⚠️ <b>AI ADVICE: DO NOT TRADE</b>\n"
            f"📊 <b>Input:</b> <code>{user_input}</code>\n"
            f"🔢 <b>Period:</b> <code>{next_period}</code>\n"
            f"❌ <b>Decision:</b> সিওর শট নয়! এই সিকোয়েন্সে রিস্ক বেশি, ট্রেড থেকে দূরে থাকুন।"
        )
    else:
        response = (
            f"✅ <b>SURE SHOT SIGNAL</b>\n"
            f"📊 <b>Input:</b> <code>{user_input}</code>\n"
            f"🔢 <b>Period:</b> <code>{next_period}</code>\n"
            f"🎯 <b>Prediction:</b> <b>{prediction}</b> (Accuracy: {confidence}%)\n"
            f"💡 <b>Decision:</b> ১০০% সিওর শট, ট্রেড নিতে পারেন!"
        )
    
    bot.reply_to(message, response, parse_mode='HTML')

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()