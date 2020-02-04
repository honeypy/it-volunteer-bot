from bs4 import BeautifulSoup
import requests
import sqlite3
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "itvolunteer.db")


def scrape_news(soup_news):
    for soup in soup_news:
        link = soup.find('a').attrs['href'].strip()
        cursor.execute("SELECT rowid FROM news WHERE link = ?", (link,))
        data = cursor.fetchone()
        if not data:
            cursor.execute('''INSERT INTO news (link) VALUES(?)''', (link,))
        db.commit()

def scrape(raw_tasks):
    raw_tasks.reverse()
    for task in raw_tasks:
        if task.find('h2') == None:
            title_raw = task.find('h4').text.strip()
            title = title_raw[0].lower() + title_raw[1:]
            tags = []
            raw_tags = task.find('div', class_='task-tags').find_all('a')
            for tag in raw_tags:
                text_tag = tag.text.lower()
                tags.append(text_tag)
            tags = ', '.join(tags)
            raw_reward = task.find('span', class_='reward-name').text.strip()
            reward = raw_reward[0].lower() + raw_reward[1:]
            link = task.find('a', class_='ga-event-trigger').attrs['href'].strip()
        cursor.execute("SELECT rowid FROM tasks WHERE title = ?", (title,))
        data = cursor.fetchone()
        if not data:
            cursor.execute('''INSERT INTO tasks(title, tags, reward, link)VALUES(?,?,?,?)''', \
                           (title, tags, reward, link))
        db.commit()


db = sqlite3.connect(db_path, check_same_thread=False)
cursor = db.cursor()

# getting soup of posts
URL = 'https://itv.te-st.ru/'
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")
raw_tasks = soup.find_all('div', class_='border-card')

# getting soup of news
URL_news = 'https://itv.te-st.ru/news/'
response_news = requests.get(URL_news)
soup_news = BeautifulSoup(response_news.text, "html.parser")
soup_news = soup_news.find_all('h4')

scrape(raw_tasks)
scrape_news(soup_news)
db.close()