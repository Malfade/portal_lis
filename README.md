# Ak-Shumkar licensing portal

Веб-портал и HTTP API для онлайн-проверки лицензии сканером (`LICENSE_MODE=remote` в `start.sh`).

## Деплой на Vercel

**Root Directory** в настройках проекта Vercel: `licensing-portal` (если репозиторий — весь `ak-shumkar-VM`).

### Обязательные переменные (Settings → Environment Variables)

| Переменная | Пример |
|------------|--------|
| `LICENSING_ADMIN_PASSWORD` | пароль входа в `/admin/login` |
| `LICENSING_SESSION_SECRET` | `openssl rand -hex 32` |

### База данных

Подключите **Vercel Postgres** (Storage) — переменные `POSTGRES_URL` / `DATABASE_URL` подхватываются **автоматически**.

Либо задайте вручную:

```text
LICENSING_DATABASE_URL=postgresql+psycopg2://...
```

(можно вставить `postgres://...` из Vercel — конвертируется в коде).

**Важно:** после смены переменных нажмите **Redeploy** (Vercel показывает уведомление).

### Деплой только с актуального коммита

В логе сборки должно быть **не** `ad740b0`, а коммит с `pyproject.toml` и `app/admin_routes.py`.  
Deployments → выберите последний коммит на `main` → **Redeploy**.

### Проверка после деплоя

1. `https://ваш-проект.vercel.app/health` → `{"status":"ok"}`
2. `https://ваш-проект.vercel.app/admin/login` — вход с `LICENSING_ADMIN_PASSWORD`

### Сканер

```bash
export LICENSE_MODE=remote
export LICENSE_API_BASE_URL='https://ваш-проект.vercel.app'
export LICENSE_API_TOKEN='aksec_...'
./security/licensectl.sh remote-check
```

### Почему был 500 FUNCTION_INVOCATION_FAILED

Типичные причины:

1. Не заданы `LICENSING_ADMIN_PASSWORD` / `LICENSING_SESSION_SECRET`.
2. Неверный **Root Directory** (должен быть каталог с `api/index.py` и `requirements.txt`).
3. Отсутствовал модуль `app/admin_routes.py` или папка `templates/`.
4. SQLite без внешней БД — нестабильно на serverless.

Логи: Vercel → Project → Deployments → Functions → View logs.

## Локально (Docker)

```bash
cp secrets.env.example secrets.env
# отредактируйте secrets.env
docker compose up --build
```

UI: http://localhost:8080/admin/login

## API

```http
GET /v1/instances/{machine-id}/status
Authorization: Bearer aksec_...
```

Ответ: `status` = `active` | `expired` | `revoked` | `forbidden` | `not_found`.
