from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Подключение БД
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Инициализация БД
def init_db():
    conn = get_db_connection()
    
    # Создаем таблицы
    conn.execute('''
        CREATE TABLE IF NOT EXISTS salary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            size REAL NOT NULL,
            comment TEXT,
            month TEXT NOT NULL
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS obligatory_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            size REAL NOT NULL,
            comment TEXT,
            month TEXT NOT NULL
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS income_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            size REAL NOT NULL,
            comment TEXT,
            current_time TEXT NOT NULL,
            month TEXT NOT NULL
        )
    ''')
    
    conn.close()

# Главная страница с добавлением и удалением данных
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    
    # Добавление записи
    if request.method == 'POST' and 'table' in request.form:
        table = request.form['table']
        size = request.form['size']
        comment = request.form['comment']
        month = datetime.now().strftime('%Y-%m')  # Текущий месяц в формате YYYY-MM

        
        if table == 'salary':
            conn.execute('INSERT INTO salary (size, comment, month) VALUES (?, ?, ?)', (size, comment, month))
        elif table == 'obligatory_expenses':
            conn.execute('INSERT INTO obligatory_expenses (size, comment, month) VALUES (?, ?, ?)', (size, comment, month))
        elif table == 'income_expenses':
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn.execute('INSERT INTO income_expenses (size, comment, current_time, month) VALUES (?, ?, ?, ?)', 
                         (size, comment, current_time, month))
        
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
        # Перенаправляем после POST-запроса
        return redirect(url_for('index'))

    # Получаем записи из всех таблиц
    salary = conn.execute('SELECT * FROM salary').fetchall()
    obligatory_expenses = conn.execute('SELECT * FROM obligatory_expenses').fetchall()
    income_expenses = conn.execute('SELECT * FROM income_expenses').fetchall()

    # Получение данных за каждый месяц
    salary_month = conn.execute('SELECT * FROM salary ORDER BY month').fetchall()
    obligatory_expenses_month = conn.execute('SELECT * FROM obligatory_expenses ORDER BY month').fetchall()
    income_expenses_month = conn.execute('SELECT * FROM income_expenses ORDER BY month').fetchall()

    # Группируем данные по месяцам
    months = list(set([row['month'] for row in salary_month + obligatory_expenses_month + income_expenses_month]))
    
    month_data = {}
    for month in months:
        month_data[month] = {
            'salary_total': sum(row['size'] for row in salary),
            'expense_total': sum(row['size'] for row in obligatory_expenses_month if row['month'] == month),
            'operations': [row for row in income_expenses_month if row['month'] == month]
        }

    # Вычисляем общие суммы для зарплаты и расходов
    salary_total = sum([row['size'] for row in salary])
    expense_total = sum([row['size'] for row in obligatory_expenses])
   
    # Подготовка данных для передачи в шаблон
    expense_data = {}

    for expense in expense_data:
        expense_data[expense] = {
            'salary_total': sum(row['size'] for row in salary),
            'expense_total': sum(row['size'] for row in obligatory_expenses_month if row['month'] == month),
            'current_time': (row['current_time'] for row in income_expenses),
            'credit': (row['size'] for row in income_expenses),
            'comment': (row['comment'] for row in income_expenses)
        }

    
    conn.close()

    return render_template('index.html', month_data=month_data, expense_data=expense_data, salary=salary, income_expenses=income_expenses, obligatory_expenses=obligatory_expenses)
if __name__ == '__main__':
    init_db()  # Инициализация базы данных перед запуском приложения
    app.run(host='0.0.0.0')
