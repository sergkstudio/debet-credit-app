from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Подключение БД
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

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

with app.app_context():
    init_db()

# Главная страница с добавлением данных и отображением таблиц
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    
    # Если запрос POST, обрабатываем добавление записи
    if request.method == 'POST':
        table = request.form['table']
        size = request.form['size']
        comment = request.form['comment']
        
        if table == 'salary':
            conn.execute('INSERT INTO salary (size, comment) VALUES (?, ?)', (size, comment))
        elif table == 'obligatory_expenses':
            conn.execute('INSERT INTO obligatory_expenses (size, comment) VALUES (?, ?)', (size, comment))
        elif table == 'income_expenses':
            conn.execute('INSERT INTO income_expenses (size, comment) VALUES (?, ?)', (size, comment))
        
        conn.commit()
        conn.close()

        # Перенаправляем после POST-запроса
        return redirect(url_for('index'))

    # Удаление записи
    if request.method == 'POST' and 'delete_id' in request.form:
        table = request.form['delete_table']
        delete_id = request.form['delete_id']
        
        if table == 'salary':
            conn.execute('DELETE FROM salary WHERE id = ?', (delete_id,))
        elif table == 'obligatory_expenses':
            conn.execute('DELETE FROM obligatory_expenses WHERE id = ?', (delete_id,))
        elif table == 'income_expenses':
            conn.execute('DELETE FROM income_expenses WHERE id = ?', (delete_id,))
        
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    # Получаем записи из всех таблиц
    salary = conn.execute('SELECT * FROM salary').fetchall()
    obligatory_expenses = conn.execute('SELECT * FROM obligatory_expenses').fetchall()
    income_expenses = conn.execute('SELECT * FROM income_expenses').fetchall()
    conn.close()

    return render_template('index.html', salary=salary, obligatory_expenses=obligatory_expenses, income_expenses=income_expenses)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
