# Outbox Processor

[![Docker Build](https://img.shields.io/badge/docker-build-blue)](https://hub.docker.com/)  
Outbox Processor — это микросервис, который проверяет таблицу `outbox` в базе данных на наличие сообщений со статусом `pending` или `failed`, публикует их в NATS и обновляет статус в зависимости от результата отправки.

## Описание
Сервис реализует следующий алгоритм:
1. Подключается к базе данных и выбирает сообщения со статусом `pending` или `failed`.
2. Публикует сообщения в NATS.
3. Обновляет статус сообщений в базе данных:
   - `sent` — если сообщение успешно отправлено.
   - `failed` — если произошла ошибка при отправке.
4. Повторяет процесс после задержки в `n` секунд.

## Требования
Для работы сервиса необходимы:
- PostgreSQL (с таблицей `outbox`)
- NATS Server
- Docker (опционально)

### Структура таблицы `outbox`
Таблица должна иметь следующие поля:
- `id` (PK): Уникальный идентификатор сообщения.
- `status`: Статус сообщения (`pending`, `failed`, `sent`).
- `payload`: Данные для отправки (JSON или строка).
- `created_at`: Время создания записи.
- `updated_at`: Время последнего обновления.


## Установка и запуск

### 1. Локальная разработка
Клонируйте репозиторий:
```bash
git clone https://github.com/RPleshkov/OutboxProcessor.git
cd outbox-processor
```

Установите зависимости (если используются):
```bash
poetry config virtualenvs.in-project true
poetry install
```

Настройте переменные окружения (см. раздел "Конфигурация").

Запустите сервис:
```bash
python main.py
```

### 2. Запуск через Docker
Соберите Docker-образ:
```bash
docker build -t outbox-processor .
```

Запустите контейнер:
```bash
docker run -d \
  --name outbox-processor \
  -e ENV_DB__URL=postgresql+psycopg2://user:password@postgres:5432/test \
  -e NATS_URL=nats://nats-server:4222 \
  -e PROCESS_DELAY=60 \
  outbox-processor
```

## Конфигурация
Сервис использует переменные окружения для настройки. Вот список доступных параметров:

| Переменная       | Описание                                 |
|------------------|------------------------------------------|
| `DB_URL`         | URL подключения к PostgreSQL             |
| `NATS_URL`       | URL NATS сервера                         |
| `PROCESS_DELAY`  | Задержка между итерациями (в секундах)   |



