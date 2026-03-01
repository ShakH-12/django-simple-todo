# Руководство по тестированию — SimpleTodo

---

## Содержание

1. [Подготовка среды](#1-подготовка-среды)
2. [Запуск тестов](#2-запуск-тестов)
3. [Тестирование модели](#3-тестирование-модели)
4. [Тестирование API](#4-тестирование-api)
5. [Ручное тестирование (curl)](#5-ручное-тестирование-curl)
6. [Граничные случаи](#6-граничные-случаи)
7. [Тестирование безопасности](#7-тестирование-безопасности)
8. [Чек-лист](#8-чек-лист)

---

## 1. Подготовка среды

### Зависимости

```bash
pip install pytest pytest-django factory-boy coverage
```

### pytest.ini

Создайте файл `pytest.ini` в корне проекта:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = SimpleTodo.settings
python_files = tests.py test_*.py *_test.py
```

### .env для тестов

```
SECRET_KEY=test-secret-key-for-testing-only
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
```

---

## 2. Запуск тестов

```bash
# Django test runner
python manage.py test apps.tasks

# pytest с подробным выводом
pytest apps/tasks/tests.py -v

# Покрытие кода
coverage run --source='.' manage.py test apps.tasks
coverage report
coverage html   # HTML-отчёт → htmlcov/index.html
```

---

## 3. Тестирование модели

### Тест-кейсы

| Тест-кейс | Входные данные | Ожидаемый результат |
|---|---|---|
| Создание валидной задачи | `name="Задача 1"`, `content="Описание задачи"` | Задача создана, `id` присвоен |
| `name` < 5 символов | `name="ab"` | `ValidationError` |
| `content` < 5 символов | `content="abc"` | `ValidationError` |
| `name` из пробелов | `name="     "` | `ValidationError` (после strip) |
| Вызов `done()` | `task.done()` | `is_done=True`, `done_at` заполнен |
| Повторный `done()` | `task.done(); task.done()` | `done_at` обновляется |
| `save()` без full_clean | `name="x"` (длина 1) | `ValidationError` до записи в БД |

### Пример кода

```python
from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.tasks.models import Task


class TaskModelTest(TestCase):

    def test_create_valid_task(self):
        task = Task.objects.create(
            name="Купить молоко",
            content="Нужно купить молоко в магазине"
        )
        self.assertIsNotNone(task.id)
        self.assertFalse(task.is_done)
        self.assertIsNone(task.done_at)

    def test_name_too_short_raises(self):
        with self.assertRaises(ValidationError):
            Task.objects.create(name="ab", content="Нормальное описание задачи")

    def test_content_too_short_raises(self):
        with self.assertRaises(ValidationError):
            Task.objects.create(name="Задача 1", content="abc")

    def test_done_method_sets_fields(self):
        task = Task.objects.create(
            name="Задача тест",
            content="Описание задачи для теста"
        )
        task.done()
        task.refresh_from_db()
        self.assertTrue(task.is_done)
        self.assertIsNotNone(task.done_at)

    def test_done_updates_done_at(self):
        task = Task.objects.create(
            name="Задача тест",
            content="Описание задачи для теста"
        )
        task.done()
        first_done_at = task.done_at
        task.done()
        self.assertGreaterEqual(task.done_at, first_done_at)
```

---

## 4. Тестирование API

### 4.1 GET /api/tasks/

| Сценарий | Ожидаемый статус | Ожидаемый результат |
|---|---|---|
| Задач нет | 200 OK | `[]` |
| Есть 2 задачи | 200 OK | Массив из 2 объектов |
| Сортировка | 200 OK | Новые задачи первыми |

### 4.2 POST /api/tasks/

| Сценарий | Входные данные | Статус | Результат |
|---|---|---|---|
| Валидные данные | `{"name":"Задача 1","content":"Описание задачи 1"}` | 201 Created | Объект с `id` |
| Нет `name` | `{"content":"Описание"}` | 400 Bad Request | Ошибка на `name` |
| Нет `content` | `{"name":"Задача 1"}` | 400 Bad Request | Ошибка на `content` |
| `name` из пробелов | `{"name":"   ","content":"Описание задачи"}` | 400 Bad Request | Ошибка валидации |
| `name` < 5 символов | `{"name":"ab","content":"Описание задачи"}` | 400 Bad Request | MinLengthValidator |
| `content` > 1000 символов | `content` длиной 1001 символ | 400 Bad Request | MaxLengthValidator |

### 4.3 GET /api/tasks/{id}/

| Сценарий | Статус | Результат |
|---|---|---|
| Существующий ID | 200 OK | Полный объект задачи |
| Несуществующий ID | 404 Not Found | `{"detail": "No Task matches..."}` |

### 4.4 PATCH /api/tasks/{id}/

| Сценарий | Входные данные | Статус | Результат |
|---|---|---|---|
| Обновление `name` | `{"name":"Новое название"}` | 200 OK | `name` обновлён |
| Завершение задачи | `{"is_done":true}` | 200 OK | `is_done=true`, `done_at` заполнен |
| Несуществующий ID | PATCH `/api/tasks/9999/` | 404 Not Found | Not found |
| Невалидные данные | `{"name":"ab"}` | 400 Bad Request | Ошибка валидации |

### Пример кода

```python
from rest_framework.test import APITestCase
from rest_framework import status
from apps.tasks.models import Task


class TaskAPITest(APITestCase):
    URL = '/api/tasks/'

    def setUp(self):
        self.valid_data = {
            "name": "Тестовая задача",
            "content": "Описание тестовой задачи"
        }

    def test_list_empty(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_create_task_success(self):
        response = self.client.post(self.URL, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(Task.objects.count(), 1)

    def test_create_task_missing_name(self):
        data = {"content": "Описание задачи без имени"}
        response = self.client.post(self.URL, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_get_task_not_found(self):
        response = self.client.get('/api/tasks/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mark_task_done(self):
        task = Task.objects.create(**self.valid_data)
        response = self.client.patch(
            f'/api/tasks/{task.id}/',
            {'is_done': True},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertTrue(task.is_done)
        self.assertIsNotNone(task.done_at)

    def test_list_sorted_by_created_desc(self):
        Task.objects.create(name="Задача первая", content="Первое описание задачи")
        Task.objects.create(name="Задача вторая", content="Второе описание задачи")
        response = self.client.get(self.URL)
        self.assertEqual(response.data[0]['name'], "Задача вторая")
```

---

## 5. Ручное тестирование (curl)

```bash
# Создать задачу
curl -X POST http://127.0.0.1:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Купить продукты", "content": "Молоко хлеб масло"}'

# Получить все задачи
curl http://127.0.0.1:8000/api/tasks/

# Получить задачу по ID
curl http://127.0.0.1:8000/api/tasks/1/

# Завершить задачу
curl -X PATCH http://127.0.0.1:8000/api/tasks/1/ \
  -H "Content-Type: application/json" \
  -d '{"is_done": true}'

# Проверка 404
curl http://127.0.0.1:8000/api/tasks/9999/
```

---

## 6. Граничные случаи

| Случай | Ожидание |
|---|---|
| `name` ровно 5 символов | ✅ Проходит (граница MinLengthValidator) |
| `name` ровно 64 символа | ✅ Проходит (граница max_length) |
| `name` 65 символов | ❌ 400 Bad Request |
| `content` ровно 1000 символов | ✅ Проходит (граница MaxLengthValidator) |
| `content` 1001 символ | ❌ 400 Bad Request |
| Пробелы вокруг `name` | Очищаются через `strip()` в сериализаторе |
| `PATCH` без `is_done` | `done_at` не изменяется |
| Повторный `PATCH is_done=true` | `done_at` перезаписывается |

---

## 7. Тестирование безопасности

### Rate Limiting

При превышении 100 запросов/час:

```json
// 429 Too Many Requests
{ "detail": "Request was throttled. Expected available in X seconds." }
```

### Заголовки безопасности

Проверьте наличие в ответе сервера:

```bash
curl -I http://127.0.0.1:8000/api/tasks/
# Ожидаем:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
```

### CORS

- `DEBUG=True` — разрешены все origins
- `DEBUG=False` — только `http://localhost:5000` и `http://127.0.0.1:5000`

---

## 8. Чек-лист

- [ ] `GET /api/tasks/` возвращает 200 и список задач
- [ ] `POST` с валидными данными создаёт задачу (201)
- [ ] `POST` с `name` < 5 символов возвращает 400
- [ ] `POST` без обязательных полей возвращает 400
- [ ] `GET /api/tasks/{id}/` возвращает задачу (200)
- [ ] `GET /api/tasks/9999/` возвращает 404
- [ ] `PATCH` с `is_done=true` устанавливает `done_at`
- [ ] `strip()` убирает пробелы из `name` и `content`
- [ ] Заголовок `X-Frame-Options: DENY` присутствует
- [ ] 101-й запрос в час возвращает 429
- [ ] `save()` вызывает `full_clean()` и блокирует невалидные данные
- [ ] Метод `done()` использует `update_fields` (не перезаписывает всю запись)
