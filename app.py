import logging
from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Подключение БД
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def close_db_connection(conn):
    conn.close()

# Инициализация БД
def init_db():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL)')
    conn.close()

# Инициализация БД при старте приложения
with app.app_context():
    init_db()

# Главная страница
@app.route('/')
def index():
    conn = get_db_connection()
    conn.execute('INSERT INTO posts (title, content) VALUES ("Why I love Flask", "This is so cool!!!")')
    conn.execute('INSERT INTO posts (title, content) VALUES ("Cats >> Dogs", "It was a joke because they are all so adorable.")')
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/<int:post_id>')
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    return render_template('post.html', post=post)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
