import telebot
from telebot import types
import random
import string

# --- CONFIGURATION ---
TOKEN = "8790029537:AAED3fNftbEAEMilUa2syszh3lP1jtZeIPg"
ADMIN_PASSWORD = "RODRI RODRI2019"
SUPPORT_USER = "@FUIP_2017"

bot = telebot.TeleBot(TOKEN)

# Databases
authorized_users = set()
user_balances = {}
users_db = {} # {chat_id: password}

# --- HELPERS ---
def generate_key(duration):
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    return f"WINDR-{duration}-{random_str}"

# --- KEYBOARDS ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("🛍️ Buy keys"), types.KeyboardButton("👤 Account"))
    markup.add(types.KeyboardButton("🚀 Log out"), types.KeyboardButton("🛠️ Manage"))
    markup.add(types.KeyboardButton("📦 Stock"), types.KeyboardButton("🎧 Support"))
    return markup

def manage_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ Add Account", callback_data="add_acc"))
    markup.add(types.InlineKeyboardButton("💰 Set Balance", callback_data="set_bal"))
    return markup

# --- HANDLERS ---

@bot.message_handler(commands=['start'])
def welcome(message):
    if message.chat.id not in user_balances:
        user_balances[message.chat.id] = 10000000.0 # Your initial balance
    
    if message.chat.id in authorized_users:
        bot.send_message(message.chat.id, "Welcome back!", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "🔐 Enter PASSWORD:")

@bot.message_handler(func=lambda message: message.chat.id not in authorized_users)
def handle_login(message):
    if message.text == ADMIN_PASSWORD or message.text == users_db.get(message.chat.id):
        authorized_users.add(message.chat.id)
        bot.send_message(message.chat.id, "✅ Authorized!", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "❌ Access Denied.")

@bot.message_handler(func=lambda message: message.text == "🛍️ Buy keys")
def buy_windr_main(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("BUY WINDR", callback_data="show_plans"))
    bot.send_message(message.chat.id, "Product:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "👤 Account")
def account_info(message):
    bal = user_balances.get(message.chat.id, 0)
    bot.send_message(message.chat.id, f"👤 User: {message.from_user.first_name}\n💰 Balance: {bal:,}$")

@bot.message_handler(func=lambda message: message.text == "🛠️ Manage")
def show_manage(message):
    bot.send_message(message.chat.id, "Admin Panel:", reply_markup=manage_menu())

@bot.message_handler(func=lambda message: message.text == "🎧 Support")
def support(message):
    bot.send_message(message.chat.id, f"Support: {SUPPORT_USER}")

# --- CALLBACKS ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    if call.data == "show_plans":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("1 DAY - 3$", callback_data="buy_1d"))
        markup.add(types.InlineKeyboardButton("7 DAYS - 6$", callback_data="buy_7d"))
        markup.add(types.InlineKeyboardButton("30 DAYS - 10$", callback_data="buy_30d"))
        bot.edit_message_text("Choose your plan:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("buy_"):
        plans = {"buy_1d": [3, "DAY"], "buy_7d": [6, "WEEK"], "buy_30d": [10, "MONTH"]}
        cost, dur = plans[call.data]
        
        if user_balances.get(chat_id, 0) >= cost:
            user_balances[chat_id] -= cost
            key = generate_key(dur)
            bot.send_message(chat_id, f"✅ Success!\n🔑 Key: `{key}`\n💰 Remaining: {user_balances[chat_id]}$", parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "❌ Not enough balance!")

    elif call.data == "add_acc":
        bot.send_message(chat_id, "Use: /add [ID] [PASS] [BAL]")

    elif call.data == "set_bal":
        bot.send_message(chat_id, "Use: /setbal [ID] [AMOUNT]")

# --- ADMIN FUNCTIONS ---
@bot.message_handler(commands=['add'])
def add_user(message):
    try:
        _, uid, pwd, bal = message.text.split()
        uid = int(uid)
        users_db[uid] = pwd
        user_balances[uid] = float(bal)
        bot.send_message(message.chat.id, f"✅ User {uid} added.")
    except:
        bot.send_message(message.chat.id, "Format: /add 12345 pass 100")

@bot.message_handler(commands=['setbal'])
def set_balance(message):
    try:
        _, uid, bal = message.text.split()
        user_balances[int(uid)] = float(bal)
        bot.send_message(message.chat.id, "✅ Balance updated.")
    except:
        bot.send_message(message.chat.id, "Format: /setbal 12345 500")

if __name__ == "__main__":
    bot.infinity_polling()
