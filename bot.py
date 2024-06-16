import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.error import BadRequest, TelegramError

TOKEN = '7125482530:AAFjCk9OKKoL5pSg0JSZm8UyQAPEXgPJqJk'
channel_link = 'https://t.me/dodjfocckdncjk'  # استخدم رابط القناة هنا

# إنشاء قاعدة البيانات والجداول إذا لم تكن موجودة
def create_db():
    conn = sqlite3.connect('votes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS votes
                 (message_id INTEGER, user_id INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (message_id INTEGER PRIMARY KEY, message_text TEXT)''')
    conn.commit()
    conn.close()

create_db()

def start(update, context):
    chat_id = update.message.chat_id  # الحصول على معرف الشات الحالي
    context.bot_data["admin_chat_id"] = chat_id  # تخزين معرف الشات في bot_data
    update.message.reply_text("تم تعيين شات الإدارة بنجاح!")

def forward_message(update, context):
    message_text = update.message.text
    message_id = update.message.message_id
    buttons = [
        [InlineKeyboardButton("❤️ 0", callback_data=f'vote_{message_id}_0')]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        if channel_link.startswith("https://t.me/"):
            channel_id = channel_link.replace("https://t.me/", "@")
        else:
            channel_id = channel_link

        context.bot.send_message(chat_id=channel_id, text=message_text, reply_markup=reply_markup)
        
        # تخزين نص الرسالة في قاعدة البيانات
        conn = sqlite3.connect('votes.db')
        c = conn.cursor()
        c.execute('INSERT INTO messages (message_id, message_text) VALUES (?, ?)', (message_id, message_text))
        conn.commit()
        conn.close()
    except BadRequest as e:
        update.message.reply_text(f"حدث خطأ: {e.message}")
        print(f"BadRequest: {e.message}")
    except TelegramError as e:
        update.message.reply_text(f"حدث خطأ: {e.message}")
        print(f"TelegramError: {e.message}")

def check_subscription(user_id, bot):
    try:
        if channel_link.startswith("https://t.me/"):
            channel_id = channel_link.replace("https://t.me/", "@")
        else:
            channel_id = channel_link

        chat_member = bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except TelegramError as e:
        print(f"Error checking subscription: {e.message}")
        return False

def button_click(update, context):
    query = update.callback_query
    user = query.from_user
    user_id = user.id
    message_id, current_votes = map(int, query.data.split('_')[1:3])

    # تحقق من اشتراك المستخدم في القناة
    if not check_subscription(user_id, context.bot):
        try:
            query.answer(text="عليك الاشتراك في القناة للتصويت.", show_alert=True)
        except BadRequest as e:
            print(f"BadRequest on answering query: {e.message}")
        return

    # الحصول على عدد التصويتات الحالي
    new_votes = current_votes

    conn = sqlite3.connect('votes.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM votes WHERE message_id=? AND user_id=?', (message_id, user_id))
    vote = c.fetchone()

    if vote:
        # المستخدم قام بالفعل بالتصويت، قم بإلغاء تصويته
        c.execute('DELETE FROM votes WHERE message_id=? AND user_id=?', (message_id, user_id))
        conn.commit()
        new_votes = current_votes - 1
    else:
        # المستخدم لم يصوت بعد، قم بإضافة تصويته
        c.execute('INSERT INTO votes (message_id, user_id) VALUES (?, ?)', (message_id, user_id))
        conn.commit()
        new_votes = current_votes + 1
    
    # استرجاع نص الرسالة الأصلي
    c.execute('SELECT message_text FROM messages WHERE message_id=?', (message_id,))
    message_text = c.fetchone()
    message_text = message_text[0] if message_text else "رسالة غير معروفة"

    conn.close()
    
    # إرسال معلومات المستخدم إلى شات الإدارة
    admin_chat_id = context.bot_data.get("admin_chat_id")
    if admin_chat_id:
        context.bot.send_message(chat_id=admin_chat_id, text=f"المتسابق : {message_text}\n\nلديه تصويت جديد 👇\n\nالإسم الكامل : {user.full_name}\nاليوزر : @{user.username}\nالمعرف : {user.id}\nإجمالي التصويتات : {new_votes}")

    new_button = InlineKeyboardButton(f"❤️ {new_votes}", callback_data=f'vote_{message_id}_{new_votes}')
    try:
        query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([[new_button]]))
        query.answer()
    except BadRequest as e:
        print(f"BadRequest on editing message: {e.message}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_message))
    dp.add_handler(CallbackQueryHandler(button_click))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()