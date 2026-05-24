# AskPupkin

Сайт вопросов и ответов. Учебный проект VK Education.

## Запуск локально

### 1. Клонировать и настроить окружение

```bash
git clone <ссылка на репозиторий>
cd public
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env.local  # заполнить параметры БД, SECRET_KEY и остальные переменные
```

### 2. Запустить PostgreSQL и Redis

PostgreSQL и Redis должны быть установлены и запущены:

```bash
# Redis (Mac)
brew install redis
brew services start redis

# Проверка
redis-cli ping  # должен ответить PONG
```

### 3. Подготовить базу данных

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py fill_db 10  # наполнить тестовыми данными (необязательно)
```

### 4. Запустить Django

```bash
python manage.py runserver
```

### 5. Запустить Celery worker (в отдельном терминале)

```bash
cd public
source ../venv/bin/activate
celery -A application worker --loglevel=info
```

### 6. Запустить Celerybeat (в отдельном терминале)

```bash
cd public
source ../venv/bin/activate
celery -A application beat --loglevel=info
```

### 7. Запустить Centrifugo (в отдельном терминале)

Установить Centrifugo: https://centrifugal.dev/docs/getting-started/installation

```bash
centrifugo --config centrifugo/config.json
```

Нужно создать `centrifugo/config.json` по шаблону `centrifugo/config.template.json`.

### 8. Запустить MailDev (в отдельном терминале)

```bash
npx maildev
```

Веб-интерфейс для просмотра писем: http://localhost:1080

## Запуск через Docker

```bash
cp .env.example .env.docker
# В .env.docker указать:
#   DB_HOST=db
#   REDIS_HOST=redis
#   EMAIL_HOST=maildev
#   CENTRIFUGO_API_URL=http://centrifugo:8000/api

# Нужно создать centrifugo/config.json по шаблону centrifugo/config.template.json

docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py fill_db 10  # необязательно
```

Сервисы:
- Приложение: http://localhost:8000
- MailDev (просмотр писем): http://localhost:1080
- Centrifugo admin: http://localhost:8080