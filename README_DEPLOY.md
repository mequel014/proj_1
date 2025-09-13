Отлично! Давай сделаем простой, рабочий деплой на VDS с доменом и HTTPS от Let’s Encrypt. Ниже — минимальный, копипаст‑френдли план.

Что будет в итоге:
- Nginx на 80/443 с валидным SSL
- Backend (FastAPI) за прокси
- Frontend (Nuxt3) в проде, без npm run dev
- Картинки через https://yourdomain/static/uploads/
- База не торчит наружу

Шаг 0. Доменные записи
- Купи домен и укажи A-запись на IP VDS (например, yourdomain.com → 1.2.3.4).
- Подожди, пока DNS обновится (обычно до 30 минут).

Шаг 1. Установи Docker на сервере (Ubuntu)
- Подключись по SSH и выполни:
  - curl -fsSL https://get.docker.com | sh
  - sudo usermod -aG docker $USER
  - newgrp docker
  - docker --version && docker compose version

Шаг 2. Скопируй проект на сервер
- git clone ... или скопируй файлы любым образом.
- Проверь .env для фронта/бэка (для фронта достаточно NUXT_PUBLIC_API_BASE=/api).

Шаг 3. Dockerfile для Nuxt3 (прод)
Создай ai_frontend/Dockerfile, который собирает и запускает Nuxt в проде (SSR):
```dockerfile
# ai_frontend/Dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npx nuxi build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NITRO_PORT=3000
ENV PORT=3000
COPY --from=build /app/.output ./.output
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
```

Шаг 4. Продовый docker-compose override
Создай docker-compose.prod.yml (не правя dev-compose), чтобы в проде:
- фронт работал в prod‑режиме без volume
- db не публиковалась наружу
- adminer/grafana были доступны только через localhost (по SSH‑туннелю), а не из интернета
- nginx получил доступ к сертификатам и uploads

```yaml
# docker-compose.prod.yml
services:
  frontend:
    build: ./ai_frontend
    container_name: nuxt_frontend
    restart: always
    env_file:
      - ./ai_frontend/.env
    depends_on:
      - backend
    # В проде порт 3000 наружу НЕ публикуем — ходим через nginx

  backend:
    build: ./ai_backend
    container_name: ai_backend
    restart: always
    environment:
      - PYTHONPATH=/app/app
    env_file:
      - ./ai_backend/.env
    depends_on:
      - db
    volumes:
      - ./ai_backend/static/uploads:/app/static/uploads
    # В проде порт 8000 наружу НЕ публикуем
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="*"

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
    # В проде БД не публикуем наружу
    # ports: удалены

  adminer:
    image: adminer
    container_name: adminer
    restart: always
    depends_on:
      - db
    ports:
      - "127.0.0.1:8081:8080"  # доступ только через SSH-туннель

  grafana:
    image: grafana/grafana
    container_name: grafana
    restart: always
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
    ports:
      - "127.0.0.1:3001:3000"  # доступ только через SSH-туннель

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
      - ./ai_backend/static/uploads:/var/www/uploads:ro
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

volumes:
  db_data:
```

Шаг 5. Nginx конфиг: сначала HTTP, чтобы выпустить сертификат
Создай nginx/conf.d/default.conf (HTTP‑только, временно):
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # ACME challenge для выдачи сертификата
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Пока без редиректа на https, чтобы certbot прошел точно
    location /api/ { proxy_pass http://backend:8000/; }
    location /     { proxy_pass http://frontend:3000/; }
}
```

Подними стэк (без https пока):
- docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

Выпусти сертификаты:
- docker compose run --rm certbot certbot certonly --webroot -w /var/www/certbot -d yourdomain.com -d www.yourdomain.com --email you@example.com --agree-tos --no-eff-email

Шаг 6. Включаем HTTPS
Замени nginx/conf.d/default.conf на финальный (HTTPS + редирект + alias для uploads):
```nginx
# HTTP -> HTTPS + ACME
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    return 301 https://$host$request_uri;
}

# HTTPS
server {
    listen 443 ssl;
    http2 on;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # заголовки + WebSocket для Nuxt
    proxy_set_header Host                $host;
    proxy_set_header X-Real-IP           $remote_addr;
    proxy_set_header X-Forwarded-For     $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto   $scheme;
    proxy_set_header X-Forwarded-Host    $host;
    proxy_http_version 1.1;
    proxy_set_header Upgrade             $http_upgrade;
    proxy_set_header Connection          "upgrade";

    client_max_body_size 50m;

    # статика загрузок напрямую с диска
    location /static/uploads/ {
        alias /var/www/uploads/;
        add_header Cache-Control "public, max-age=3600";
    }

    location /api/ {
        proxy_pass http://backend:8000/;
    }

    location / {
        proxy_pass http://frontend:3000/;
    }
}
```

Проверка и перезагрузка nginx:
- docker compose exec nginx nginx -t
- docker compose exec nginx nginx -s reload

Готово: https://yourdomain.com должен работать.

Шаг 7. Важные примечания
- Frontend env: в ai_frontend/.env поставь
  - NUXT_PUBLIC_API_BASE=/api
- Бэк (FastAPI): убедись, что CORS (если включен) разрешает origin https://yourdomain.com. Uvicorn уже запущен с --proxy-headers.
- Обновления: деплой новой версии
  - git pull
  - docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build frontend backend
  - docker compose exec nginx nginx -s reload
- Adminer/Grafana: теперь доступны только через SSH‑туннель:
  - ssh -L 8081:127.0.0.1:8081 -L 3001:127.0.0.1:3001 user@your.vds.ip
  - Открой http://localhost:8081 и http://localhost:3001
- Бэкапы БД: настроить cron с pg_dump или использовать внешнюю систему бэкапов.

Хочешь, подставлю твой домен в конфиг и дам готовые команды ровно под твою ОС на сервере? Напиши домен и систему (Ubuntu/Debian/CentOS).