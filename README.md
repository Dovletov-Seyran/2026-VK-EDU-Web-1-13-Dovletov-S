# AskPupkin

Сайт вопросов и ответов. Учебный проект VK Education.

## Страницы

| URL | Описание |
|-----|----------|
| `/home/` | Главная — список вопросов |
| `/ask/` | Задать вопрос |
| `/question/` | Страница вопроса |
| `/tag/` | Вопросы по тегу |
| `/profile/` | Настройки профиля |

## Запуск локально
```bash
git clone <ссылка на репозиторий>
cd <папка проекта>
python -m venv venv
source venv/bin/activate  # на Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

Открыть в браузере: http://127.0.0.1:8000/


