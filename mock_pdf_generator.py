import sys
import base64
import os
from io import BytesIO
from pprint import pformat
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
    Image, Table, TableStyle
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm


# === Конфигурация шрифтов ===
def register_font(path, name, default):
    try:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(name, path))
            return name
        else:
            return default
    except Exception:
        return default

FONT_NAME = register_font("./fonts/DejaVuSans.ttf", "DejaVuSans", "Helvetica")
FONT_NAME_MONO = register_font("./fonts/DejaVuSansMono.ttf", "DejaVuSansMono", "Courier")
FONT_NAME_MONO_BOLD = register_font("./fonts/DejaVuSansMono-Bold.ttf", "DejaVuSansMonoBold", "Courier")
PAGE_WIDTH, PAGE_HEIGHT = A4

# === Стили ===
styles = getSampleStyleSheet()
style_normal = ParagraphStyle(
    'StyleNormal',
    parent=styles["Normal"],
    fontName=FONT_NAME,
    # fontSize=10,
    # leading=14
)
style_h1 = ParagraphStyle(
    'StyleH1',
    parent=styles["Heading1"],
    fontName=FONT_NAME,
    # fontSize=16,
    # leading=20,
    alignment=1,
    spaceAfter=18,
    textColor=(0.3, 0.3, 0.3)
)
style_mono = ParagraphStyle(
    'StyleMono',
    parent=style_normal,
    fontSize=8,
    fontName=FONT_NAME_MONO,
    textColor=(0.2, 0.2, 0.6),
)
style_mono_header = ParagraphStyle(
    'StyleMonoHeader',
    parent=style_mono,
    fontName=FONT_NAME_MONO_BOLD,
    textColor=colors.black,
)

# === Класс для нумерации страниц ===
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(total_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, total):
        page = self._pageNumber
        self.setFont(FONT_NAME, 9)
        self.setFillColor(colors.gray)
        text = f"Страница {page} из {total} "
        self.drawCentredString(PAGE_WIDTH / 2.0, 1 * cm, text)

# === Колонтитул ===
def footer(canvas_obj: canvas.Canvas, doc):
    pass

# === Шаблон страницы ===
def create_page_template(doc):
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    return PageTemplate(id="template", frames=[frame], onPage=footer)

# === Отладочный блок ===
def add_debug_block(story, title, value, doc):
    story.append(Paragraph(f"<b>{title}</b>", style_mono_header))
    if isinstance(value, str):
        formatted = value
    else:
        formatted = ''.join(pformat(value, width=90, compact=False))
    for line in formatted.splitlines():
        story.append(Paragraph(line.replace(" ", "&nbsp;"), style_mono))

    story.append(Spacer(1, 4))
    line = Table([[""]], colWidths=[PAGE_WIDTH - 2 * doc.leftMargin], rowHeights=[0.5])
    line.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, -1), 0.5, colors.lightgrey)]))
    story.append(line)
    story.append(Spacer(1, 8))


# === Основная функция генерации PDF ===
def generate_pdf(request_headers, request_body):
    buffer = BytesIO()
    doc = BaseDocTemplate(buffer, pagesize=A4)
    doc.addPageTemplates([create_page_template(doc)])
    story = []

    # Заголовок
    story.append(Paragraph("Привет!", style_h1))
    story.append(Spacer(1, 12))

    # Основной текст и изображение
    image = Image("cats.png", width=7 * cm, height=5 * cm)
    center_text = Paragraph("Этот сервис находится в разработке.<br/><br/>"
                            "Но раз уж вы здесь...<br/>"
                            "Знакомьтесь, это мои котики.<br/>"
                            "Слева Котик, справа Кисуля.<br/><br/>"
                            "А внизу отладочная информация<br/>для разработчиков", 
                            style=style_normal)
    table = Table(
        [[center_text, image]],
        colWidths=[(PAGE_WIDTH - 2 * doc.leftMargin) / 2] * 2,
    )
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    # Заголовки запроса
    add_debug_block(story, "Заголовки запроса", request_headers, doc)

    # Тело запроса
    add_debug_block(story, "Тело запроса", request_body, doc)

    # Тело запроса в виде JSON
    try:
        request_json = json.loads(request_body)
    except Exception as e:
        request_json = f"Увы, тело запроса не соответствует формату JSON. {e}"
    add_debug_block(story, "Парсинг тела запроса как JSON", request_json, doc)

    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data


# === Пример данных для отладки ===
example_headers = {
    'accept': '*/*',
    'content-length': '20',
    'content-type': 'application/json',
    'host': '127.0.0.1:8000',
    'user-agent': 'curl/8.7.1'
}
example_body = """{
    "parameters": {
        "length": 10,
        "width": 12
    },
    "messages": [
        {
            "role": "system",
            "content": "Ты — глупый помощник, который помогает пользователю впустую провести время."
        },
        {
            "role": "user",
            "content": "Начни диалог и задай первый вопрос."
        },
        {
            "role": "assistant",
            "content": "Знаете ли вы почему коровы утратили способность летать?"
        }
    ],
    "scalar": 42
}"""


# === FastAPI-приложение ===
app = FastAPI(title="Mock PDF Generator")

@app.post("/")
async def generate_endpoint(request: Request):
    # Получаем данные запроса
    request_body = await request.body()

    # Заголовки запроса
    request_headers = dict(request.headers)

    # Генерация PDF
    response_payload = {
        "status": 200,
        "info": ["PDF успешно создан"],
        "errors": []
    }

    # Заголовки ответа
    headers_out = {"content-type": "application/json"}

    pdf_data = generate_pdf(
        request_headers=request_headers,
        request_body=request_body
    )
    response_payload["document"] = base64.b64encode(pdf_data).decode("utf-8")
    return JSONResponse(response_payload, headers=headers_out)


# === Точка входа ===
if __name__ == "__main__":
    if "--debug" in sys.argv:
        print("🧩 Отладочный режим: создаём PDF...")
        pdf_data = generate_pdf(example_headers, example_body)
        with open("example.pdf", "wb") as f:
            f.write(pdf_data)
        print("✅ PDF успешно сохранён как example.pdf")
    else:
        print("🚀 Запуск FastAPI сервиса...")
        uvicorn.run("mock_pdf_generator:app", host="0.0.0.0", port=8000)
