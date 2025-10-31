#!/bin/bash

# Скрипт для запуска Docker-контейнера mock-pdf-generator

# Проверяем наличие Docker
if ! command -v docker &> /dev/null
then
    echo "Docker не найден. Пожалуйста, установите Docker."
    exit 1
fi

# Название образа
IMAGE_NAME="mock-pdf-generator"

# Версия образа (по умолчанию latest)
VERSION=${1:-latest}

# Порт хоста (по умолчанию 8000)
HOST_PORT=${2:-8000}

# Порт контейнера (по умолчанию 8000)
CONTAINER_PORT=8000

echo "Запуск контейнера $IMAGE_NAME:$VERSION на порту $HOST_PORT..."

# Проверяем, запущен ли уже контейнер с таким именем
if [ "$(docker ps -q -f name=$IMAGE_NAME)" ]; then
    echo "Контейнер с именем $IMAGE_NAME уже запущен. Останавливаем..."
    docker stop $IMAGE_NAME
fi

# Удаляем предыдущий контейнер, если он существует
if [ "$(docker ps -aq -f name=$IMAGE_NAME)" ]; then
    echo "Удаление предыдущего контейнера..."
    docker rm $IMAGE_NAME
fi

# Запуск контейнера
docker run -d \
    --name $IMAGE_NAME \
    -p $HOST_PORT:$CONTAINER_PORT \
    $IMAGE_NAME:$VERSION

if [ $? -eq 0 ]; then
    echo "Контейнер $IMAGE_NAME:$VERSION успешно запущен!"
    echo "Сервис доступен по адресу: http://localhost:$HOST_PORT"
    echo "Для остановки контейнера используйте:"
    echo "  docker stop $IMAGE_NAME"
else
    echo "Ошибка при запуске контейнера!"
    exit 1
fi