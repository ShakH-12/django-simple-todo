# SimpleTodo

REST API для управления задачами на Django + Django REST Framework.

---

## Технологический стек

| Компонент | Технология |
|---|---|
| Backend | Python / Django |
| API | Django REST Framework |
| База данных | SQLite (dev) |
| Rate Limiting | 100 запросов/час (AnonRateThrottle) |
| CORS | django-cors-headers |
| Конфигурация | python-decouple (.env) |

---

## Структура проекта

```
SimpleTodo/
├── SimpleTodo/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   └── tasks/
│       ├── models.py       # Модель Task
│       ├── views.py        # CreateListTaskView, TaskDetailView
│       ├── serializers.py
│       ├── urls.py
│       └── tests.py
├── manage.py
└── cdb.py
```

---

## Установка и запуск

```bash
# 1. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Установить зависимости
pip install django djangorestframework django-cors-headers python-decouple

# 3. Создать .env в корне проекта
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 4. Применить миграции и запустить
python manage.py migrate
python manage.py runserver
```

API доступно по адресу: `http://127.0.0.1:8000/api/tasks/`

---

## Модель данных

| Поле | Тип | Ограничения | Описание |
|---|---|---|---|
| `name` | CharField | min=5, max=64 | Название задачи |
| `content` | TextField | min=5, max=1000 | Описание задачи |
| `is_done` | BooleanField | default=False | Статус выполнения |
| `done_at` | DateTimeField | null/blank | Время завершения |
| `created_at` | DateTimeField | auto_now_add | Время создания |
| `updated_at` | DateTimeField | auto_now | Время обновления |

**Методы модели:**
- `done()` — устанавливает `is_done=True` и записывает текущее время в `done_at`
- `save()` — вызывает `full_clean()` перед сохранением (валидация на уровне модели)

---

## API Endpoints

### `GET /api/tasks/` — Список задач

Возвращает все задачи, отсортированные по дате создания (новые первыми).

```json
[
  {
    "id": 1,
    "name": "Купить продукты",
    "content": "Молоко, хлеб, масло",
    "is_done": false,
    "done_at": null,
    "created_at": "2025-01-01T10:00:00Z",
    "updated_at": "2025-01-01T10:00:00Z"
  }
]
```

### `POST /api/tasks/` — Создать задачу

Обязательные поля: `name`, `content`.

```json
// Request
{ "name": "Купить продукты", "content": "Молоко, хлеб, масло" }

// Response 201
{ "id": 2, "name": "Купить продукты", "content": "Молоко, хлеб, масло", "is_done": false, ... }
```

### `GET /api/tasks/{id}/` — Получить задачу

Возвращает задачу по ID. `404` если не найдена.

### `PATCH /api/tasks/{id}/` — Обновить задачу

Частичное обновление. При передаче `is_done=true` автоматически вызывается `done()` и проставляется `done_at`.

```json
// Request
{ "is_done": true }

// Response 200
{ "id": 1, "is_done": true, "done_at": "2025-01-01T12:00:00Z", ... }
```

---

## Безопасность

- **Rate limiting:** 100 запросов/час для анонимных пользователей (429 при превышении)
- **CORS:** в `DEBUG=True` разрешены все origins; в продакшене только `localhost:5000`
- **Заголовки:** `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, XSS-фильтр
- **Аутентификация:** отсутствует (`AllowAny`)
