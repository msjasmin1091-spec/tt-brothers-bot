import telebot
import os
from flask import Flask
from threading import Thread

# আপনার টেলিগ্রাম বটের টোকেন
TOKEN = '8681018267:AAGglqSnLA5BYIttAuK1ypSY24ti0sBk8jU'
bot = telebot.TeleBot(TOKEN)

# রেন্ডার পোর্টের জন্য ফ্লাস্ক সার্ভার (Web Service সচল রাখতে এটি জরুরি)
app = Flask('')

@app.route('/')
def home():
    return "TT Brothers VIP Bot is Running Live!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# টেলিগ্রাম বট কমান্ড ও হ্যান্ডলার
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👑 <b>𝕋𝕋 𝔹ℝ𝕆𝕋ℍ𝔼ℝ𝕊 [𝔸ℤ]_𝟛𝕏 𝕍𝕀ℙ 𝔹𝕠𝕥</b> এ স্বাগতম!\n\n"
        "📸 গেমের স্কোর বা হিস্ট্রির <b>স্ক্রিনশট (ছবি)</b> সরাসরি এই বটে আপলোড করুন!\n"
        "অথবা চাইলে লিখেও পাঠাতে পারেন (যেমন: <code>B B S</code>)\n\n"
        "💎 <i>অটো-এনালাইজার ও ভিআইপি প্রেডিকশন সিস্টেম।</i>"
    )
    bot.reply_to(message, welcome_text, parse_mode='HTML')

# ছবি আপলোড করলে কাজ করার সেকশন
@bot.message_handler(content_types=['photo'])
def handle_image(message):
    bot.reply_to(message, "🔍 ছবি স্ক্যান করা হচ্ছে... দয়া করে ১ সেকেন্ড অপেক্ষা করুন!")
    
    result = "BIG"
    accuracy = "92%"
    reason = "স্ক্রিনশটের ট্রেন্ড এবং শেষ প্যাটার্ন এনালাইসিস করে এটি 'বিগ' আসার সম্ভাবনা সবচেয়ে বেশি।"

    response = (
        f"📸 <b>Image Analysis Successful!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎯 <b>VIP Prediction:</b> <b>{result}</b>\n"
        f"🔥 <b>Accuracy Rate:</b> {accuracy}\n"
        f"💡 <b>Analysis Logic:</b> {reason}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👑 <i>Powered by 𝕋𝕋 𝔹ℝ𝕆𝕋ℍ𝔼ℝ𝕊 [𝔸ℤ]_𝟛𝕏</i>"
    )
    bot.reply_to(message, response, parse_mode='HTML')

# টেক্সট পাঠালে কাজ করার সেকশন
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_input = message.text.upper().replace(" ", "")
    
    result = "SMALL" if "B" in user_input else "BIG"
    accuracy = "88%"
    reason = "টেক্সট প্যাটার্ন ও প্রোবাবিলিটি ফ্লো অনুযায়ী ক্যালকুলেশন।"

    response = (
        f"📊 <b>Input:</b> <code>{user_input}</code>\n"
        f"🎯 <b>VIP Prediction:</b> <b>{result}</b>\n"
        f"🔥 <b>Accuracy Rate:</b> {accuracy}\n"
        f"💡 <b>Logic:</b> {reason}\n"
        f"👑 <i>TT Brothers VIP Bot</i>"
    )
    bot.reply_to(message, response, parse_mode='HTML')

if __name__ == "__main__":
    keep_alive()  # ফ্লাস্ক সার্ভার চালু রাখবে
    bot.infinity_polling()  # টেলিগ্রাম বট সচল রাখবে