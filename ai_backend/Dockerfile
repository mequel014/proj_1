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