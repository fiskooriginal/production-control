# Dev Containers - Гайд по настройке

Этот документ описывает настройку и использование Dev Containers для разработки проекта Production Control в Visual Studio Code и PyCharm.

## Что такое Dev Containers?

Dev Containers (Development Containers) позволяют использовать Docker-контейнер в качестве полноценной среды разработки. Это обеспечивает:

- **Воспроизводимость**: одинаковая среда для всех разработчиков
- **Изоляцию**: зависимости проекта не влияют на систему
- **Быстрый старт**: новые разработчики могут начать работу за минуты
- **Консистентность**: одинаковые версии инструментов и библиотек

## Структура конфигурации

Проект использует следующую структуру Dev Containers:

```
.devcontainer/
├── devcontainer.json       # Основная конфигурация Dev Container
├── docker-compose.yml      # Docker Compose конфигурация для dev среды
└── Dockerfile              # Dockerfile для dev container
```

### Компоненты

- **devcontainer.json**: Определяет настройки контейнера, расширения VS Code, переменные окружения и команды
- **docker-compose.yml**: Оркестрирует dev container и зависимые сервисы (PostgreSQL, Redis, RabbitMQ)
- **Dockerfile**: Определяет образ контейнера с Python 3.13, uv и необходимыми инструментами

## Предварительные требования

### Общие требования

1. **Docker Desktop** (для Windows/Mac) или **Docker Engine** (для Linux)
   - Минимальная версия: 20.10+
   - Docker Compose: 2.0+ (входит в Docker Desktop)

2. **Git** (для клонирования репозитория)

### Для VS Code

1. **Visual Studio Code** версии 1.74.0 или новее
2. **Расширение "Dev Containers"** от Microsoft
   - Устанавливается автоматически при первом открытии проекта
   - Или вручную: `ms-vscode-remote.remote-containers`

### Для PyCharm

1. **PyCharm Professional** версии 2023.1 или новее
   - Dev Containers поддерживаются только в Professional версии
   - Community Edition не поддерживает Dev Containers

## Настройка VS Code

### Шаг 1: Установка расширения

1. Откройте VS Code
2. Перейдите в раздел расширений (`Ctrl+Shift+X` / `Cmd+Shift+X`)
3. Найдите "Dev Containers" от Microsoft
4. Нажмите "Install"

### Шаг 2: Открытие проекта в контейнере

#### Способ 1: Через командную палитру (рекомендуется)

1. Откройте проект в VS Code: `File → Open Folder...`
2. Нажмите `F1` или `Ctrl+Shift+P` (`Cmd+Shift+P` на Mac)
3. Введите "Dev Containers: Reopen in Container"
4. Выберите команду из списка
5. Дождитесь сборки контейнера (первый раз может занять несколько минут)

#### Способ 2: Через кнопку в левом нижнем углу

1. Откройте проект в VS Code
2. В левом нижнем углу появится зелёная кнопка `><` (Remote Window)
3. Нажмите на неё и выберите "Reopen in Container"
4. Дождитесь сборки контейнера

### Шаг 3: Проверка работы

После открытия контейнера:

1. Откройте встроенный терминал (`Ctrl+`` ` / `Cmd+`` `)
2. Выполните:
   ```bash
   python --version  # Должно показать Python 3.13.x
   uv --version      # Должно показать версию uv
   ```
3. Проверьте, что зависимости установлены:
   ```bash
   uv sync --all-extras
   ```

### Шаг 4: Запуск приложения

1. Убедитесь, что все сервисы запущены (они должны запуститься автоматически):
   - PostgreSQL (порт 5432)
   - Redis (порт 6379)
   - RabbitMQ (порт 5672, Management на 15672)

2. Запустите приложение:
   ```bash
   python -m uvicorn src.presentation.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. Откройте браузер: http://localhost:8000

### Использование расширений

После открытия в контейнере будут автоматически установлены расширения:

- **Python** (`ms-python.python`) - поддержка Python
- **Pylance** (`ms-python.vscode-pylance`) - языковой сервер Python
- **Black Formatter** (`ms-python.black-formatter`) - форматирование кода
- **Ruff** (`charliermarsh.ruff`) - линтер и форматтер
- **Docker** (`ms-azuretools.vscode-docker`) - работа с Docker

### Отладка

1. Создайте файл `.vscode/launch.json` (если его нет):
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Python: FastAPI",
         "type": "python",
         "request": "launch",
         "module": "uvicorn",
         "args": [
           "src.presentation.main:app",
           "--host",
           "0.0.0.0",
           "--port",
           "8000",
           "--reload"
         ],
         "jinja": true,
         "justMyCode": false
       }
     ]
   }
   ```

2. Установите breakpoint в коде
3. Нажмите `F5` или выберите "Run → Start Debugging"

## Настройка PyCharm

### Шаг 1: Установка Docker

Убедитесь, что Docker Desktop запущен и работает корректно.

### Шаг 2: Открытие проекта через Dev Container

#### Способ 1: С экрана приветствия (рекомендуется для нового проекта)

1. Запустите PyCharm Professional
2. На экране приветствия выберите "Remote Development"
3. Выберите "Dev Containers"
4. Нажмите "Next"
5. Укажите путь к проекту (папка, содержащая `.devcontainer`)
6. PyCharm автоматически обнаружит `devcontainer.json`
7. Нажмите "Build Container and Continue"
8. Дождитесь сборки контейнера (первый раз может занять несколько минут)

#### Способ 2: Из открытого проекта

1. Откройте проект в PyCharm: `File → Open...`
2. Перейдите: `File → Settings → Build, Execution, Deployment → Docker`
3. Убедитесь, что Docker настроен корректно
4. Перейдите: `File → Settings → Project → Python Interpreter`
5. Нажмите на шестерёнку → "Add Interpreter" → "On Docker Compose"
6. Выберите `docker-compose.yml` из папки `.devcontainer`
7. Выберите сервис `devcontainer`
8. Укажите путь к интерпретатору: `/app/.venv/bin/python`
9. Нажмите "OK"

### Шаг 3: Настройка интерпретатора

1. Перейдите: `File → Settings → Project → Python Interpreter`
2. Убедитесь, что выбран интерпретатор из контейнера
3. Интерпретатор должен быть: `/app/.venv/bin/python`

### Шаг 4: Запуск приложения

1. Создайте конфигурацию запуска:
   - `Run → Edit Configurations...`
   - Нажмите `+` → "Python"
   - Имя: "FastAPI"
   - Script path: оставьте пустым
   - Module name: `uvicorn`
   - Parameters: `src.presentation.main:app --host 0.0.0.0 --port 8000 --reload`
   - Python interpreter: выберите интерпретатор из контейнера

2. Нажмите "OK" и запустите конфигурацию

### Шаг 5: Отладка

1. Создайте конфигурацию отладки аналогично конфигурации запуска
2. Установите breakpoint
3. Нажмите `Shift+F9` или `Run → Debug 'FastAPI'`

### Доступ к сервисам

Все сервисы доступны по тем же хостам, что и в основном `docker-compose.yml`:

- **PostgreSQL**: `postgres:5432`
- **Redis**: `redis:6379`
- **RabbitMQ**: `rabbitmq:5672`
- **RabbitMQ Management**: `http://localhost:15672` (guest/guest)

## Полезные команды

### Работа с контейнером

```bash
# Проверка статуса сервисов
docker compose -f .devcontainer/docker-compose.yml ps

# Просмотр логов
docker compose -f .devcontainer/docker-compose.yml logs -f

# Перезапуск контейнера
# В VS Code: Command Palette → "Dev Containers: Rebuild Container"
# В PyCharm: остановите и запустите контейнер заново
```

### Установка зависимостей

```bash
# Установка всех зависимостей
uv sync --all-extras

# Добавление новой зависимости
uv add package-name

# Добавление dev зависимости
uv add --dev package-name
```

### Работа с базой данных

```bash
# Подключение к PostgreSQL
psql -h postgres -U postgres -d production_control

# Запуск миграций
alembic upgrade head

# Создание новой миграции
alembic revision --autogenerate -m "description"
```

## Переменные окружения

Переменные окружения настраиваются через `.env` файл в корне проекта. В Dev Container используются следующие значения по умолчанию:

```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=production_control
DB_USER=postgres
DB_PASSWORD=postgres
DB_SCHEMA=public

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/

LOG_LEVEL=INFO
```

## Устранение проблем

### Контейнер не запускается

1. Проверьте, что Docker запущен
2. Проверьте логи: `docker compose -f .devcontainer/docker-compose.yml logs`
3. Пересоберите контейнер: `docker compose -f .devcontainer/docker-compose.yml build --no-cache`

### Проблемы с интерпретатором Python

1. Убедитесь, что виртуальное окружение создано: `uv sync --all-extras`
2. Проверьте путь к интерпретатору: `/app/.venv/bin/python`
3. В PyCharm: перезагрузите интерпретатор в настройках

### Проблемы с портами

Если порты заняты:

1. Остановите другие контейнеры, использующие те же порты
2. Или измените маппинг портов в `devcontainer.json`:
   ```json
   "forwardPorts": [8001, 5433, 6378, 5673, 15673]
   ```

### Проблемы с зависимостями

1. Переустановите зависимости: `uv sync --all-extras --force`
2. Очистите кеш: `uv cache clean`
3. Пересоберите контейнер

### Медленная работа файловой системы (Windows/Mac)

Используйте Docker Desktop с включённой опцией "Use VirtioFS" (в настройках Docker Desktop).

## Дополнительные ресурсы

- [Официальная документация Dev Containers](https://containers.dev/)
- [VS Code Dev Containers документация](https://code.visualstudio.com/docs/devcontainers/containers)
- [PyCharm Docker Support](https://www.jetbrains.com/help/pycharm/docker.html)
- [Docker Compose документация](https://docs.docker.com/compose/)

## Отличия от основного docker-compose.yml

Dev Container использует отдельный `docker-compose.yml` в папке `.devcontainer` по следующим причинам:

1. **Изоляция**: Dev Container не конфликтует с основными сервисами
2. **Разные сети**: используется отдельная сеть `production-control-devcontainer-network`
3. **Отдельные volumes**: данные хранятся в отдельных томах (префикс `devcontainer-`)
4. **Оптимизация для разработки**: контейнер настроен для разработки, а не для production

Основной `docker-compose.yml` можно использовать одновременно с Dev Container для запуска production-like окружения.





