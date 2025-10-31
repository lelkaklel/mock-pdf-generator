#!/bin/bash

# Скрипт для сборки Docker-образа mock-pdf-generator

# Проверяем наличие Docker
if ! command -v docker &> /dev/null
then
    echo "Docker не найден. Пожалуйста, установите Docker."
    exit 1
fi

# Название образа
IMAGE_NAME="ghcr.io/lelkaklel/mock-pdf-generator"

# Версия образа (по умолчанию latest)
VERSION=${1:-latest}

echo "Сборка Docker-образа $IMAGE_NAME:$VERSION..."

# Сборка образа
docker build --platform linux/amd64 -t $IMAGE_NAME:$VERSION .

if [ $? -eq 0 ]; then
    echo "Docker-образ $IMAGE_NAME:$VERSION успешно собран!"
    echo "Для запуска контейнера используйте:"
    echo "  docker run -p 8000:8000 $IMAGE_NAME:$VERSION"
else
    echo "Ошибка при сборке Docker-образа!"
    exit 1
fi