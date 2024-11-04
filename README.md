
# API для обработки изображений
Приложение на основе FastAPI для загрузки, обработки и управления изображениями, с поддержкой аутентификации пользователей, кэширования с помощью Redis, фоновых задач с RabbitMQ и базы данных PostgreSQL.

## Содержание
- Возможности
- Требования
- Установка
  - Клонирование репозитория
  - Переменные окружения
  - Развертывание с помощью Docker
  - Локальное развертывание
- Использование
  - Документация API
  - Процесс аутентификации
  - Конечные точки API
- Тестирование
- Структура проекта
- Внесение изменений
- Лицензия

## Возможности
- Аутентификация пользователей: Безопасная регистрация и вход с использованием JWT токенов.
- Загрузка изображений: Пользователи могут загружать изображения, которые сохраняются на сервере.
- Обработка изображений: Фоновые задачи изменяют размер изображений и конвертируют их в градации серого.
- Кэширование: Используется Redis для кэширования данных изображений для более быстрого получения.
- Фоновые задачи: RabbitMQ и процессорный сервис обрабатывают задачи на фоне.
- База данных: Для постоянного хранения данных используется PostgreSQL.
- Документация API: Интерактивная документация API с помощью Swagger UI.

## Требования
- Установленные Docker и Docker Compose.
- Альтернативно для локального развертывания:
  - Python 3.10 или выше.
  - База данных PostgreSQL.
  - Сервер Redis.
  - Сервер RabbitMQ.

## Установка

### Клонирование репозитория
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### Переменные окружения
Создайте файл `.env` в корневой директории и укажите следующие переменные:

```env
DATABASE_URL=postgresql://user:password@db:5432/image_db
BROKER_URL=amqp://guest:guest@broker:5672/
REDIS_URL=redis://cache:6379/0
SECRET_KEY=your_secret_key
```
- Замените `user` и `password` на ваши учетные данные PostgreSQL.
- Установите `SECRET_KEY` как безопасную случайную строку.

### Развертывание с помощью Docker

#### Сборка и запуск контейнеров
```bash
docker-compose up -d --build
```
Эта команда соберет и запустит все службы, определенные в файле `docker-compose.yml`:
- `web`: Приложение FastAPI.
- `db`: База данных PostgreSQL.
- `cache`: Сервер Redis.
- `broker`: Сервер RabbitMQ.
- `processor`: Фоновый обработчик изображений.

#### Применение миграций базы данных
```bash
docker-compose exec web alembic upgrade head
```

### Локальное развертывание

#### Установка зависимостей
```bash
pip install -r requirements.txt
```

#### Применение миграций базы данных
```bash
alembic upgrade head
```

#### Запуск приложения
```bash
uvicorn app.main:app --reload
```
Убедитесь, что PostgreSQL, Redis и RabbitMQ запущены и доступны с конфигурациями, указанными в вашем `.env` файле.

## Использование

### Документация API
После запуска приложения откройте в браузере:
```bash
http://localhost:8000/docs
```

### Процесс аутентификации

#### Регистрация нового пользователя
**Конечная точка**: `POST /api/v1/auth/signup`

**Тело запроса**:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

#### Получение JWT токена
**Конечная точка**: `POST /api/v1/auth/token`

**Тело запроса**:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```
Ответ будет содержать `access_token`, который нужно использовать для авторизации последующих запросов.

#### Авторизация в Swagger UI
Нажмите кнопку `Authorize` в Swagger UI и введите токен в формате:
```
Bearer your_access_token
```

## Конечные точки API

### Аутентификация
- **Регистрация**: `POST /api/v1/auth/signup`
  Регистрирует нового пользователя.
- **Токен**: `POST /api/v1/auth/token`
  Возвращает JWT токен для авторизованных запросов.

### Изображения
- **Загрузка изображения**: `POST /api/v1/images/`
  Загрузка нового изображения.
  **Параметры**:
  - `name` (query): Имя изображения.
  - `tags` (query): Теги через запятую (опционально).
  - `file` (form): Файл изображения.
- **Список изображений**: `GET /api/v1/images/`
  Получение списка изображений.
  **Параметры**:
  - `skip` (query): Количество пропускаемых записей (по умолчанию: 0).
  - `limit` (query): Максимальное количество возвращаемых записей (по умолчанию: 10).
- **Получение изображения**: `GET /api/v1/images/{image_id}`
  Получение данных о конкретном изображении.
- **Обновление изображения**: `PUT /api/v1/images/{image_id}`
  Обновление данных изображения.
  **Тело запроса**:
  ```json
  {
    "name": "New Name",
    "tags": "tag1, tag2"
  }
  ```
- **Удаление изображения**: `DELETE /api/v1/images/{image_id}`
  Удаление изображения.

## Тестирование

### Запуск тестов
Убедитесь, что установлены `pytest` и другие зависимости:
```bash
pip install pytest pytest-asyncio httpx
```
Запуск тестов:
```bash
pytest
```

### Пример теста
```python
# tests/test_app.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_signup():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/signup", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
```

## Структура проекта
```
├── app
│   ├── api
│   │   └── v1
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── images.py
│   ├── crud.py
│   ├── database.py
│   ├── dependencies.py
│   ├── image_processing.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── config.py
├── tests
│   ├── __init__.py
│   └── test_app.py
├── alembic
│   ├── versions
│   │   └── [timestamp]_create_tables.py
│   ├── env.py
│   └── script.py.mako
├── uploads
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

