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
# В secrets.env задайте LICENSING_ADMIN_PASSWORD=...
docker compose up --build
```

- На этой машине: http://localhost:8080/admin/login  
- **Из локальной сети** (другой ПК, сканер): `http://<IP-этого-хоста>:8080/admin/login`

Узнать IP (Linux):

```bash
hostname -I | awk '{print $1}'
```

Пример для сканера в той же сети:

```bash
export LICENSE_API_BASE_URL="http://192.168.1.50:8080"
```

Другой порт на хосте: `LICENSING_PORT=9080 docker compose up --build`

Если с других машин не открывается — проверьте файрвол (например `sudo ufw allow 8080/tcp`).

## API

```http
GET /v1/instances/{machine-id}/status
Authorization: Bearer aksec_...
```

Ответ: `status` = `active` | `expired` | `revoked` | `forbidden` | `not_found`.
