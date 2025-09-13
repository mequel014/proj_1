Ок, вот «шпаргалка», что делать после правок.

Если ты поменял только Vue-компонент (фронтенд)
- Ничего собирать не нужно: у тебя в docker-compose фронтенд монтирует папку проекта (./ai_frontend:/app) и крутится npm run dev. Nuxt подхватит изменения сам (HMR). Просто обнови страницу.
- Если менял .env фронта (например NUXT_PUBLIC_API_BASE), перезапусти контейнер фронта:
  - docker compose restart frontend
- Если совсем не подхватывается, перестрой только фронт:
  - docker compose up -d --build frontend
- Логи фронта:
  - docker compose logs -f frontend

Если менял конфиг nginx
- Проверить и перезагрузить:
  - docker compose exec nginx nginx -t
  - docker compose exec nginx nginx -s reload
- Или просто перезапустить:
  - docker compose restart nginx

Если менял бэкенд (FastAPI)
- Сейчас у тебя код бэкенда не примонтирован в контейнер (монтируется только uploads), поэтому изменения кода требуют пересборки образа:
  - docker compose up -d --build backend
- Хочешь «горячую» перезагрузку без сборки? Примонтируй исходники в backend и оставь --reload:
  1) В docker-compose для backend замени volumes на:
     - ./ai_backend:/app
  2) Перезапусти backend:
     - docker compose up -d backend
  Теперь любые правки в ai_backend будут подхватываться uvicorn’ом автоматически.

Если менял зависимости
- Фронт (package.json/lock): docker compose up -d --build frontend
- Бэк (requirements.txt/poetry.lock): docker compose up -d --build backend
- Полная пересборка всего: docker compose up -d --build

Полезные команды
- Статусы: docker compose ps
- Логи всех: docker compose logs -f
- Перезапуск сервиса: docker compose restart <service>
- Чистая сборка без кеша (когда совсем «залипло»):
  - docker compose build --no-cache frontend backend
  - docker compose up -d

Хочешь, я пришлю готовый diff для docker-compose (с примонтированием кода бэкенда) и для nginx, чтобы всё было «автообновляемо» в dev? Напиши, что именно правишь чаще — фронт, бэк или оба.