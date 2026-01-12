# Production Control

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.123+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Система управления производством с поддержкой фоновых задач и событийно-ориентированной архитектуры.

## Содержание

- [Описание](#описание)
- [Основные возможности](#основные-возможности)
- [Архитектура](#архитектура)
- [Технологический стек](#технологический-стек)
- [Быстрый старт](#быстрый-старт)
- [Документация](#документация)
- [Лицензия](#лицензия)

## Описание

Production Control — это система управления производством, построенная на принципах Clean Architecture, CQRS и Event-Driven Architecture. Система обеспечивает управление партиями продукции, рабочими центрами, продуктами, аналитикой и вебхуками для интеграции с внешними системами.

## Основные возможности

- **Управление партиями** — создание, обновление, закрытие и агрегация партий продукции
- **Управление продуктами** — работа с продуктами и их агрегация
- **Рабочие центры** — управление рабочими центрами производства
- **Аналитика** — аналитические запросы и отчеты
- **Вебхуки** — система подписок и доставки событий
- **Фоновые задачи** — асинхронная обработка с использованием Celery
- **Генерация отчетов** — создание отчетов в различных форматах (PDF, Excel)
- **Импорт/Экспорт** — массовый импорт и экспорт данных
- **Outbox Pattern** — надежная доставка событий через паттерн Outbox

## Архитектура

Проект следует принципам **Clean Architecture** с четким разделением на слои:

```
src/
├── domain/             # Доменная модель (сущности, события, value objects)
├── application/        # Use cases (commands, query handlers, DTO)
├── infrastructure/     # Реализация инфраструктуры
│   ├── persistence/    # Модели БД, репозитории, миграции
│   ├── background_tasks/ # Celery app и задачи
│   ├── events/         # Сериализация событий и реестр
│   └── webhooks/       # Отправка вебхуков
└── presentation/       # FastAPI приложение и endpoints
```

### Ключевые архитектурные паттерны

- **Clean Architecture** — разделение на слои с инверсией зависимостей
- **CQRS** — разделение команд (write) и запросов (read)
- **Domain Events** — события домена для слабой связанности
- **Outbox Pattern** — надежная доставка событий
- **Repository Pattern** — абстракция доступа к данным
- **Unit of Work** — управление транзакциями

Подробнее об архитектуре см. в [docs/ARCHITECTURE_ANALYSIS.md](docs/ARCHITECTURE_ANALYSIS.md) и [docs/EVENTS_ARCHITECTURE.md](docs/EVENTS_ARCHITECTURE.md).

## Технологический стек

### Backend
- **Python 3.13+** — язык программирования
- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.0** — ORM
- **Alembic** — миграции БД
- **AsyncPG** — асинхронный драйвер PostgreSQL
- **Pydantic** — валидация данных

### Инфраструктура
- **PostgreSQL** — основная база данных
- **Redis** — кэширование и бэкенд для Celery
- **RabbitMQ** — брокер сообщений для Celery
- **MinIO** — объектное хранилище для файлов
- **Celery** — распределенная очередь задач
- **Flower** — мониторинг Celery

### Инструменты разработки
- **uv** — менеджер зависимостей и пакетов
- **Ruff** — линтер и форматтер
- **Pre-commit** — хуки для проверки кода
- **Docker & Docker Compose** — контейнеризация

## Быстрый старт

### Требования

- **Python 3.13+**
- **Docker 20.10+** и **Docker Compose 2.0+**
- **uv** (для управления зависимостями)

> **Использование Dev Containers**: Проект поддерживает Dev Containers для быстрой настройки среды разработки. Подробные инструкции см. в [docs/DEVCONTAINERS.md](docs/DEVCONTAINERS.md).

### Установка

1. **Клонирование репозитория**

```bash
git clone <repository-url>
cd production-control
```

2. **Настройка окружения**

Создайте файл `.env` в корне проекта. Пример конфигурации см. в [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

3. **Установка зависимостей**

```bash
uv sync
```

4. **Запуск миграций**

```bash
docker compose --profile migration up
```

5. **Запуск сервисов**

```bash
# Запуск всего стека (API + Celery)
docker compose --profile api --profile celery up -d
```

6. **Проверка работоспособности**

```bash
# Проверка API
curl http://localhost:8000/api/healthcheck/service

# Проверка базы данных
curl http://localhost:8000/api/healthcheck/database
```

### Доступ к сервисам

После запуска сервисы будут доступны:

- **API**: <http://localhost:8000>
- **API Документация (Swagger)**: <http://localhost:8000/docs>
- **API Документация (ReDoc)**: <http://localhost:8000/redoc>
- **Flower** (Celery мониторинг): <http://localhost:5555>
- **RabbitMQ Management**: <http://localhost:15672> (guest/guest)
- **MinIO Console**: <http://localhost:19001> (minioadmin/minioadmin)

## Документация

### Для пользователей

- **[Установка и настройка](docs/INSTALLATION.md)** — подробное руководство по установке и настройке системы
- **[Конфигурация](docs/CONFIGURATION.md)** — описание всех переменных окружения и настроек
- **[API Документация](docs/API.md)** — полное описание REST API с примерами использования
- **[Мониторинг](docs/MONITORING.md)** — руководство по мониторингу и логированию
- **[Устранение неполадок](docs/TROUBLESHOOTING.md)** — решение распространенных проблем

### Для разработчиков

- **[Руководство для разработчиков](docs/DEVELOPMENT.md)** — архитектура, структура проекта, добавление функциональности
- **[Архитектура событий](docs/EVENTS_ARCHITECTURE.md)** — описание событийно-ориентированной архитектуры
- **[Руководство по CQRS и запросам](docs/CQRS_QUERY_GUIDELINES.md)** — рекомендации по работе с запросами
- **[Dev Containers](docs/DEVCONTAINERS.md)** — настройка среды разработки с Dev Containers

### Быстрая навигация

| Задача | Документ |
|--------|----------|
| Установить систему | [INSTALLATION.md](docs/INSTALLATION.md) |
| Настроить переменные окружения | [CONFIGURATION.md](docs/CONFIGURATION.md) |
| Использовать API | [API.md](docs/API.md) |
| Добавить новую функциональность | [DEVELOPMENT.md](docs/DEVELOPMENT.md) |
| Настроить мониторинг | [MONITORING.md](docs/MONITORING.md) |
| Решить проблему | [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) |
| Понять архитектуру | [ARCHITECTURE_ANALYSIS.md](docs/ARCHITECTURE_ANALYSIS.md) |

## Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.

---

**Автор**: Nikolai Bebikov
**Версия**: 0.1.0
