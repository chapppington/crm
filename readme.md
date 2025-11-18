# CRM System - Multi-tenant Backend

![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen)

Backend-сервис мини-CRM с поддержкой мультитенантности. Версионированное JSON API для управления организациями, пользователями, контактами, сделками, задачами и аналитикой.

## Реализованные требования

### Технологический стек

- Python 3.13, FastAPI (async)
- PostgreSQL, SQLAlchemy 2.0, Alembic
- JWT аутентификация (access/refresh токены)
- Type hints во всех слоях
- Docker, docker-compose
- Pydantic Settings для конфигурации

### Архитектура

Проект разделен на четыре слоя:

- **Domain** (`app/domain/`) — бизнес-логика, сущности, value objects, доменные сервисы
- **Application** (`app/application/`) — use cases через CQRS (Commands/Queries) и Mediator
- **Infrastructure** (`app/infrastructure/`) — SQLAlchemy модели, репозитории, конвертеры, миграции
- **Presentation** (`app/presentation/`) — FastAPI роуты, схемы запросов/ответов

### Модель данных

Реализованы все требуемые сущности:

- **Organization** — id, name, created_at
- **User** — id, email (уникальный), hashed_password, name, created_at
- **OrganizationMember** — id, organization_id, user_id, role (owner/admin/manager/member), уникальность пары (organization_id, user_id)
- **Contact** — id, organization_id, owner_id, name, email, phone, created_at
- **Deal** — id, organization_id, contact_id, owner_id, title, amount, currency, status, stage, created_at, updated_at
- **Task** — id, deal_id, title, description, due_date, is_done, created_at
- **Activity** — id, deal_id, author_id, type, payload (JSONB), created_at

### Бизнес-правила

- Multi-tenant: работа в контексте организации через заголовок X-Organization-Id
- Роли и права: owner/admin/manager/member с соответствующими ограничениями доступа
- Проверки доступа: 403/404 для чужой организации
- Сделки:
  - Нельзя закрыть сделку со статусом won, если amount <= 0
  - Автоматическое создание Activity при смене статуса/стадии
  - Запрет отката стадии назад для member (разрешено для admin/owner)
- Контакты: нельзя удалить контакт с активными сделками
- Задачи: нельзя создать задачу для чужой сделки (member), due_date не в прошлом
- Организационный контекст: проверка принадлежности сущностей к организации

### API эндпоинты

- Авторизация: `/api/v1/user/register`, `/api/v1/user/login`, `/api/v1/user/token/refresh`
- Организации: `/api/v1/organizations` (CRUD + members)
- Контакты: `/api/v1/contacts` (CRUD с фильтрацией)
- Сделки: `/api/v1/deals` (CRUD с фильтрацией и сортировкой)
- Задачи: `/api/v1/tasks` (CRUD с фильтрацией)
- Активности: `/api/v1/deals/{deal_id}/activities` (GET, POST для комментариев)
- Аналитика: `/api/v1/analytics/deals`, `/api/v1/analytics/funnel`

### Аналитика

- Сводка по сделкам: количество по статусам, суммы, средний amount, новые сделки за период
- Воронка продаж: количество по стадиям, конверсия между стадиями

### Тестирование

- Unit-тесты бизнес-логики (правила перехода статусов, ролей)
- Интеграционные тесты API через TestClient (полные сценарии: регистрация → организация → контакты → сделки → задачи → аналитика)
- Покрытие: 87%

### Качество кода

- Типизация во всех публичных интерфейсах
- Обработка ошибок: 400 (валидация), 401 (неавторизован), 403 (нет прав), 404 (не найдено), 409 (конфликт)
- Линтер: ruff + isort с pre-commit хуками

## Запуск

```bash
# Копирование файла с переменными окружения
cp .env.example .env

# Запуск всех сервисов
make all

# Применение миграций
make migrate

# Запуск тестов
make test
```

API документация: http://localhost:8000/api/docs

## Основные команды

| Команда | Описание |
|---------|----------|
| `make all` | Запуск приложения + PostgreSQL |
| `make migrate` | Применение миграций |
| `make test` | Запуск всех тестов |
| `make migrations` | Создание новой миграции |