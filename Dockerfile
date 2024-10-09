# Используем базовый образ с Python
FROM python:3.9-slim

# Устанавливаем зависимости
WORKDIR /app
RUN pip install flask

# Копируем исходный код
COPY app.py /app/app.py

# Запуск приложения
CMD ["python", "app.py"]
