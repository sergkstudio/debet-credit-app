import logging
from flask import Flask, render_template, request, redirect, url_for
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
    # Создаем таблицу для заработной платы
    conn.execute('''
        CREATE TABLE IF NOT EXISTS salary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            size REAL NOT NULL,
            comment TEXT
        )
    ''')
    
    # Создаем таблицу для обязательных расходов
    conn.execute('''
        CREATE TABLE IF NOT EXISTS obligatory_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            size REAL NOT NULL,
            comment TEXT
        )
    ''')

    # Создаем таблицу для прихода/расхода
    conn.execute('''
        CREATE TABLE IF NOT EXISTS income_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            size REAL NOT NULL,
            comment TEXT
        )
    ''')
    conn.close()

# Инициализация БД при старте приложения
with app.app_context():
    init_db()

# Главная страница
@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/<int:post_id>')
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    return render_template('post.html', post=post)

# Страница для добавления новых данных
@app.route('/new', methods=['GET', 'POST'])
def new_entry():
    if request.method == 'POST':
        # Получаем данные из формы
        table = request.form['table']
        size = request.form['size']
        comment = request.form['comment']

        # Вставляем данные в нужную таблицу
        conn = get_db_connection()
        if table == 'salary':
            conn.execute('INSERT INTO salary (size, comment) VALUES (?, ?)', (size, comment))
        elif table == 'obligatory_expenses':
            conn.execute('INSERT INTO obligatory_expenses (size, comment) VALUES (?, ?)')
        elif table == 'income_expenses':
            conn.execute('INSERT INTO income_expenses (size, comment) VALUES (?, ?)')
        
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('new.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
