# Конфигурация

Подробное описание всех переменных окружения и настроек Production Control.

## Содержание

- [Обзор](#обзор)
- [База данных](#база-данных)
- [Redis](#redis)
- [RabbitMQ](#rabbitmq)
- [Celery](#celery)
- [MinIO](#minio)
- [Логирование](#логирование)
- [Примеры конфигураций](#примеры-конфигураций)

## Обзор

Все настройки приложения задаются через переменные окружения в файле `.env` в корне проекта. Файл `.env` не должен попадать в систему контроля версий (должен быть в `.gitignore`).

## База данных

### PostgreSQL

```env
# Хост PostgreSQL
DB_HOST=postgres

# Порт PostgreSQL
DB_PORT=5432

# Имя базы данных
DB_NAME=production_control

# Пользователь базы данных
DB_USER=postgres

# Пароль пользователя
DB_PASSWORD=postgres

# Схема базы данных (по умолчанию: public)
DB_SCHEMA=public
```

### Описание параметров

- **DB_HOST** — адрес хоста PostgreSQL. В Docker Compose используйте имя сервиса (`postgres`), локально — `localhost`.
- **DB_PORT** — порт PostgreSQL (по умолчанию `5432`).
- **DB_NAME** — имя базы данных, которая будет использоваться приложением.
- **DB_USER** — имя пользователя для подключения к БД.
- **DB_PASSWORD** — пароль пользователя. **Важно**: в production используйте надежный пароль!
- **DB_SCHEMA** — схема базы данных (по умолчанию `public`).

### Примеры подключения

**Docker Compose:**
```env
DB_HOST=postgres
DB_PORT=5432
```

**Локальное подключение:**
```env
DB_HOST=localhost
DB_PORT=5432
```

**Внешний сервер:**
```env
DB_HOST=db.example.com
DB_PORT=5432
DB_USER=prod_user
DB_PASSWORD=secure_password_here
```

## Redis

```env
# Хост Redis
REDIS_HOST=redis

# Порт Redis
REDIS_PORT=6379

# Пароль Redis (опционально, оставьте пустым если не используется)
REDIS_PASSWORD=

# Номер базы данных Redis (0-15)
REDIS_DB=0

# Полный URL подключения (опционально, переопределяет отдельные параметры)
REDIS_URL=redis://redis:6379/0
```

### Описание параметров

- **REDIS_HOST** — адрес хоста Redis. В Docker Compose используйте имя сервиса (`redis`), локально — `localhost`.
- **REDIS_PORT** — порт Redis (по умолчанию `6379`).
- **REDIS_PASSWORD** — пароль для подключения к Redis. Оставьте пустым, если аутентификация не используется.
- **REDIS_DB** — номер базы данных Redis (от 0 до 15).
- **REDIS_URL** — полный URL подключения. Если указан, переопределяет отдельные параметры. Формат: `redis://[:password@]host[:port][/db]`

### Примеры подключения

**Без пароля:**
```env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

**С паролем:**
```env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=my_secure_password
REDIS_DB=0
```

**С использованием URL:**
```env
REDIS_URL=redis://:password@redis:6379/0
```

## RabbitMQ

```env
# Хост RabbitMQ
RABBITMQ_HOST=rabbitmq

# Порт RabbitMQ
RABBITMQ_PORT=5672

# Пользователь RabbitMQ
RABBITMQ_USER=guest

# Пароль пользователя
RABBITMQ_PASSWORD=guest

# Виртуальный хост
RABBITMQ_VHOST=/
```

### Описание параметров

- **RABBITMQ_HOST** — адрес хоста RabbitMQ. В Docker Compose используйте имя сервиса (`rabbitmq`), локально — `localhost`.
- **RABBITMQ_PORT** — порт RabbitMQ (по умолчанию `5672`).
- **RABBITMQ_USER** — имя пользователя для подключения к RabbitMQ.
- **RABBITMQ_PASSWORD** — пароль пользователя.
- **RABBITMQ_VHOST** — виртуальный хост (по умолчанию `/`).

### Примеры подключения

**Стандартная конфигурация:**
```env
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
```

**Production конфигурация:**
```env
RABBITMQ_HOST=rabbitmq.prod.example.com
RABBITMQ_PORT=5672
RABBITMQ_USER=prod_user
RABBITMQ_PASSWORD=secure_password
RABBITMQ_VHOST=/production
```

## Celery

```env
# URL брокера сообщений (если не указано, собирается из RABBITMQ_*)
CELERY_BROKER_URL=

# Бэкенд для хранения результатов (если не указано, собирается из REDIS_*)
CELERY_RESULT_BACKEND=

# Часовой пояс для планировщика задач
CELERY_TIMEZONE=UTC

# Очередь по умолчанию для задач
CELERY_TASK_DEFAULT_QUEUE=default

# Подтверждать выполнение задачи после завершения (true) или до начала (false)
CELERY_TASK_ACKS_LATE=true

# Отклонять задачи при потере воркера
CELERY_TASK_REJECT_ON_WORKER_LOST=true

# Количество параллельных воркеров
CELERY_WORKER_CONCURRENCY=2

# Префикс для ключей Redis
CELERY_REDIS_KEY_PREFIX=celery
```

### Описание параметров

- **CELERY_BROKER_URL** — полный URL брокера сообщений. Если не указан, автоматически собирается из `RABBITMQ_*` переменных. Формат: `amqp://user:password@host:port/vhost`
- **CELERY_RESULT_BACKEND** — URL бэкенда для хранения результатов задач. Если не указан, автоматически собирается из `REDIS_*` переменных.
- **CELERY_TIMEZONE** — часовой пояс для планировщика периодических задач (по умолчанию `UTC`).
- **CELERY_TASK_DEFAULT_QUEUE** — имя очереди по умолчанию для задач.
- **CELERY_TASK_ACKS_LATE** — если `true`, задачи подтверждаются после успешного выполнения, что предотвращает потерю задач при сбое воркера.
- **CELERY_TASK_REJECT_ON_WORKER_LOST** — если `true`, задачи отклоняются при потере воркера.
- **CELERY_WORKER_CONCURRENCY** — количество параллельных воркеров (по умолчанию `2`).
- **CELERY_REDIS_KEY_PREFIX** — префикс для всех ключей Redis, используемых Celery.

### Примеры конфигурации

**Автоматическая сборка URL (рекомендуется):**
```env
# Укажите только RabbitMQ и Redis параметры
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Celery автоматически соберет URL
CELERY_BROKER_URL=
CELERY_RESULT_BACKEND=
```

**Явное указание URL:**
```env
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

## MinIO

```env
# Endpoint MinIO (host:port)
MINIO_ENDPOINT=minio:9000

# Access Key для MinIO
MINIO_ACCESS_KEY=minioadmin

# Secret Key для MinIO
MINIO_SECRET_KEY=minioadmin

# Список bucket'ов через запятую (создаются автоматически)
MINIO_BUCKETS=reports,exports,imports

# Использовать HTTPS для подключения (true/false)
MINIO_SECURE=false
```

### Описание параметров

- **MINIO_ENDPOINT** — адрес и порт MinIO сервера в формате `host:port`.
- **MINIO_ACCESS_KEY** — ключ доступа (Access Key) для MinIO.
- **MINIO_SECRET_KEY** — секретный ключ (Secret Key) для MinIO.
- **MINIO_BUCKETS** — список bucket'ов, разделенных запятой. Bucket'ы создаются автоматически при старте приложения.
- **MINIO_SECURE** — использовать HTTPS для подключения (`true`) или HTTP (`false`).

### Примеры конфигурации

**Локальная разработка:**
```env
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKETS=reports,exports,imports
MINIO_SECURE=false
```

**Production с HTTPS:**
```env
MINIO_ENDPOINT=minio.example.com:9000
MINIO_ACCESS_KEY=production_access_key
MINIO_SECRET_KEY=production_secret_key
MINIO_BUCKETS=reports,exports,imports,backups
MINIO_SECURE=true
```

## Логирование

```env
# Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
```

### Описание параметров

- **LOG_LEVEL** — уровень логирования. Возможные значения:
  - `DEBUG` — детальная отладочная информация
  - `INFO` — информационные сообщения (по умолчанию)
  - `WARNING` — предупреждения
  - `ERROR` — ошибки
  - `CRITICAL` — критические ошибки

### Рекомендации

- **Development**: `DEBUG` или `INFO`
- **Staging**: `INFO` или `WARNING`
- **Production**: `WARNING` или `ERROR`

## Примеры конфигураций

### Минимальная конфигурация для разработки

```env
# База данных
DB_HOST=postgres
DB_PORT=5432
DB_NAME=production_control
DB_USER=postgres
DB_PASSWORD=postgres
DB_SCHEMA=public

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKETS=reports,exports,imports
MINIO_SECURE=false

# Логирование
LOG_LEVEL=INFO
```

### Production конфигурация

```env
# База данных
DB_HOST=db.production.example.com
DB_PORT=5432
DB_NAME=production_control
DB_USER=prod_user
DB_PASSWORD=very_secure_password_here
DB_SCHEMA=public

# Redis
REDIS_HOST=redis.production.example.com
REDIS_PORT=6379
REDIS_PASSWORD=redis_secure_password
REDIS_DB=0

# RabbitMQ
RABBITMQ_HOST=rabbitmq.production.example.com
RABBITMQ_PORT=5672
RABBITMQ_USER=prod_rabbitmq_user
RABBITMQ_PASSWORD=rabbitmq_secure_password
RABBITMQ_VHOST=/production

# Celery
CELERY_TIMEZONE=Europe/Moscow
CELERY_WORKER_CONCURRENCY=4
CELERY_TASK_ACKS_LATE=true
CELERY_TASK_REJECT_ON_WORKER_LOST=true

# MinIO
MINIO_ENDPOINT=minio.production.example.com:9000
MINIO_ACCESS_KEY=production_access_key
MINIO_SECRET_KEY=production_secret_key
MINIO_BUCKETS=reports,exports,imports,backups
MINIO_SECURE=true

# Логирование
LOG_LEVEL=WARNING
```

### Локальная разработка (без Docker для инфраструктуры)

```env
# База данных
DB_HOST=localhost
DB_PORT=5432
DB_NAME=production_control
DB_USER=postgres
DB_PASSWORD=postgres
DB_SCHEMA=public

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKETS=reports,exports,imports
MINIO_SECURE=false

# Логирование
LOG_LEVEL=DEBUG
```

## Безопасность

### Рекомендации для production

1. **Никогда не храните пароли в открытом виде** — используйте секретные менеджеры (HashiCorp Vault, AWS Secrets Manager, etc.)
2. **Используйте сильные пароли** — минимум 16 символов, смешанный регистр, цифры, спецсимволы
3. **Ограничьте доступ к БД** — используйте отдельного пользователя с минимальными правами
4. **Используйте SSL/TLS** — для всех внешних подключений
5. **Регулярно обновляйте пароли** — особенно после утечек или смены сотрудников
6. **Не коммитьте `.env` файлы** — убедитесь, что `.env` в `.gitignore`

## Проверка конфигурации

После настройки переменных окружения проверьте конфигурацию:

```bash
# Проверка подключения к БД
curl http://localhost:8000/api/healthcheck/database

# Проверка статуса сервиса
curl http://localhost:8000/api/healthcheck/service

# Просмотр логов для выявления проблем с конфигурацией
docker compose logs app
```

## Дополнительная информация

- [Установка и настройка](INSTALLATION.md)
- [Устранение неполадок](TROUBLESHOOTING.md)

