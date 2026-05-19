# AskPupkin

Сайт вопросов и ответов. Учебный проект VK Education.

## Запуск локально

```bash
git clone <ссылка на репозиторий>
cd public
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env.local  # заполнить параметры БД и SECRET_KEY
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Запуск через Docker

```bash
cp .env.example .env.docker  # указать DB_HOST=db
docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## Наполнение БД тестовыми данными

```bash
python manage.py fill_db 10       # для тестирования
```