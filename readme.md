# CRM Backend Service

Мини-CRM система с поддержкой нескольких организаций, сделок, контактов и задач.

## Технологии

- **Python 3.13+**
- **FastAPI** (async)
- **SQLAlchemy 2.0** + **Alembic** (миграции)
- **PostgreSQL**
- **JWT** аутентификация (access/refresh токены)
- **Docker** / **Docker Compose**

## Архитектура

Проект разделён на слои:

```
app/
├── domain/          # Доменная логика (entities, value objects, services)
├── application/     # Слой приложения (commands, queries, mediator)
├── infrastructure/  # Инфраструктура (database, repositories)
└── presentation/     # API слой (FastAPI routes, schemas)
```

### Основные компоненты

- **Domain Layer**: Бизнес-сущности и правила
- **Application Layer**: CQRS паттерн (Commands/Queries через Mediator)
- **Infrastructure Layer**: Репозитории, модели БД, конвертеры
- **Presentation Layer**: REST API endpoints

## Быстрый старт

### Требования

- Docker и Docker Compose
- Poetry (для управления зависимостями)

### Запуск

1. Клонируйте репозиторий
2. Создайте `.env` файл (см. пример ниже)
3. Запустите сервисы:

```bash
make all
```

4. Примените миграции:

```bash
make migrate
```

5. API доступен по адресу: `http://localhost:8000`

### Основные команды

```bash
make all              # Запустить все сервисы
make all-down         # Остановить все сервисы
make test             # Запустить тесты
make migrate          # Применить миграции
make migrations       # Создать новую миграцию
make app-shell        # Войти в контейнер приложения
```

## API

Все эндпоинты начинаются с `/api/v1/`.

### Основные ресурсы

- `/api/v1/auth/register` - Регистрация
- `/api/v1/auth/login` - Авторизация
- `/api/v1/organizations/` - Организации
- `/api/v1/contacts/` - Контакты
- `/api/v1/deals/` - Сделки
- `/api/v1/tasks/` - Задачи
- `/api/v1/analytics/deals/` - Аналитика

## Роли и права

- **owner/admin**: Полный доступ ко всем сущностям организации
- **manager**: Управление всеми сущностями (кроме настроек организации)
- **member**: Может изменять только свои контакты, сделки и задачи

## Тесты

Проект содержит unit и интеграционные тесты:

```bash
make test
```

Все бизнес-правила из задания покрыты тестами:
- Правила валидации сделок и задач
- Проверки прав доступа (403/404)
- Проверки ролей (owner, admin, manager, member)
- Аналитика

## Структура БД

Основные сущности:
- `organizations` - Организации
- `users` - Пользователи
- `organization_members` - Участники организаций (с ролями)
- `contacts` - Контакты
- `deals` - Сделки
- `tasks` - Задачи
- `activities` - Активности (таймлайн по сделкам)

## Переменные окружения

Создайте `.env` файл:

```env
API_PORT=8000
PYTHONPATH=/app

POSTGRES_DB=crm
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin
PGADMIN_PORT=5050

JWT_SECRET_KEY="63f4945d921d599f27ae4fdf5bada3f1"
```
