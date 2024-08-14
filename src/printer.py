import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtPrintSupport as QtPrintSupport
import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
from tabs.create_distilling_tab import CreateDistillingTab
import constants
import config
import calculations
import db

WORD_WRAP_CENTER = QtGui.QTextOption(QtCore.Qt.AlignmentFlag.AlignCenter)
WORD_WRAP_CENTER.setWrapMode(QtGui.QTextOption.WrapMode.WordWrap)

WORD_WRAP_LEFT = QtGui.QTextOption(QtCore.Qt.AlignmentFlag.AlignLeft)
WORD_WRAP_LEFT.setWrapMode(QtGui.QTextOption.WrapMode.WordWrap)

WORD_WRAP_RIGHT = QtGui.QTextOption(QtCore.Qt.AlignmentFlag.AlignRight)
WORD_WRAP_RIGHT.setWrapMode(QtGui.QTextOption.WrapMode.WordWrap)

WORD_WRAP = QtGui.QTextOption()
WORD_WRAP.setWrapMode(QtGui.QTextOption.WrapMode.WordWrap)

VERTICAL_SPACER = 10
HORIZONTAL_SPACER = 10

TABLE_VERTICAL_MARGIN = 3
TABLE_HORIZONTAL_MARGIN = 2


class OrderPrinter:
    class TablePrint:
        def __init__(
            self,
            painter: QtGui.QPainter,
            data: list[list[str]],
            rect: QtCore.QRectF,
            stretch: bool = True,
            title: str = None,
        ) -> None:
            super().__init__()
            self.painter = painter
            self.rows = data
            self.cols = list(zip(*data))
            self.rect = rect
            self.stretch = stretch
            self.title = title
            self.fairDistribute()

        def fairDistribute(self):
            even_col_size = QtCore.QSizeF(
                self.rect.width() / len(self.cols) - 2 * TABLE_HORIZONTAL_MARGIN,
                self.rect.height(),
            )

            self.cols_size = [
                max(
                    [
                        self.painter.boundingRect(
                            QtCore.QRectF(QtCore.QPointF(), even_col_size),
                            text,
                            WORD_WRAP,
                        )
                        .size()
                        .width()
                        for text in col
                    ]
                )
                for col in self.cols
            ]
            aditional_space = (self.rect.width() - sum(self.cols_size)) / len(
                self.cols_size
            )
            if self.stretch:
                self.cols_size = [col + aditional_space for col in self.cols_size]

            self.rows_size = [
                max(
                    [
                        self.painter.boundingRect(
                            QtCore.QRectF(
                                QtCore.QPointF(),
                                QtCore.QSizeF(col_size, self.rect.height()),
                            ),
                            text,
                            WORD_WRAP,
                        )
                        .size()
                        .height()
                        + 2 * TABLE_VERTICAL_MARGIN
                        for text, col_size in zip(row, self.cols_size)
                    ]
                )
                for row in self.rows
            ]

            if self.title:
                self.rect.setHeight(
                    sum(self.rows_size)
                    + self.painter.boundingRect(
                        self.rect, self.title, WORD_WRAP_LEFT
                    ).height()
                )
            else:
                self.rect.setHeight(sum(self.rows_size))

        def paintCell(self, rect, text):
            rect = QtCore.QRectF(rect)
            self.painter.drawRect(rect)
            rect.setLeft(rect.left() + TABLE_HORIZONTAL_MARGIN)
            rect.setRight(rect.right() - TABLE_HORIZONTAL_MARGIN)
            rect.setTop(rect.top() + TABLE_VERTICAL_MARGIN)
            rect.setBottom(rect.bottom() - TABLE_VERTICAL_MARGIN)
            self.painter.drawText(rect, text, WORD_WRAP_CENTER)

        def paint(self):
            rect = QtCore.QRectF(self.rect)
            if self.title:
                title_rect = self.painter.boundingRect(
                    self.rect, self.title, WORD_WRAP_LEFT
                )
                self.painter.drawText(title_rect, self.title, WORD_WRAP_LEFT)
                rect.setTop(rect.top() + title_rect.height())

            for row, row_size in zip(self.rows, self.rows_size):
                rect.setHeight(row_size)
                rect.setLeft(self.rect.left())
                for cell_text, col_size in zip(row, self.cols_size):
                    rect.setWidth(col_size)
                    self.paintCell(rect, cell_text)
                    rect.moveLeft(rect.left() + col_size)
                rect.moveTop(rect.top() + row_size)

    def __init__(self) -> None:
        super().__init__()
        pass

    def print_order(self, window: CreateDistillingTab, order: db.Order):
        printer = QtPrintSupport.QPrinter()
        painter = QtGui.QPainter()

        # printer.setOutputFileName("prueba.pdf")
        # printer.setOutputFormat(QtPrintSupport.QPrinter.OutputFormat.PdfFormat)

        # printer.setPageMargins(0.0, 0.0, 0.0, 0.0, QtGui.QPageLayout.Unit.Point)
        # printer.setFullPage(True)
        # margin = printer.(QPageLayout.Unit.Point)

        printer.setPageSize(QtGui.QPageSize(QtGui.QPageSize.PageSizeId.A4))
        printer.setPageOrientation(QtGui.QPageLayout.Orientation.Portrait)
        printer.setCopyCount(config.config.get("printer", {}).get("copy_count"))
        printer.setPageMargins(
            QtCore.QMarginsF(4.0, 4.0, 4.0, 4.0), QtGui.QPageLayout.Unit.Point
        )

        painter.begin(printer)
        painter.setPen(QtGui.QPen(QtGui.QColor().black(), 1.1))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)

        # painter.setBrush(QtGui.QColorConstants.White)

        layout = printer.pageLayout().paintRectPixels(printer.resolution()).toRectF()
        layout.setHeight(layout.height() / 2)
        self.paint_order(painter, window, layout, order)
        painter.end()

    def paint_order(
        self,
        painter: QtGui.QPainter,
        window: CreateDistillingTab,
        layout: QtCore.QRectF,
        order: db.Order = None,
    ):
        def print_header():
            nonlocal layout

            contact = "www.palenicasmizany.sk\ntel.č: 0905530298"
            address = "Pestovateľská pálenica, Hviezdoslavova 959, 053 11 Smižany\nJozef Szabó, Tatranská 20 053 11 Smižany"
            id_number = "IČO: 37179845\nIČ DPH: SK1026735831"
            title = f"VYSKLADŇOVACÍ LIST / DAŇOVÝ DOKLAD č.: {order.mark}/{order.production_date.strftime(r'%Y')}/{order.production_line.name}"

            rect = QtCore.QRectF(layout)
            header_height = max(
                painter.boundingRect(rect, contact, WORD_WRAP_LEFT).height(),
                painter.boundingRect(rect, address, WORD_WRAP_CENTER).height(),
                painter.boundingRect(rect, id_number, WORD_WRAP_RIGHT).height(),
            )

            rect.setHeight(header_height)

            painter.drawText(rect, contact, WORD_WRAP_LEFT)
            painter.drawText(rect, address, WORD_WRAP_CENTER)
            painter.drawText(rect, id_number, WORD_WRAP_RIGHT)

            rect.setTop(rect.bottom() + VERTICAL_SPACER)
            rect.setBottom(layout.bottom())
            save_font = QtGui.QFont(painter.font())

            title_font = QtGui.QFont(save_font)
            title_font.setBold(True)
            title_font.setPointSize(save_font.pointSize() + 3)
            painter.setFont(title_font)

            title_height = painter.boundingRect(rect, title, WORD_WRAP_CENTER).height()
            rect.setHeight(title_height)
            painter.drawText(rect, title, WORD_WRAP_CENTER)

            painter.setFont(save_font)

            rect.setTop(layout.top())
            layout.setTop(rect.bottom())
            return rect

        def number_by_word(num: int) -> str:
            known_numbers = {
                0: "nula",
                1: "jeden",
                2: "dva",
                3: "tri",
                4: "štyri",
                5: "päť",
                6: "šesť",
                7: "sedem",
                8: "osem",
                9: "deväť",
                10: "desať",
                11: "jedenásť",
                12: "dvanásť",
                13: "trinásť",
                14: "štrnásť",
                15: "pätnásť",
                16: "šestnásť",
                17: "sedemnásť",
                18: "osemnásť",
                19: "devätnásť",
                20: "dvadsať",
                30: "tridsať",
                40: "štyridsať",
                50: "päťdesiat",
                60: "šesťdesiat",
                70: "sedemdesiat",
                80: "osemdesiat",
                90: "deväťdesiat",
                100: "sto",
                200: "dvesto",
                300: "tristo",
                400: "štyristo",
                500: "päťsto",
                600: "šesťsto",
                700: "sedemsto",
                800: "osemsto",
                900: "deväťsto",
                1000: "tisíc",
            }

            if num in known_numbers:
                return known_numbers[num]

            if num < 100:
                return f"{known_numbers[num // 10 * 10]}{known_numbers[num % 10]}"
            elif num < 1000:
                return f"{known_numbers[num // 100 * 100]} {number_by_word(num % 100) if num % 100 else ''}"
            elif num < 1000000:
                return f"{number_by_word(num // 1000) if num // 1000 != 1 else ''}{known_numbers[1000]} {number_by_word(num % 1000) if num % 1000 else ''}"

            return "veľa"

        def print_footer():
            nonlocal layout

            price_sum = order.cost_sum

            confirmation = "Svojím podpisom potvrdzujem prevzatie a zaplatenie nezávadného destilátu."
            sign_customer = "_____________________________\nPodpis pestovateľa"
            sign_employee = "_____________________________\nPodpis prevádzkovateľa"
            cost_words = f"Spolu zaplatené slovom: {number_by_word(int(price_sum))} eur a {int(price_sum*100%100)} centov"
            production_date = f"Dátum výroby destilátu: {order.production_date.strftime(constants.DATE_FORMAT)}"
            pickup_date = "Dátum prevzatia destilátu: ______________________"

            dates = f"{cost_words}\n\n{production_date}\n\n{pickup_date}"

            rect = QtCore.QRectF(layout)
            height = painter.boundingRect(rect, confirmation, WORD_WRAP_CENTER).height()
            rect.setTop(rect.bottom() - height)
            painter.drawText(rect, confirmation, WORD_WRAP_CENTER)

            rect_employee = QtCore.QRectF(layout)
            rect_employee.setLeft(rect.left() + rect.width() * 3 / 4)
            rect_customer = QtCore.QRectF(layout)
            rect_customer.setLeft(rect.left() + rect.width() * 2 / 4)
            rect_customer.setRight(rect.right() - rect.width() * 1 / 4)
            height = max(
                painter.boundingRect(
                    rect_customer, sign_customer, WORD_WRAP_CENTER
                ).height(),
                painter.boundingRect(
                    rect_employee, sign_employee, WORD_WRAP_CENTER
                ).height(),
            )

            rect_employee.setTop(rect.top() - height)
            rect_customer.setTop(rect.top() - height)
            rect_employee.setBottom(rect.top())
            rect_customer.setBottom(rect.top())
            rect.setTop(rect.top() - height)

            painter.drawText(rect_customer, sign_customer, WORD_WRAP_CENTER)
            painter.drawText(rect_employee, sign_employee, WORD_WRAP_CENTER)

            rect.setTop(rect_customer.top())

            dates_rect = QtCore.QRectF(layout)
            dates_rect = painter.boundingRect(dates_rect, dates, WORD_WRAP_LEFT)
            dates_rect.moveBottom(rect.top())

            painter.drawText(dates_rect, dates, WORD_WRAP_LEFT)

            rect.setTop(dates_rect.top())

            pass

        def paint_customer(rect: QtCore.QRectF) -> QtCore.QRectF:
            texts = [
                [
                    (
                        f"Meno a priezvisko: ",
                        f"{order.customer.name}",
                    ),
                    (
                        f"Dátum narodenia: ",
                        f"{order.customer.birthday.strftime(constants.DATE_FORMAT)}",
                    ),
                ],
                [
                    (
                        f"Adresa: ",
                        f"{order.customer.address}",
                    ),
                    (
                        f"Telefónne číslo: ",
                        f"{order.customer.phone_number}",
                    ),
                ],
                [
                    (
                        f"Množstvo la pred pálením: ",
                        f"{window.customer_handler.le_la_before.text()}",
                    ),
                    (
                        f"Množstvo la po pálení: ",
                        f"{window.customer_handler.le_la_after.text()}",
                    ),
                ],
            ]

            # set pen to bold
            save_font = painter.font()
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)

            row_bound = QtCore.QRectF(rect)

            for row in texts:
                row_bounds = [
                    (
                        painter.boundingRect(
                            QtCore.QRectF(
                                pair_bound.left(),
                                pair_bound.top(),
                                pair_bound.width() / 2,
                                pair_bound.height(),
                            ),
                            pair_texts[0],
                            WORD_WRAP_RIGHT,
                        ),
                        painter.boundingRect(
                            QtCore.QRectF(
                                pair_bound.left() + pair_bound.width() / 2,
                                pair_bound.top(),
                                pair_bound.width() / 2,
                                pair_bound.height(),
                            ),
                            pair_texts[1],
                            WORD_WRAP_LEFT,
                        ),
                    )
                    for pair_bound, pair_texts in zip(
                        [
                            QtCore.QRectF(
                                row_bound.left() + i * row_bound.width() / len(row),
                                row_bound.top(),
                                row_bound.width() / len(row),
                                row_bound.height(),
                            )
                            for i in range(len(row))
                        ],
                        row,
                    )
                ]

                row_height = max(
                    [
                        max(pair_bound[0].height(), pair_bound[1].height())
                        for pair_bound in row_bounds
                    ]
                )

                for pair_bound, pair_texts in zip(row_bounds, row):
                    pair_bound[0].setHeight(row_height)
                    pair_bound[1].setHeight(row_height)
                    painter.drawText(pair_bound[0], pair_texts[0], WORD_WRAP_RIGHT)
                    painter.drawText(pair_bound[1], pair_texts[1], WORD_WRAP_LEFT)

                row_bound.setTop(row_bound.top() + row_height)

            rect.setBottom(row_bound.top())

            painter.setFont(save_font)

            painter.drawLine(rect.topLeft(), rect.topRight())
            painter.drawLine(rect.bottomLeft(), rect.bottomRight())

            return rect

        def paint_distillings(rect: QtCore.QRectF):
            distillings_header = [
                r"Množstvo prijatého kvasu v litroch",
                r"Druh prijatého kvasu",
                r"Množstvo vyrobeného destilátu v l",
                r"Zistené objemové %",
                r"Teplota destilátu (˚C)",
                r"Objemové % liehu pri 20˚C",
                r"Množstvo vyrobeného a prevzatého destilátu v la",
                r"Spotrebná daň s niššou sadzbou",
                r"Spotrebná dan s vyššou sadzbou",
                r"Suma spotrebnej dane v € zaplatenej pestovateľom",
            ]

            distillings = [
                [
                    f"{distilling.ferment_volume:.0f}",
                    distilling.ferment_type,
                    f"{distilling.alcohol_volume:.2f}",
                    f"{distilling.alcohol_percentage:.2f}",
                    f"{distilling.alcohol_temperature:.2f}",
                    f"{distilling.alcohol_percentage_at_20:.2f}",
                    f"{distilling.alcohol_volume_la:.2f}",
                    f"{distilling.lower_tax:.3f}",
                    f"{distilling.full_tax:.3f}",
                    f"{distilling.sum_tax:.3f}",
                ]
                for distilling in order.distillings
            ]

            table_distillings = self.TablePrint(
                painter, [distillings_header, *distillings], rect
            )
            table_distillings.paint()

            return table_distillings.rect

        def paint_dilute(rect: QtCore.QRectF):
            dilute_header = [f"{val * 100:.0f}%" for val in constants.DILUTE_TARGETS]
            dilute_cells = calculations.calculate_dillute_table(
                [
                    distilling.alcohol_percentage_at_20
                    for distilling in order.distillings
                ]
            )

            table_dilute = self.TablePrint(
                painter,
                [dilute_header, *dilute_cells],
                rect,
                title="Riedenie v dcl na 1 liter liehu:",
            )
            table_dilute.paint()

            return table_dilute.rect

        def paint_costs(rect: QtCore.QRectF):
            sum_la = sum(
                [distilling.alcohol_volume_la for distilling in order.distillings]
            )

            costs_cells = [
                [
                    "Cena za službu s DPH v €",
                    f"{order.service_cost:.2f}",
                ],
                [
                    "Ostatné náklady s DPH v €",
                    f"{order.operating_costs:.2f}",
                ],
                [
                    "Cena za liter 50%",
                    f"{calculations.calculate_cost_per_liter(order.cost_sum-order.operating_costs, sum_la):.2f}",
                ],
                ["Základ dane", f"{order.tax_base:.2f}"],
                ["DPH 20%", f"{order.tax_vat:.2f}"],
            ]

            cost_sum_cells = [
                ["Spolu zaplatené pestovateľom s DPH v €", f"{order.cost_sum:.2f}"]
            ]

            # set pen to bold

            costs_table = self.TablePrint(painter, costs_cells, rect, title=" ")
            costs_table.paint()

            rect.setTop(costs_table.rect.bottom())

            save_font = painter.font()
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)

            cost_sum_table = self.TablePrint(painter, cost_sum_cells, rect, title=" ")
            cost_sum_table.cols_size = costs_table.cols_size
            cost_sum_table.paint()

            painter.setFont(save_font)

            return costs_table.rect

        def paint_notes(rect: QtCore.QRectF):
            title = "Iné záznamy:"
            text = window.notes.toPlainText()

            title_rect = QtCore.QRectF(rect)
            title_rect = painter.boundingRect(title_rect, title, WORD_WRAP_LEFT)
            painter.drawText(title_rect, title, WORD_WRAP_LEFT)

            notes_rect = QtCore.QRectF(rect)
            notes_rect.setTop(title_rect.bottom())

            notes_rect.setLeft(notes_rect.left() + TABLE_HORIZONTAL_MARGIN)
            notes_rect.setRight(notes_rect.right() - TABLE_HORIZONTAL_MARGIN)
            notes_rect.setTop(notes_rect.top() + TABLE_VERTICAL_MARGIN)
            notes_rect.setBottom(notes_rect.bottom() - TABLE_VERTICAL_MARGIN)

            notes_rect_height = painter.boundingRect(
                notes_rect, text, WORD_WRAP_LEFT
            ).height()
            notes_rect.setHeight(notes_rect_height)

            painter.drawText(notes_rect, text, WORD_WRAP_LEFT)

            notes_rect.setLeft(notes_rect.left() - TABLE_HORIZONTAL_MARGIN)
            notes_rect.setRight(notes_rect.right() + TABLE_HORIZONTAL_MARGIN)
            notes_rect.setTop(notes_rect.top() - TABLE_VERTICAL_MARGIN)
            notes_rect.setBottom(notes_rect.bottom() + TABLE_VERTICAL_MARGIN)

            painter.drawRect(notes_rect)
            rect.setBottom(notes_rect.bottom())

            return rect

        # Layout constant shift
        layout.setBottomRight(
            layout.bottomRight() - layout.topLeft() - layout.topLeft()
        )

        header_rect = print_header()
        footer_rect = print_footer()

        customer_rect = paint_customer(QtCore.QRectF(layout))

        distillings_rect = QtCore.QRectF(layout)
        distillings_rect.setTop(customer_rect.bottom() + VERTICAL_SPACER)
        distillings_rect = paint_distillings(distillings_rect)

        # increase font size
        save_font = painter.font()
        font = painter.font()
        font.setPointSize(save_font.pointSize() + 1)
        painter.setFont(font)

        dilute_rect = QtCore.QRectF(layout)
        dilute_rect.setTop(distillings_rect.bottom() + VERTICAL_SPACER)
        dilute_rect.setWidth(dilute_rect.size().width() / 4)
        dilute_rect = paint_dilute(dilute_rect)

        costs_rect = QtCore.QRectF(layout)
        costs_rect.setTop(distillings_rect.bottom() + VERTICAL_SPACER)
        costs_rect.setLeft(costs_rect.left() + costs_rect.size().width() * 2 / 3)
        costs_rect = paint_costs(costs_rect)

        notes_rect = QtCore.QRectF(layout)
        notes_rect.setTop(distillings_rect.bottom() + VERTICAL_SPACER)
        notes_rect.setLeft(dilute_rect.right() + HORIZONTAL_SPACER)
        notes_rect.setRight(costs_rect.left() - HORIZONTAL_SPACER)
        notes_rect = paint_notes(notes_rect)

        painter.setFont(save_font)

        pass
