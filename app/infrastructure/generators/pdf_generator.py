from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


from app.domain.models.value_objects import ColumnDefinition, StylingConfig
from app.domain.repositories.generator import IFileGenerate


class PDFGenerator(IFileGenerate):
    def __init__(self):
        try:
            pdfmetrics.registerFont(
                TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
            )
            self.font_name = "DejaVu"
        except Exception:
            self.font_name = "Times-Roman"

    async def generate(
        self,
        data: list[dict[str, Any]],
        columns: list[ColumnDefinition],
        styling: StylingConfig | None = None,
    ):
        buffer = BytesIO()

        page_size = A4
        if styling and styling.orientation == "landscape":
            page_size = landscape(A4)
        else:
            page_size = portrait(A4)

        doc = SimpleDocTemplate(
            buffer,
            pagesize=page_size,
            leftMargin=1 * cm,
            rightMargin=1 * cm,
            topMargin=1 * cm,
            bottomMargin=1 * cm,
        )

        # Строим контент
        story: list[Any] = []
        self._add_title(story, styling)
        self._add_table(story, data, columns, styling)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _add_title(self, story: list, styling: StylingConfig | None) -> None:
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontName=self.font_name,
            fontSize=styling.font_size + 4 if styling and styling.font_size else 16,
            alignment=1,  # center
            spaceAfter=20,
        )
        title = Paragraph("Отчет", title_style)
        story.append(title)
        story.append(Spacer(1, 0.5 * cm))

    def _add_table(
        self,
        story: list,
        data: list[dict[str, Any]],
        columns: list[ColumnDefinition],
        styling: StylingConfig | None,
    ) -> None:
        """Добавляет таблицу с данными"""
        # Подготавливаем данные для таблицы
        table_data = []

        # Заголовки
        headers = [col.header for col in columns]
        table_data.append(headers)

        # Строки с данными
        for row_data in data:
            row = []
            for col in columns:
                value = row_data.get(col.field, "")
                # Форматируем значение если нужно
                if col.format and isinstance(value, (int, float)):
                    try:
                        value = format(value, col.format)
                    except Exception:
                        pass
                row.append(str(value) if value is not None else "")
            table_data.append(row)

        # Создаем таблицу
        table = Table(table_data, repeatRows=1)

        # Стили таблицы
        table_style = [
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ]

        header_bg = colors.HexColor("#4472C4")
        if styling and styling.header_bg_color:
            try:
                # Убеждаемся, что есть решетка
                color_str = styling.header_bg_color
                if not color_str.startswith("#"):
                    color_str = "#" + color_str
                header_bg = colors.HexColor(color_str)
            except (ValueError, AttributeError):
                pass

        header_font_color = colors.white
        if styling and styling.header_font_color:
            try:
                color_str = styling.header_font_color
                if not color_str.startswith("#"):
                    color_str = "#" + color_str
                header_font_color = colors.HexColor(color_str)
            except (ValueError, AttributeError):
                pass

        table_style.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), header_bg),
                ("TEXTCOLOR", (0, 0), (-1, 0), header_font_color),
                ("FONTNAME", (0, 0), (-1, 0), self.font_name),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, 0),
                    styling.font_size + 2 if styling and styling.font_size else 12,
                ),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
            ]
        )

        # Стиль данных
        table_style.extend(
            [
                ("FONTNAME", (0, 1), (-1, -1), self.font_name),
                (
                    "FONTSIZE",
                    (0, 1),
                    (-1, -1),
                    styling.font_size if styling and styling.font_size else 10,
                ),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
                ("TOPPADDING", (0, 1), (-1, -1), 5),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F2F2F2")],
                ),
            ]
        )

        table.setStyle(TableStyle(table_style))
        story.append(table)
