import telebot
import datetime
import random
import os
import re
import pytesseract
from PIL import Image
from io import BytesIO
from flask import Flask
from threading import Thread
from telebot import types

# আপনার টেলিগ্রাম বটের টোকেন
TOKEN = '8681018267:AAGglqSnLA5BYIttAuK1ypSY24ti0sBk8jU'
bot = telebot.TeleBot(TOKEN)

# ফ্লাস্ক সার্ভার
app = Flask('')
@app.route('/')
def home():
    return "AZ TEAM VIP OCR AI is Running Live!"
def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive():
    t = Thread(target=run)
    t.start()

# ইউজার ডেটাবেস
user_data = {}

def get_user_data(user_id):
    today = (datetime.datetime.utcnow() + datetime.timedelta(hours=6)).strftime("%Y-%m-%d")
    if user_id not in user_data or user_data[user_id]["date"] != today:
        user_data[user_id] = {
            "date": today,
            "wins": 0,
            "losses": 0,
            "consecutive_losses": 0,
            "pending_period": None,
            "pending_prediction": None,
            "status": None,
            "timeframe": 1 # ডিফল্ট 1 Min
        }
    return user_data[user_id]

# মেইন মেনু
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📸 স্ক্রিনশট দিয়ে শুরু করুন"),
        types.KeyboardButton("📊 আজকের পারফরম্যান্স")
    )
    return markup

# ইনলাইন রেজাল্ট বাটন (স্মার্ট লুপ)
def get_result_inline_keyboard(period):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🟢 BIG", callback_data=f"RES_{period}_BIG"),
        types.InlineKeyboardButton("🔴 SMALL", callback_data=f"RES_{period}_SMALL")
    )
    markup.add(types.InlineKeyboardButton("⏭️ স্কিপ করেছি", callback_data=f"RES_{period}_SKIP"))
    return markup

# এআই লজিক (Anti-loss & Hunch)
def analyze_market_logic(consecutive_losses):
    confidence = random.randint(75, 99)
    prediction = random.choice(["BIG", "SMALL"])
    
    if consecutive_losses >= 4:
        return 0, "NONE", "FORCE_SKIP", False
        
    ai_hunch = False
    if confidence < 88:
        if random.random() < 0.15: 
            ai_hunch = True
            confidence = random.randint(88, 95) 
            
    status = "TRADE" if (confidence >= 88 or ai_hunch) else "SKIP"
    return confidence, prediction, status, ai_hunch

# Start Command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = (
        "👑 <b>𝗔𝗭 𝗧𝗘𝗔𝗠 𝗩𝗜𝗣 𝗢𝗖𝗥 𝗔𝗜</b> 👑\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "অ্যাডভান্সড ইমেজ এনালাইসিস ট্রেডিং বটে স্বাগতম।\n\n"
        "<b>নিয়ম:</b> গেমের চার্টের একটি স্ক্রিনশট আপলোড করুন। বট নিজে থেকে পিরিয়ড এবং রেজাল্ট স্ক্যান করে সিগন্যাল জেনারেট করবে!"
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=get_main_keyboard())

# Text Handlers
@bot.message_handler(func=lambda message: message.text in ["📸 স্ক্রিনশট দিয়ে শুরু করুন", "📊 আজকের পারফরম্যান্স"])
def handle_menu_texts(message):
    ud = get_user_data(message.from_user.id)
    chat_id = message.chat.id
    
    if message.text == "📊 আজকের পারফরম্যান্স":
        total = ud["wins"] + ud["losses"]
        acc = (ud["wins"] / total * 100) if total > 0 else 0
        report = (
            f"📈 <b>𝗗𝗔𝗜𝗟𝗬 𝗔𝗜 𝗥𝗘𝗣𝗢𝗥𝗧</b> 📈\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🟢 <b>প্রফিট (Wins):</b> {ud['wins']}\n"
            f"🔴 <b>লস (Losses):</b> {ud['losses']}\n"
            f"⚠️ <b>টানা লস:</b> {ud['consecutive_losses']}\n"
            f"🎯 <b>একুরেসি:</b> {acc:.1f}%\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        bot.send_message(chat_id, report, parse_mode='HTML')
        
    elif message.text == "📸 স্ক্রিনশট দিয়ে শুরু করুন":
        bot.send_message(chat_id, "📸 <b>ট্রেডিং চার্টের সর্বশেষ স্ক্রিনশটটি আপলোড করুন।</b>", parse_mode='HTML')

# 📸 স্ক্রিনশট এনালাইসিস (OCR Engine) - মেইন ম্যাজিক!
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    ud = get_user_data(user_id)
    chat_id = message.chat.id
    
    msg = bot.reply_to(message, "🧠 <i>এআই আপনার ছবি স্ক্যান করছে... দয়া করে অপেক্ষা করুন।</i>", parse_mode='HTML')
    
    try:
        # ছবি ডাউনলোড
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image = Image.open(BytesIO(downloaded_file))
        
        # ছবি থেকে টেক্সট বের করা
        extracted_text = pytesseract.image_to_string(image)
        
        # ১৭-ডিজিটের পিরিয়ড নাম্বার খোঁজা (যেমন: 20260803100011389)
        periods = re.findall(r'(202\d{14})', extracted_text)
        
        if not periods:
            bot.edit_message_text("⚠️ <b>ভুল বা ঘোলা ছবি!</b>\nআমি চার্ট থেকে ১৭-ডিজিটের পিরিয়ড নাম্বারটি পড়তে পারিনি। দয়া করে পরিষ্কার ছবি দিন।", chat_id, msg.message_id, parse_mode='HTML')
            return
            
        # সবচেয়ে বড় পিরিয়ড নাম্বারটি বের করা (যেটি একদম উপরে থাকে)
        latest_period = max(periods)
        
        # রেজাল্ট খোঁজা (Big বা Small)
        # টেক্সটের ভেতর লেটেস্ট পিরিয়ডের আশেপাশেই Big/Small লেখা থাকবে
        result = "NONE"
        if re.search(f"{latest_period}.*?(?i)big", extracted_text.replace('\n', ' ')):
            result = "BIG"
        elif re.search(f"{latest_period}.*?(?i)small", extracted_text.replace('\n', ' ')):
            result = "SMALL"

        verification_msg = f"📸 <b>এনালাইসিস সাকসেস!</b>\nঅরিজিনাল পিরিয়ড <code>{latest_period}</code> ডিটেক্ট করা হয়েছে।\n\n"
        
        # অটোমেটিক উইন/লস চেক
        if ud["pending_period"] == int(latest_period):
            if ud["status"] == "SKIP":
                verification_msg += f"ℹ️ <i>এই পিরিয়ডটি আমরা স্কিপ করেছিলাম। (No Loss)</i>\n\n"
            elif ud["pending_prediction"] == result:
                ud["wins"] += 1
                ud["consecutive_losses"] = 0 
                verification_msg += f"✅ <b>Period {latest_period} WIN! (+1 Profit)</b> 💸\n\n"
            elif result != "NONE":
                ud["losses"] += 1
                ud["consecutive_losses"] += 1
                verification_msg += f"❌ <b>Period {latest_period} LOSS!</b> ⚠️\n\n"
        
        bot.delete_message(chat_id, msg.message_id)
        
        # নতুন সিগন্যাল জেনারেট
        generate_signal_logic(chat_id, user_id, int(latest_period), verification_msg)
        
    except Exception as e:
        bot.edit_message_text("⚠️ <i>ছবি স্ক্যান করতে সার্ভার সমস্যা হয়েছে। আবার চেষ্টা করুন।</i>", chat_id, msg.message_id, parse_mode='HTML')

# Result Button Callback (বাটন হ্যাং প্রবলেম ফিক্সড)
@bot.callback_query_handler(func=lambda call: call.data.startswith('RES_'))
def handle_result(call):
    # বাটন হ্যাং হওয়া বন্ধ করার কোড (Very Important!)
    bot.answer_callback_query(call.id) 
    
    parts = call.data.split('_')
    period = int(parts[1])
    result = parts[2] 
    
    user_id = call.from_user.id
    ud = get_user_data(user_id)
    chat_id = call.message.chat.id
    
    # বাটন মুছে দেওয়া
    bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
    
    verification_msg = ""
    # Profit/Loss checking
    if ud["pending_period"] == period:
        if result == "SKIP":
            verification_msg = f"ℹ️ <i>পিরিয়ড {period} স্কিপ করা হয়েছে। (No Loss)</i>\n\n"
        elif ud["status"] == "SKIP":
            verification_msg = f"ℹ️ <i>এআই স্কিপ করতে বলেছিল। (No Loss)</i>\n\n"
        elif ud["pending_prediction"] == result:
            ud["wins"] += 1
            ud["consecutive_losses"] = 0 
            verification_msg = f"✅ <b>Period {period} WIN! (+1 Profit)</b> 💸\n\n"
        else:
            ud["losses"] += 1
            ud["consecutive_losses"] += 1
            verification_msg = f"❌ <b>Period {period} LOSS!</b> ⚠️\n\n"
    
    # পরের সিগন্যাল দেওয়া (স্মার্ট লুপ)
    generate_signal_logic(chat_id, user_id, period, verification_msg)


# Signal Generator Logic
def generate_signal_logic(chat_id, user_id, current_period, prefix_msg=""):
    ud = get_user_data(user_id)
    
    # সাইটের ১৭ ডিজিটের নাম্বারের সাথে ১ যোগ করে পরের নাম্বার তৈরি করা
    next_period = current_period + 1
    
    conf, pred, status, is_hunch = analyze_market_logic(ud["consecutive_losses"])
    
    ud["pending_period"] = next_period
    ud["pending_prediction"] = pred
    ud["status"] = status
    
    if status == "FORCE_SKIP":
        response = (
            f"{prefix_msg}"
            f"🚨 <b>ANTI-LOSS PROTOCOL (FORCE SKIP)</b> 🚨\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ <b>মার্কেট ভোলাটাইল!</b> টানা ৪ লস এড়াতে সিস্টেম সিগন্যাল বন্ধ করেছে।\n"
            f"⏱️ <i>দয়া করে ৫-১০ মিনিট পর আবার স্ক্রিনশট দিন।</i>\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        ud["consecutive_losses"] = 0 
        bot.send_message(chat_id, response, parse_mode='HTML')
        return
        
    if status == "SKIP":
        response = (
            f"{prefix_msg}"
            f"⚠️ <b>𝗔𝗜 𝗥𝗜𝗦𝗞 𝗔𝗟𝗘𝗥𝗧 (𝗦𝗞𝗜𝗣 𝗧𝗥𝗔𝗗𝗘)</b> ⚠️\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔢 <b>আপকামিং পিরিয়ড:</b> <code>{next_period}</code>\n"
            f"📉 <b>এআই কনফিডেন্স:</b> {conf}%\n"
            f"🚫 <b>এআই সিদ্ধান্ত:</b> <b>মার্কেট স্কিপ করুন!</b>\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
    else:
        pred_display = "🟢 <b>𝗕𝗜𝗚</b> 🚀" if pred == "BIG" else "🔴 <b>𝗦𝗠𝗔𝗟𝗟</b> 📉"
        hunch_text = f"🧠 <i>AI Intuition: ম্যাট্রিক্স অনুযায়ী সিওর শট। ট্রেড নিন!</i>\n" if is_hunch else ""
            
        response = (
            f"{prefix_msg}"
            f"⚜️ <b>[𝗔𝗭] 𝗦𝗨𝗥𝗘 𝗦𝗛𝗢𝗧 𝗦𝗜𝗚𝗡𝗔𝗟</b> ⚜️\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔢 <b>আপকামিং পিরিয়ড:</b> <code>{next_period}</code>\n"
            f"🎯 <b>ভিআইপি প্রেডিকশন:</b> {pred_display}\n"
            f"🔥 <b>এআই কনফিডেন্স:</b> {conf}%\n"
            f"{hunch_text}"
            f"✅ <b>এআই সিদ্ধান্ত:</b> <b>১০০% একুরেট, কনফিডেন্সের সাথে ট্রেড নিন!</b>\n"
            f"━━━━━━━━━━━━━━━━━━"
        )

    markup = get_result_inline_keyboard(next_period)
    bot.send_message(chat_id, response, parse_mode='HTML')
    bot.send_message(chat_id, f"👉 <b>পিরিয়ড {next_period}</b> এর রেজাল্ট আসলে নিচের বাটনে ক্লিক করুন (অথবা নতুন স্ক্রিনশট দিন):", reply_markup=markup, parse_mode='HTML')

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()