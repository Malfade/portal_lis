# Ak-Shumkar licensing portal

Веб-портал и HTTP API для **онлайн-проверки** лицензии сканером (`LICENSE_MODE=remote` в `start.sh`).

## Быстрый старт (Docker)

Из каталога `licensing-portal/`:

**Вариант A — файл `secrets.env`** (передаётся в контейнер через `env_file`; в `.gitignore`):

```bash
cp secrets.env.example secrets.env
# Укажите LICENSING_ADMIN_PASSWORD в secrets.env (символ $ в пароле допустим как есть).
docker compose up --build
```

**Вариант B — переменные в оболочке:**

```bash
export LICENSING_ADMIN_PASSWORD='your-secure-password'
export LICENSING_SESSION_SECRET="$(openssl rand -hex 32)"
docker compose up --build
```

- UI: `http://localhost:8080/admin/login`
- API: `GET /v1/instances/{instance_id}/status` с заголовком `Authorization: Bearer <токен сканера>`

В продакшене поставьте reverse proxy с TLS (HTTPS). Приложение слушает HTTP на порту **8080**.

## Переменные окружения

| Переменная | Описание |
|------------|----------|
| `LICENSING_DATABASE_URL` | SQLAlchemy URL. По умолчанию `sqlite:///./data/licensing.db` (локально) или в Docker `sqlite:////data/licensing.db`. Для PostgreSQL: `postgresql+psycopg2://user:pass@host/db` (добавьте драйвер в `requirements.txt`). |
| `LICENSING_ADMIN_PASSWORD` | Пароль входа в админ-UI. В Docker задайте в `secrets.env` (см. `env_file` в `docker-compose.yml`). |
| `LICENSING_SESSION_SECRET` | Секрет подписи cookie-сессии (обязательно уникальный в проде). |
| `LICENSING_RATE_LIMIT_PER_MINUTE` | Лимит запросов API на пару IP+`instance_id` в минуту (по умолчанию 120). |

## API для сканера

**Запрос:**

```http
GET /v1/instances/{instance_id}/status
Authorization: Bearer aksec_...
```

`instance_id` — значение `/etc/machine-id` на хосте сканера (без переводов строк).

**Ответ 200, JSON:**

```json
{"status":"active","expires_at":"2027-04-24T07:39:19Z","license_id":"...","customer_id":"..."}
```

`status`: `active` | `expired` | `revoked` | `forbidden` (несовпадение instance) | `not_found` (неверный токен или лицензия удалена).

Сканер принимает только `status == active` и проверяет `expires_at` в UTC.

## Админ-поток

1. Войти в `/admin/login`.
2. Создать клиента.
3. На карточке клиента создать лицензию (дата окончания UTC, опционально `instance_id`).
4. «Выпустить токен сканера» — один раз показывается plaintext; сохраните в секрет-хранилище.
5. Если `instance_id` у лицензии пустой, при **первом** успешном check он будет записан автоматически (привязка к машине).

## Интеграция со сканером

На хосте сканера задайте:

```bash
export LICENSE_MODE=remote
export LICENSE_API_BASE_URL='https://license.example.com'   # без завершающего слэша
export LICENSE_API_TOKEN='aksec_...'
./start.sh
```

Подробнее: [../PRODUCTION_LICENSE_AND_ACCESS.md](../PRODUCTION_LICENSE_AND_ACCESS.md).

## Разработка без Docker

```bash
cd licensing-portal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export LICENSING_ADMIN_PASSWORD=dev
uvicorn app.main:app --reload --port 8080
```

Тесты:

```bash
pytest -q
```
# portal_lis
