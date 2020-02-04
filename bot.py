from telegram.ext import Updater, CommandHandler
import telegram.ext
import logging
import config
import sqlite3
import os.path


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "itvolunteer.db")

telegram_token = config.telegram_token
channel = config.test_channel
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

updater = Updater(telegram_token, use_context= True)
dispatcher = updater.dispatcher
jobber = updater.job_queue

db = sqlite3.connect(db_path, check_same_thread=False)
cursor = db.cursor()

def post(context: telegram.ext.CallbackContext):
    cursor.execute('SELECT * FROM tasks WHERE published=0')
    tasks_to_post = cursor.fetchall()
    for task in tasks_to_post:
        text = make_text(task)
        context.bot.sendMessage(chat_id=channel, text=text, parse_mode='HTML', disable_web_page_preview=True)
        cursor.execute('UPDATE tasks SET published=(1) WHERE (link)=(?)', (task[-2],))
        db.commit()

    cursor.execute('SELECT * FROM news WHERE published=0')
    news_to_post = cursor.fetchall()
    for n in news_to_post:
        link = n[1]
        context.bot.sendMessage(chat_id=channel, text=link, parse_mode='HTML')
        cursor.execute('UPDATE news SET published=(1) WHERE (link)=(?)', (link,))
        db.commit()


def make_text(task):
    title_text ='<b>'+ "\U0001F449 Новое задание: " + '</b>'
    title = task[1]+'\n'
    tags_text = '<b>'+ "\U00002B50 Теги: " + '</b>'
    tags = task[2]+'\n'
    reward_text = '<b>'+ "\U0001F576 Вознаграждение: " + '</b>'
    reward = task[3]+'\n'
    more_text = '<b>'+ "\U0001F4C4 Подробности: " + '</b>'
    url_more = task[4].replace('https://', '')
    more = url_more + '\n\n'
    text = title_text+title+tags_text+tags+reward_text+reward+more_text+more
    return text

def start(update, context):
    context.bot.sendMessage(text='Бот запущен.', chat_id=update.message.chat.id)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


job_post = jobber.run_repeating(post, interval=60, first=0)



if __name__ == '__main__':
    updater.start_polling()
    print('go')
    #updater.idle()
    # updater.start_webhook(listen='127.0.0.1', port=5001, url_path=telegram_token)
    # updater.bot.setWebhook(webhook_url='https://95.85.37.72/' + telegram_token, certificate=open('cert.pem', 'rb'))
