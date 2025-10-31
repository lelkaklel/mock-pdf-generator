# Mock PDF Generator

Сервис-заглушка для генерации PDF-документов

## Описание

Этот сервис предоставляет REST API endpoint для генерации PDF-документов. Он принимает JSON-данные в теле POST-запроса и возвращает PDF-документ в формате base64.

## Запуск сервиса

### Локальный запуск

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Запустите сервис:
   ```bash
   uvicorn mock_pdf_generator:app --reload --port ${MPG_PORT:-8000}
   ```

   По умолчанию сервис будет доступен по адресу `http://localhost:8000`, порт можно указать с помощью переменной среды MPG_PORT.

### Запуск с помощью Docker

#### Сборка Docker-образа

Для сборки Docker-образа выполните скрипт:

```bash
./build_docker.sh
```

Вы также можете указать конкретную версию образа:

```bash
./build_docker.sh v1.0
```

#### Запуск Docker-контейнера

Для запуска контейнера выполните следующую команду:

```bash
docker run -p 8000:8000 ghcr.io/lelkaklel/mock-pdf-generator
```

## Использование API

Отправьте POST-запрос на корневой endpoint (`/`) с любыми JSON-данными в теле запроса:

```bash
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, World!", "data": [1, 2, 3]}'
```

Либо, чтобы сохранить файл на диск:

```bash
curl -s -X POST http://localhost:8000 \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello, World!", "data": [1, 2, 3]}' \
| jq -r '.document' \
| base64 --decode > test.pdf
```

Сервис вернет ответ в формате JSON с PDF-документом в кодировке base64:

```json
{
  "status": 200,
  "info": ["PDF успешно создан"],
  "errors": [],
  "document": "JVBERi0xLjQKJcOkw7zDtsO..."
}
```

## Структура проекта

- `mock_pdf_generator.py` - основной файл сервиса
- `requirements.txt` - зависимости Python
- `cats.png` - изображение для PDF
- `fonts/` - директория со шрифтами (спасибо )
- `Dockerfile` - конфигурация Docker-образа
- `build_docker.sh` - скрипт сборки Docker-образаDocker-контейнера

## Зависимости

- Python 3.7+
- FastAPI
- Uvicorn
- ReportLab
Полный список указан в `requirements.txt`

## Шрифты

В проекте использованы шрифры [DejaVu](https://dejavu-fonts.github.io)

## Лицензия

MIT
