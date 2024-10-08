from flask import Flask, render_template, request, redirect, url_for
import redis

app = Flask(__name__)

# Настройка Redis
r = redis.Redis(host='redis', port=6379)

# Главная страница заработной платы
@app.route('/salary', methods=['GET', 'POST'])
def salary():
    if request.method == 'POST':
        company = request.form['company']
        salary = request.form['salary']
        r.hset('salaries', company, salary)
    salaries = r.hgetall('salaries')
    return render_template('salary.html', salaries=salaries)

# Страница обязательных расходов
@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if request.method == 'POST':
        expense_name = request.form['expense_name']
        expense_amount = request.form['expense_amount']
        r.hset('expenses', expense_name, expense_amount)
    expenses = r.hgetall('expenses')
    return render_template('expenses.html', expenses=expenses)

# Страница для ввода данных
@app.route('/enter_data', methods=['GET', 'POST'])
def enter_data():
    if request.method == 'POST':
        amount = request.form['amount']
        type_ = request.form['type']
        comment = request.form['comment']
        if type_ == 'income':
            r.lpush('accounting', f'Debet: {amount} | Комментарий: {comment}')
        elif type_ == 'expense':
            r.lpush('accounting', f'Кредит: {amount} | Комментарий: {comment}')
    return render_template('enter_data.html')

# Страница таблицы учёта
@app.route('/')
def accounting():
    records = r.lrange('accounting', 0, -1)
    return render_template('accounting.html', records=records)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
