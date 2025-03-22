# VPN Billing System

Система биллинга для VPN-сервиса на основе Netbird.

## Функциональность

- Управление пользователями VPN
- Система оплаты и подписок
- Интеграция с Netbird API
- Автоматическая блокировка пользователей при неуплате
- API для управления пользователями
- Веб-интерфейс с админ-панелью и личным кабинетом

## Запуск в Docker

1. Убедитесь, что у вас установлены Docker и Docker Compose

2. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd vpn-billing
```

3. Создайте файл .env на основе .env.example и настройте необходимые переменные окружения:
```bash
cp .env.example .env
```

4. Запустите приложение с помощью Docker Compose:
```bash
docker-compose up -d
```

После запуска будут доступны следующие сервисы:
- Веб-приложение: http://localhost:8000
- PgAdmin: http://localhost:5050
  - Email: admin@admin.com
  - Пароль: admin

## Ручная установка (без Docker)

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd vpn-billing
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env на основе .env.example и настройте необходимые переменные окружения:
```bash
cp .env.example .env
```

5. Примените миграции:
```bash
alembic upgrade head
```

6. Запустите сервер:
```bash
python run.py
```

## Конфигурация

Создайте файл .env со следующими параметрами:

```
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key
NETBIRD_API_KEY=your-netbird-api-key
NETBIRD_API_URL=https://api.netbird.io/api/v1
```

## API Documentation

После запуска сервера, документация API доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Структура проекта

```
vpn-billing/
├── app/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   └── netbird.py
├── alembic/
│   ├── versions/
│   └── env.py
├── alembic.ini
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
``` 