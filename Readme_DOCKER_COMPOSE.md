Отлично 👍
Ниже — пример `docker-compose.yml` и описание для `README.md` под ваш стек.

---

## 📄 **docker-compose.yml**

```yaml
version: "3.9"

services:
  # === Бэкенд (FastAPI) ===
  backend:
    build: ./ai_backend
    container_name: ai_backend
    restart: always
    env_file:
      - ./ai_backend/.env
    depends_on:
      - db
      - mailhog
    volumes:
      - ./ai_backend/static/uploads:/app/static/uploads
    ports:
      - "8000:8000"
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # === Фронтенд (Nuxt3) ===
  frontend:
    build: ./frontend
    container_name: nuxt_frontend
    restart: always
    env_file:
      - ./frontend/.env
    depends_on:
      - backend
    ports:
      - "3000:3000"
    command: npm run dev

  # === PostgreSQL ===
  db:
    image: postgres:15
    container_name: postgres_db
    restart: always
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppassword
      POSTGRES_DB: appdb
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # === Mailhog (почтовый клиент) ===
  mailhog:
    image: mailhog/mailhog
    container_name: mailhog
    restart: always
    ports:
      - "1025:1025"  # SMTP
      - "8025:8025"  # Web UI

  # === Nginx + Let's Encrypt ===
  nginx:
    image: nginx:alpine
    container_name: nginx_proxy
    restart: always
    depends_on:
      - backend
      - frontend
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./certbot/www:/var/www/certbot
      - ./certbot/conf:/etc/letsencrypt
    ports:
      - "80:80"
      - "443:443"

  certbot:
    image: certbot/certbot
    container_name: certbot
    volumes:
      - ./certbot/www:/var/www/certbot
      - ./certbot/conf:/etc/letsencrypt
    entrypoint: /bin/sh
    command: >
      -c "trap exit TERM;
          while :; do
            certbot renew --webroot -w /var/www/certbot;
            sleep 12h & wait $${!};
          done;"

  # === Prometheus ===
  prometheus:
    image: prom/prometheus
    container_name: prometheus
    restart: always
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  # === Grafana ===
  grafana:
    image: grafana/grafana
    container_name: grafana
    restart: always
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
    ports:
      - "3001:3000"  # графана UI

volumes:
  db_data:
```

---

## 📄 **README.md (пример)**

````markdown
# 🚀 Проект: AI Backend + Nuxt Frontend

Полноценный стек для AI-приложения:
- **Backend**: FastAPI (SQLModel, JWT, Yandex LLM)
- **Frontend**: Nuxt 3 + Bulma
- **DB**: PostgreSQL
- **Mail**: Mailhog для тестовой почты
- **Monitoring**: Prometheus + Grafana
- **Reverse Proxy + HTTPS**: Nginx + Certbot (Let's Encrypt)

---

## 📦 Установка

1. Склонируйте репозиторий и подготовьте `.env` в `ai_backend` и `frontend` (см. примеры в коде выше).

2. Создайте каталоги для томов:
```bash
mkdir -p nginx/conf.d certbot/www certbot/conf prometheus
````

3. Добавьте конфиг Nginx в `nginx/conf.d/default.conf` (пример ниже):

```nginx
server {
    listen 80;
    server_name example.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location /api/ {
        proxy_pass http://backend:8000/;
    }

    location / {
        proxy_pass http://frontend:3000/;
    }
}
```

4. Пример конфига Prometheus `prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
```

---

## ▶️ Запуск

```bash
docker compose up -d --build
```

* Бэкенд: [http://localhost:8000](http://localhost:8000)
* Фронтенд: [http://localhost:3000](http://localhost:3000)
* Mailhog UI: [http://localhost:8025](http://localhost:8025)
* Prometheus: [http://localhost:9090](http://localhost:9090)
* Grafana: [http://localhost:3001](http://localhost:3001)

---

## 📨 Почта

Для тестов письма регистрации уходят через `mailhog` (SMTP `localhost:1025`), интерфейс доступен на `http://localhost:8025`.

---

## 📊 Мониторинг

* **Prometheus** собирает метрики с backend.
* **Grafana** подключается к Prometheus по адресу `http://prometheus:9090`.

---

## 🔒 HTTPS

* Certbot автоматически обновляет сертификаты Let's Encrypt.
* Настройте `server_name` в `nginx/conf.d/default.conf` на ваш домен.
* Первую выдачу сертификата можно сделать:

```bash
docker compose run --rm certbot certonly --webroot -w /var/www/certbot -d example.com
```

---

## 🔑 Полезные команды

```bash
docker compose logs -f backend
docker compose exec db psql -U appuser -d appdb
docker compose down -v
```

---

## 📝 Структура

* `ai_backend/` — FastAPI + SQLModel
* `frontend/` — Nuxt 3 + Bulma
* `nginx/` — конфиги для nginx + certbot
* `prometheus/` — конфиги Prometheus

```

---

Хочешь, чтобы я сразу добавил пример `Dockerfile` для **backend** и **frontend**, чтобы `docker-compose` мог их собрать?
```
Отлично 🚀
Вот как можно сделать минимальные `Dockerfile` под ваш проект, чтобы тот `docker-compose.yml`, который я скинул выше, сразу собирался:

---

### 📄 **ai\_backend/Dockerfile** (FastAPI backend)

```dockerfile
# Базовый образ Python
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Скопировать requirements (или pyproject.toml, если Poetry)
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY . .

# Экспонируем порт
EXPOSE 8000

# Запуск uvicorn (но в docker-compose мы его переопределяем)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

> ⚠️ Убедитесь, что у вас есть `requirements.txt` в `ai_backend/`
> (или замените установку на Poetry/Pipenv, если используете их).

---

### 📄 **frontend/Dockerfile** (Nuxt3 frontend)

```dockerfile
# Стадия 1: build
FROM node:20-alpine as build

WORKDIR /app

# Установить зависимости
COPY package*.json ./
RUN npm install

# Скопировать исходники
COPY . .

# Сборка (production)
RUN npm run build

# Стадия 2: production
FROM node:20-alpine

WORKDIR /app

COPY --from=build /app/.output ./.output
COPY --from=build /app/node_modules ./node_modules

EXPOSE 3000

# Запуск Nuxt в продакшн-режиме
CMD ["node", ".output/server/index.mjs"]
```

> ⚠️ Если вы хотите запускать в dev-режиме, как было в `docker-compose` (`npm run dev`), можно убрать вторую стадию и оставить только первую. Но в проде лучше именно так.

---

### В `docker-compose.yml` (чтобы использовать Dockerfile):

```yaml
services:
  backend:
    build: ./ai_backend
    ...

  frontend:
    build: ./frontend
    ...
```

(как у нас уже указано выше)

---

### Пример `requirements.txt` (минимум)

```txt
fastapi
uvicorn[standard]
sqlmodel
psycopg2-binary
python-jose[cryptography]
passlib[bcrypt]
email-validator
httpx
pydantic[email]
```

(добавьте туда все свои зависимости)

---

Теперь достаточно:

```bash
docker compose up -d --build
```

и всё поднимется 🎉
---

Коротко и по делу:

- Да, Certbot/Let’s Encrypt выдают сертификаты только для реального домена, доступного из интернета. Для localhost сертификат от LE получить нельзя.
- Для локального https лучше всего сделать dev‑сертификат через mkcert (или самоподписанный). Ниже — самый простой рабочий вариант.

Сделаем локальный HTTPS на https://localhost через mkcert

1) Установите mkcert
- Сайт: https://github.com/FiloSottile/mkcert
- macOS: brew install mkcert nss
- Windows: choco install mkcert (или scoop install mkcert)
- Linux: установите libnss3-tools, скачайте бинарник mkcert со страницы релизов и поместите в PATH

2) Сгенерируйте сертификат для localhost
В терминале:
- mkcert -install
- mkcert localhost 127.0.0.1 ::1

Появятся два файла, типа localhost+2.pem и localhost+2-key.pem.

3) Положите сертификаты в проект
- Создайте папку: ./nginx/certs
- Переименуйте/скопируйте файлы:
  - ./nginx/certs/localhost.pem
  - ./nginx/certs/localhost-key.pem

4) Обновите docker-compose для nginx
Добавьте монтирование сертификатов (и убедитесь, что 443 прокинут):
- в сервис nginx добавьте volume: - ./nginx/certs:/etc/nginx/certs:ro
- порты уже есть "80:80" и "443:443" — оставить

Пример фрагмента:
nginx:
  image: nginx:alpine
  container_name: nginx_proxy
  restart: always
  depends_on:
    - backend
    - frontend
  volumes:
    - ./nginx/conf.d:/etc/nginx/conf.d:ro
    - ./nginx/certs:/etc/nginx/certs:ro
  ports:
    - "80:80"
    - "443:443"

(Локально certbot не нужен — можно временно убрать сервис certbot и его volume’ы, чтобы не путали.)

5) Замените конфиг nginx (./nginx/conf.d/default.conf)
server {
    listen 80;
    server_name localhost;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name localhost;

    ssl_certificate     /etc/nginx/certs/localhost.pem;
    ssl_certificate_key /etc/nginx/certs/localhost-key.pem;

    # важно для Nuxt/Vite HMR и прокси
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    client_max_body_size 50m;

    location /api/ {
        proxy_pass http://backend:8000/;
    }
    location / {
        proxy_pass http://frontend:3000/;
    }
}

6) Перезапустите nginx
- docker compose up -d nginx
- docker compose exec nginx nginx -t
- docker compose exec nginx nginx -s reload
Откройте https://localhost — должно работать через nginx.

Полезно знать:
- Если продолжает открываться http://localhost:3000 — вы просто заходите напрямую на Nuxt. Для проверки https всегда используйте https://localhost.
- Можно временно убрать публикацию портов 3000:3000 и 8000:8000, чтобы всё шло только через nginx.
- Если видите 502 Bad Gateway — проверьте, что backend и frontend контейнеры запущены: docker compose ps.

Хотите, пришлю готовые патчи к вашему docker-compose и конфигам ровно под ваш репозиторий? Скажи ОС (macOS/Windows/Linux) — дам точные команды установки mkcert.

---

Хочешь, чтобы я ещё добавил **примеры файлов** `nginx/conf.d/default.conf` и `prometheus/prometheus.yml` прямо готовые? (чтобы можно было скопировать и запускать без изменений)


* Бэкенд: [http://localhost:8000](http://localhost:8000)
* Фронтенд: [http://localhost:3000](http://localhost:3000)
* Mailhog UI: [http://localhost:8025](http://localhost:8025)
* Prometheus: [http://localhost:9090](http://localhost:9090)
* Grafana: [http://localhost:3001](http://localhost:3001)

docker compose up -d --build
docker compose logs -f backend frontend

## Adminer
👉 http://localhost:8081

Система: PostgreSQL
Сервер: db (имя сервиса из docker-compose)
Пользователь: appuser
Пароль: apppassword
База: appdb