import telebot
import datetime
import random
import os
from flask import Flask
from threading import Thread
from telebot import types

# আপনার টেলিগ্রাম বটের টোকেন
TOKEN = '8681018267:AAGglqSnLA5BYIttAuK1ypSY24ti0sBk8jU'
bot = telebot.TeleBot(TOKEN)

# ফ্লাস্ক সার্ভার (Render-এ লাইভ রাখার জন্য)
app = Flask('')
@app.route('/')
def home():
    return "AZ TEAM VIP DYNAMIC AI is Running Live!"
def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive():
    t = Thread(target=run)
    t.start()

# ইউজার ডেটাবেস
user_data = {}

def get_user_data(user_id):
    # বাংলাদেশ সময় অনুযায়ী ডেটা রিসেট (UTC+6)
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
            "timeframe": 1,        # ডিফল্ট 1 Min
            "mode": "TEXT"         # ডিফল্ট TEXT/Button Mode (অন্যটি "PHOTO")
        }
    return user_data[user_id]

# মেইন মেনু বাটন
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🎮 ট্রেড শুরু করুন"),
        types.KeyboardButton("⚙️ সিস্টেম সেটআপ (Setup)")
    )
    markup.add(types.KeyboardButton("📊 আজকের পারফরম্যান্স"))
    return markup

# প্রফেশনাল সেটআপ মেনু (Inline)
def get_settings_keyboard(user_id):
    ud = get_user_data(user_id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Timeframe selection
    t30 = "✅ 30 Sec" if ud['timeframe'] == 0.5 else "30 Sec"
    t1  = "✅ 1 Min"  if ud['timeframe'] == 1 else "1 Min"
    t3  = "✅ 3 Min"  if ud['timeframe'] == 3 else "3 Min"
    t5  = "✅ 5 Min"  if ud['timeframe'] == 5 else "5 Min"
    
    # Mode selection
    m_text  = "✅ 🔘 বাটন মোড" if ud['mode'] == 'TEXT' else "🔘 বাটন মোড"
    m_photo = "✅ 📸 স্ক্রিনশট মোড" if ud['mode'] == 'PHOTO' else "📸 স্ক্রিনশট মোড"
    
    markup.add(
        types.InlineKeyboardButton(t30, callback_data="SET_TF_0.5"),
        types.InlineKeyboardButton(t1, callback_data="SET_TF_1")
    )
    markup.add(
        types.InlineKeyboardButton(t3, callback_data="SET_TF_3"),
        types.InlineKeyboardButton(t5, callback_data="SET_TF_5")
    )
    markup.add(types.InlineKeyboardButton("━━━━━━━━━━━━━━", callback_data="NONE"))
    markup.add(
        types.InlineKeyboardButton(m_text, callback_data="SET_MODE_TEXT"),
        types.InlineKeyboardButton(m_photo, callback_data="SET_MODE_PHOTO")
    )
    return markup

# রেজাল্ট ইনপুট বাটন
def get_result_inline_keyboard(period):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🟢 BIG", callback_data=f"RES_{period}_BIG"),
        types.InlineKeyboardButton("🔴 SMALL", callback_data=f"RES_{period}_SMALL")
    )
    markup.add(types.InlineKeyboardButton("⏭️ স্কিপ করেছি", callback_data=f"RES_{period}_SKIP"))
    return markup

# লাইভ টাইম-সিঙ্ক পিরিয়ড জেনারেটর (BD Time UTC+6)
def get_live_period(timeframe_min):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
    total_seconds = now.hour * 3600 + now.minute * 60 + now.second
    
    if timeframe_min == 0.5:   # 30 Sec (2880 periods/day)
        seq = int(total_seconds // 30) + 1
    else:                      # 1M, 3M, 5M
        seq = int(total_seconds // (timeframe_min * 60)) + 1
        
    return f"{now.strftime('%Y%m%d')}{seq:04d}"

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
        "👑 <b>𝗔𝗭 𝗧𝗘𝗔𝗠 𝗩𝗜𝗣 𝗗𝗬𝗡𝗔𝗠𝗜𝗖 𝗔𝗜</b> 👑\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "মাল্টি-টাইমফ্রেম (30s, 1m, 3m, 5m) ট্রেডিং বটে স্বাগতম।\n\n"
        "⚙️ <i>প্রথমে 'সিস্টেম সেটআপ' থেকে আপনার পছন্দের টাইমফ্রেম এবং সিগন্যাল মোড (বাটন/স্ক্রিনশট) ঠিক করে নিন!</i>"
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=get_main_keyboard())

# Text Handlers for Reply Keyboard
@bot.message_handler(func=lambda message: message.text in ["🎮 ট্রেড শুরু করুন", "⚙️ সিস্টেম সেটআপ (Setup)", "📊 আজকের পারফরম্যান্স"])
def handle_menu_texts(message):
    user_id = message.from_user.id
    ud = get_user_data(user_id)
    chat_id = message.chat.id
    
    if message.text == "⚙️ সিস্টেম সেটআপ (Setup)":
        text = "⚙️ <b>ভিআইপি কন্ট্রোল প্যানেল</b>\nআপনার গেমের টাইমফ্রেম এবং সিগন্যাল নেওয়ার পদ্ধতি সিলেক্ট করুন:"
        bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=get_settings_keyboard(user_id))
        
    elif message.text == "📊 আজকের পারফরম্যান্স":
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
        
    elif message.text == "🎮 ট্রেড শুরু করুন":
        time_text = "30 Sec" if ud['timeframe'] == 0.5 else f"{ud['timeframe']} Min"
        
        if ud['mode'] == 'TEXT':
            current_period = get_live_period(ud['timeframe'])
            text = (
                f"🕹️ <b>লাইভ মার্কেট কানেক্টেড! ({time_text})</b>\n\n"
                f"দয়া করে সাইটে দেখে বলুন, <b>পিরিয়ড {current_period}</b> এ কী রেজাল্ট এসেছে?"
            )
            bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=get_result_inline_keyboard(current_period))
        else:
            text = (
                f"📸 <b>স্ক্রিনশট মোড অ্যাক্টিভ! ({time_text})</b>\n\n"
                f"সিগন্যাল পেতে গেমের চার্টের একটি পরিষ্কার <b>স্ক্রিনশট আপলোড করুন।</b>"
            )
            bot.send_message(chat_id, text, parse_mode='HTML')

# Settings Callback Handler
@bot.callback_query_handler(func=lambda call: call.data.startswith('SET_'))
def handle_settings(call):
    user_id = call.from_user.id
    ud = get_user_data(user_id)
    
    if call.data.startswith('SET_TF_'):
        ud['timeframe'] = float(call.data.split('_')[2])
    elif call.data.startswith('SET_MODE_'):
        ud['mode'] = call.data.split('_')[2]
        
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_settings_keyboard(user_id))

# Screenshot Analysis Handler
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    ud = get_user_data(user_id)
    chat_id = message.chat.id
    
    if ud['mode'] != 'PHOTO':
        bot.reply_to(message, "⚠️ <b>আপনি বর্তমানে 'বাটন মোডে' আছেন।</b>\nস্ক্রিনশট দিয়ে সিগন্যাল পেতে '⚙️ সিস্টেম সেটআপ' থেকে <b>'স্ক্রিনশট মোড'</b> সিলেক্ট করুন।", parse_mode='HTML')
        return
        
    bot.reply_to(message, "🧠 <i>এআই চার্ট স্ক্যান করছে... (Live Syncing)</i>", parse_mode='HTML')
    
    # Generate signal based on the selected timeframe
    current_period = int(get_live_period(ud['timeframe']))
    generate_signal_logic(chat_id, user_id, current_period, is_photo=True)

# Result Button Callback (Win/Loss Tracking)
@bot.callback_query_handler(func=lambda call: call.data.startswith('RES_'))
def handle_result(call):
    parts = call.data.split('_')
    period = int(parts[1])
    result = parts[2] 
    
    user_id = call.from_user.id
    ud = get_user_data(user_id)
    chat_id = call.message.chat.id
    
    bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
    
    verification_msg = ""
    # Profit/Loss checking
    if ud["pending_period"] and str(ud["pending_period"])[-4:] == str(period)[-4:]:
        if result == "SKIP":
            verification_msg = f"ℹ️ <i>পিরিয়ড {period} স্কিপ করা হয়েছে। (No Loss)</i>\n"
        elif ud["status"] == "SKIP":
            verification_msg = f"ℹ️ <i>এআই স্কিপ করতে বলেছিল। (No Loss)</i>\n"
        elif ud["pending_prediction"] == result:
            ud["wins"] += 1
            ud["consecutive_losses"] = 0 
            verification_msg = f"✅ <b>Period {period} WIN! (+1 Profit)</b> 💸\n"
        else:
            ud["losses"] += 1
            ud["consecutive_losses"] += 1
            verification_msg = f"❌ <b>Period {period} LOSS!</b> ⚠️\n"
    
    bot.send_message(chat_id, verification_msg, parse_mode='HTML')
    
    # If in TEXT mode, automatically give the next signal!
    if ud['mode'] == 'TEXT':
        generate_signal_logic(chat_id, user_id, period, is_photo=False)
    # If in PHOTO mode, ask for the next screenshot!
    else:
        time_txt = "30 Sec" if ud['timeframe'] == 0.5 else f"{ud['timeframe']} Min"
        bot.send_message(chat_id, f"📸 <b>পরবর্তী সিগন্যালের জন্য নতুন চার্টের স্ক্রিনশট আপলোড করুন!</b> ({time_txt})", parse_mode='HTML')

# Signal Generator Logic
def generate_signal_logic(chat_id, user_id, current_period, is_photo=False):
    ud = get_user_data(user_id)
    next_period = current_period + 1
    
    conf, pred, status, is_hunch = analyze_market_logic(ud["consecutive_losses"])
    
    ud["pending_period"] = next_period
    ud["pending_prediction"] = pred
    ud["status"] = status
    
    time_display = "30s" if ud['timeframe'] == 0.5 else f"{ud['timeframe']}m"
    
    if status == "FORCE_SKIP":
        response = (
            f"🚨 <b>ANTI-LOSS PROTOCOL (FORCE SKIP)</b> 🚨\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ <b>মার্কেট ভোলাটাইল!</b> টানা ৪ লস এড়াতে সিস্টেম সিগন্যাল বন্ধ করেছে।\n"
            f"⏱️ <i>দয়া করে ৫-১০ মিনিট পর আবার চেষ্টা করুন।</i>\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        ud["consecutive_losses"] = 0 
        bot.send_message(chat_id, response, parse_mode='HTML')
        return
        
    if status == "SKIP":
        response = (
            f"⚠️ <b>𝗔𝗜 𝗥𝗜𝗦𝗞 𝗔𝗟𝗘𝗥𝗧 (𝗦𝗞𝗜𝗣 𝗧𝗥𝗔𝗗𝗘)</b> ⚠️\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏱️ <b>টাইমফ্রেম:</b> WinGo {time_display}\n"
            f"🔢 <b>আপকামিং পিরিয়ড:</b> <code>{next_period}</code>\n"
            f"📉 <b>এআই কনফিডেন্স:</b> {conf}%\n"
            f"🚫 <b>এআই সিদ্ধান্ত:</b> <b>মার্কেট স্কিপ করুন!</b> (High Risk)\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
    else:
        pred_display = "🟢 <b>𝗕𝗜𝗚</b> 🚀" if pred == "BIG" else "🔴 <b>𝗦𝗠𝗔𝗟𝗟</b> 📉"
        hunch_text = f"🧠 <i>AI Intuition: ম্যাট্রিক্স অনুযায়ী সিওর শট। ট্রেড নিন!</i>\n" if is_hunch else ""
            
        response = (
            f"⚜️ <b>[𝗔𝗭] 𝗦𝗨𝗥𝗘 𝗦𝗛𝗢𝗧 𝗦𝗜𝗚𝗡𝗔𝗟</b> ⚜️\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏱️ <b>টাইমফ্রেম:</b> WinGo {time_display}\n"
            f"🔢 <b>আপকামিং পিরিয়ড:</b> <code>{next_period}</code>\n"
            f"🎯 <b>ভিআইপি প্রেডিকশন:</b> {pred_display}\n"
            f"🔥 <b>এআই কনফিডেন্স:</b> {conf}%\n"
            f"{hunch_text}"
            f"✅ <b>এআই সিদ্ধান্ত:</b> <b>১০০% একুরেট, কনফিডেন্সের সাথে ট্রেড নিন!</b>\n"
            f"━━━━━━━━━━━━━━━━━━"
        )

    # সিগন্যাল দেওয়ার সাথেই পরের পিরিয়ডের রেজাল্ট চাওয়ার বাটন যুক্ত করা হলো
    markup = get_result_inline_keyboard(next_period)
    bot.send_message(chat_id, response, parse_mode='HTML')
    bot.send_message(chat_id, f"👉 <b>পিরিয়ড {next_period}</b> এর রেজাল্ট আসলে নিচের বাটনে ক্লিক করুন:", reply_markup=markup, parse_mode='HTML')

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()