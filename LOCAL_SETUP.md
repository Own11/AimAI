# Локальный запуск без Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.local.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Открыть http://127.0.0.1:8000/tasks/.

В локальном режиме используется SQLite, а Celery работает eager-режиме и не требует Redis. Для реального Gemini добавьте `GEMINI_API_KEY` в `.env`.

Для фонового запуска Celery без Docker установите Redis локально, замените `CELERY_TASK_ALWAYS_EAGER=0`, затем в отдельных терминалах запустите:

```bash
celery -A config worker -l info
celery -A config beat -l info
```
