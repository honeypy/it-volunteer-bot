from bs4 import BeautifulSoup
import requests
import sqlite3

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
            title = task.find('h4').text.strip()
            tags = []
            raw_tags = task.find('div', class_='task-tags').find_all('a')
            for tag in raw_tags:
                text_tag = tag.text
                tags.append(text_tag)
            tags = ','.join(tags)
            reward = task.find('span', class_='reward-name').text.strip()
            link = task.find('a', class_='ga-event-trigger').attrs['href'].strip()
        cursor.execute("SELECT rowid FROM tasks WHERE title = ?", (title,))
        data = cursor.fetchone()
        if not data:
            cursor.execute('''INSERT INTO tasks(title, tags, reward, link)VALUES(?,?,?,?)''', \
                           (title, tags, reward, link))
        db.commit()


db = sqlite3.connect('itvolunteer.db')
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