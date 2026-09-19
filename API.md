# AimAI API для Telegram-бота

## Получить токен

```http
POST /api/auth/token/
Content-Type: application/json

{"username":"your-email-or-username","password":"your-password"}
```

Ответ содержит `token`. Сохрани его в настройках бота и передавай в каждом запросе:

```http
Authorization: Token YOUR_TOKEN
```

## Задачи

- `GET /api/tasks/` — список только задач текущего пользователя
- `POST /api/tasks/` — создать задачу (`title`, `due_at`, опционально `description`)
- `GET /api/tasks/{id}/` — получить задачу
- `PATCH /api/tasks/{id}/` — изменить задачу
- `DELETE /api/tasks/{id}/` — удалить задачу
- `POST /api/tasks/{id}/complete/` — выполнить задачу
- `POST /api/tasks/{id}/fail/` — записать причину пропуска: `{"text":"...","tags":["усталость"]}`

Все endpoint-ы требуют Token Authentication и автоматически ограничены владельцем задач.
