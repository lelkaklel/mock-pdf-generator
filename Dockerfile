# Используем официальный образ Python slim
FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем зависимости для работы с PDF и шрифтами
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY mock_pdf_generator.py .
COPY run_service.sh .
COPY cats.png .
COPY example.pdf .

# Создаем директорию для шрифтов и копируем их
RUN mkdir -p fonts
COPY fonts/ ./fonts/

# Делаем исполняемым скрипт запуска
RUN chmod +x run_service.sh

# Открываем порт
EXPOSE 8000

# Команда запуска приложения
CMD ["./run_service.sh"]