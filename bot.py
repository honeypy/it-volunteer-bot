from telegram.ext import Updater, Job
import logging
import config
import sqlite3

telegram_token = config.telegram_token
channel = config.channel
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
updater = Updater(telegram_token)
jobber = updater.job_queue

db = sqlite3.connect('itvolunteer.db', check_same_thread=False)
cursor = db.cursor()

def post(bot, job):
    cursor.execute('SELECT * FROM tasks WHERE published=0')
    tasks_to_post = cursor.fetchall()
    for task in tasks_to_post:
        text = make_text(task)
        bot.sendMessage(chat_id=channel, text=text, parse_mode='HTML')
        cursor.execute('UPDATE tasks SET published=(1) WHERE (link)=(?)', (task[-2],))
        db.commit()

    cursor.execute('SELECT * FROM news WHERE published=0')
    news_to_post = cursor.fetchall()
    for n in news_to_post:
        link = n[1]
        bot.sendMessage(chat_id=channel, text=link, parse_mode='HTML')
        cursor.execute('UPDATE news SET published=(1) WHERE (link)=(?)', (link,))
        db.commit()


def make_text(task):
    title_text ='<b>'+ "\U0001F449Новое задание: " + '</b>'
    title = task[1]+'\n'
    tags_text = '<b>'+ "\U00002B50Теги: " + '</b>'
    tags = task[2]+'\n'
    reward_text = '<b>'+ "\U0001F576Вознаграждение: " + '</b>'
    reward = task[3]+'\n'
    more_text = '<b>'+ "\U0001F4C4Подробности: " + '</b>'
    more = task[4]+'\n\n'
    text = title_text+title+tags_text+tags+reward_text+reward+more_text+more
    return text

job_post = Job(post, 10.0)
jobber.put(job_post, next_t=0.0)

if __name__ == '__main__':
    # updater.start_polling()
    # updater.idle()
    updater.start_webhook(listen='127.0.0.1', port=5001, url_path=telegram_token)
    updater.bot.setWebhook(webhook_url='https://95.85.37.72/' + telegram_token, certificate=open('cert.pem', 'rb'))
    #print('go')