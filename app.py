from flask import Flask, render_template, request, redirect, url_for
import redis

app = Flask(__name__)

# Настройка Redis
r = redis.Redis(host='redis', port=6379)

# Главная страница заработной платы
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
