# CRM System - Multi-tenant Backend

![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen)

Backend-сервис для мини-CRM c поддержкой мультитенантности. Архитектура построена на принципах Domain-Driven Design с четким разделением слоев и изоляцией бизнес-логики. Система предоставляет версионированное REST API для управления организациями, пользователями, контактами, сделками, задачами и аналитикой продаж.

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

**Dependency Injection** реализован через контейнер `punq`. Все зависимости (репозитории, доменные сервисы, command/query handlers) регистрируются в контейнере и автоматически инжектируются в handlers через конструкторы. Контейнер создается один раз при старте приложения и используется во всех эндпоинтах через FastAPI Depends.

### Модель данных

Реализованы все требуемые сущности:

**Organization**
- `id` — UUID
- `name` — строка
- `created_at` — timestamp

**User**
- `id` — UUID
- `email` — строка (уникальный)
- `hashed_password` — строка (bcrypt)
- `name` — строка
- `created_at` — timestamp

**OrganizationMember**
- `id` — UUID
- `organization_id` — UUID (FK → Organization)
- `user_id` — UUID (FK → User)
- `role` — enum (owner, admin, manager, member)
- Уникальность пары `(organization_id, user_id)`

**Contact**
- `id` — UUID
- `organization_id` — UUID (FK → Organization)
- `owner_id` — UUID (FK → User)
- `name` — строка
- `email` — строка
- `phone` — строка
- `created_at` — timestamp

**Deal**
- `id` — UUID
- `organization_id` — UUID (FK → Organization)
- `contact_id` — UUID (FK → Contact)
- `owner_id` — UUID (FK → User)
- `title` — строка
- `amount` — decimal
- `currency` — строка (USD, EUR, RUB и т.д.)
- `status` — enum (new, in_progress, won, lost)
- `stage` — enum (qualification, proposal, negotiation, closed)
- `created_at` — timestamp
- `updated_at` — timestamp

**Task**
- `id` — UUID
- `deal_id` — UUID (FK → Deal)
- `title` — строка
- `description` — строка (nullable)
- `due_date` — date (nullable)
- `is_done` — boolean
- `created_at` — timestamp

**Activity**
- `id` — UUID
- `deal_id` — UUID (FK → Deal)
- `author_id` — UUID (FK → User, nullable)
- `type` — enum (comment, status_changed, stage_changed, task_created, system)
- `payload` — JSONB (произвольные данные)
- `created_at` — timestamp

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

**Авторизация** (`/api/v1/auth`)
- `POST /api/v1/auth/register` — регистрация пользователя
- `POST /api/v1/auth/login` — аутентификация и получение токенов
- `POST /api/v1/auth/token/refresh` — обновление access токена

**Организации** (`/api/v1/organizations`)
- `POST /api/v1/organizations` — создание организации
- `GET /api/v1/organizations/me` — список организаций текущего пользователя

**Контакты** (`/api/v1/contacts`)
- `GET /api/v1/contacts` — список контактов (фильтры: page, page_size, search, owner_id)
- `POST /api/v1/contacts` — создание контакта
- `GET /api/v1/contacts/{contact_id}` — получение контакта по ID
- `DELETE /api/v1/contacts/{contact_id}` — удаление контакта

**Сделки** (`/api/v1/deals`)
- `GET /api/v1/deals` — список сделок (фильтры: page, page_size, status, min_amount, max_amount, stage, owner_id, order_by, order)
- `POST /api/v1/deals` — создание сделки
- `GET /api/v1/deals/{deal_id}` — получение сделки по ID
- `PATCH /api/v1/deals/{deal_id}` — обновление сделки (статус, стадия)

**Активности** (`/api/v1/deals/{deal_id}/activities`)
- `GET /api/v1/deals/{deal_id}/activities` — список активностей по сделке
- `POST /api/v1/deals/{deal_id}/activities` — создание комментария

**Задачи** (`/api/v1/tasks`)
- `GET /api/v1/tasks` — список задач (фильтры: page, page_size, deal_id, only_open, due_before, due_after, is_done)
- `POST /api/v1/tasks` — создание задачи
- `GET /api/v1/tasks/{task_id}` — получение задачи по ID
- `PATCH /api/v1/tasks/{task_id}` — обновление задачи

**Аналитика** (`/api/v1/analytics`)
- `GET /api/v1/analytics/deals/summary` — сводка по сделкам (фильтры: created_after, status_list)
- `GET /api/v1/analytics/deals/funnel` — воронка продаж (фильтры: status_list)

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

### Управление сервисами

| Команда | Описание |
|---------|----------|
| `make all` | Запуск приложения + PostgreSQL |
| `make all-down` | Остановка всех сервисов |
| `make app-up` | Запуск только приложения |
| `make app-down` | Остановка приложения |
| `make storages` | Запуск только PostgreSQL |
| `make storages-down` | Остановка PostgreSQL |

### Миграции

| Команда | Описание |
|---------|----------|
| `make migrations` | Создание новой миграции (autogenerate) |
| `make migrate` | Применение миграций (upgrade head) |

### Разработка

| Команда | Описание |
|---------|----------|
| `make test` | Запуск всех тестов |
| `make precommit` | Запуск pre-commit проверок для всех файлов |
| `make app-shell` | Подключение напрямую в контейнер приложения |
| `make postgres` | Подключение к PostgreSQL через psql |

### Логи

| Команда | Описание |
|---------|----------|
| `make app-logs` | Просмотр логов приложения |
| `make storages-logs` | Просмотр логов PostgreSQL |
