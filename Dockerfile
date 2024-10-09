# Используем базовый образ с Python
FROM python:3.9-slim

# Устанавливаем зависимости
WORKDIR /app
RUN pip install -r requirements.txt

# Копируем исходный код
COPY . .

# Запуск приложения
CMD ["python", "app.py"]
