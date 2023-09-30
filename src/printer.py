import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtPrintSupport as QtPrintSupport
import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
import main_window
import constants

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


class OrderPrinter():

    class TablePrint():
        def __init__(self, painter: QtGui.QPainter, data: list[list[str]], rect: QtCore.QRectF, stretch: bool = True, title: str = None) -> None:
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
                self.rect.width() / len(self.cols) - 2*TABLE_HORIZONTAL_MARGIN, self.rect.height())

            self.cols_size = [max([self.painter.boundingRect(QtCore.QRectF(QtCore.QPointF(
            ), even_col_size), text, WORD_WRAP).size().width() for text in col]) for col in self.cols]
            aditional_space = (self.rect.width() -
                               sum(self.cols_size))/len(self.cols_size)
            if self.stretch:
                self.cols_size = [
                    col + aditional_space for col in self.cols_size]

            self.rows_size = [max([self.painter.boundingRect(QtCore.QRectF(QtCore.QPointF(), QtCore.QSizeF(col_size, self.rect.height(
            ))), text, WORD_WRAP).size().height()+2*TABLE_VERTICAL_MARGIN for text, col_size in zip(row, self.cols_size)]) for row in self.rows]

            if self.title:
                self.rect.setHeight(
                    sum(self.rows_size) + self.painter.boundingRect(self.rect, self.title, WORD_WRAP_LEFT).height())
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
                    self.rect, self.title, WORD_WRAP_LEFT)
                self.painter.drawText(title_rect, self.title, WORD_WRAP_LEFT)
                rect.setTop(rect.top() + title_rect.height())

            for row, row_size in zip(self.rows, self.rows_size):
                rect.setHeight(row_size)
                rect.setLeft(self.rect.left())
                for cell_text, col_size in zip(row, self.cols_size):
                    rect.setWidth(col_size)
                    self.paintCell(rect, cell_text)
                    rect.moveLeft(rect.left()+col_size)
                rect.moveTop(rect.top()+row_size)

    def __init__(self) -> None:
        super().__init__()
        pass

    def print_order(self, window: main_window.MainWindow):
        printer = QtPrintSupport.QPrinter()
        painter = QtGui.QPainter()

        # printer.setOutputFileName("prueba.pdf")
        # printer.setOutputFormat(QtPrintSupport.QPrinter.OutputFormat.PdfFormat)

        # printer.setPageMargins(0.0, 0.0, 0.0, 0.0, QtGui.QPageLayout.Unit.Point)
        # printer.setFullPage(True)
        # margin = printer.(QPageLayout.Unit.Point)

        printer.setPageSize(QtGui.QPageSize(QtGui.QPageSize.PageSizeId.A4))
        printer.setPageOrientation(QtGui.QPageLayout.Orientation.Portrait)
        printer.setCopyCount(2)
        printer.setPageMargins(QtCore.QMarginsF(
            4.0, 4.0, 4.0, 4.0), QtGui.QPageLayout.Unit.Point)

        painter.begin(printer)
        painter.setPen(QtGui.QPen(QtGui.QColor().black(), 1.1))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)

        # painter.setBrush(QtGui.QColorConstants.White)

        layout = printer.pageLayout().paintRectPixels(printer.resolution()).toRectF()
        layout.setHeight(layout.height()/2)
        self.paint_order(painter, window, layout)
        painter.end()

    def paint_order(self, painter: QtGui.QPainter, window: main_window.MainWindow, layout: QtCore.QRectF):

        def print_header():
            nonlocal layout

            contact = "www.palenicasmizany.sk\ntel.č: 0905530298"
            address = "Pestovateľská pálenica, Hviezdoslavova 959, 053 11 Smižany\nJozef Szabó, Tatranská 20 053 11 Smižany"
            id_number = "IČO: 37179845\nIČ DPH: SK1026735831"
            title = f"VYSKLADŇOVACÍ LIST / DAŇOVÝ DOKLAD č.: {window.le_mark.text()}/{window.production_date.strftime(r'%Y')}/{window.cb_production_line.currentText()}"

            rect = QtCore.QRectF(layout)
            header_height = max(painter.boundingRect(rect, contact, WORD_WRAP_LEFT).height(),
                                painter.boundingRect(
                rect, address, WORD_WRAP_CENTER).height(),
                painter.boundingRect(rect, id_number, WORD_WRAP_RIGHT).height())

            rect.setHeight(header_height)

            painter.drawText(rect, contact, WORD_WRAP_LEFT)
            painter.drawText(rect, address, WORD_WRAP_CENTER)
            painter.drawText(rect, id_number, WORD_WRAP_RIGHT)

            rect.setTop(rect.bottom() + VERTICAL_SPACER)
            rect.setBottom(layout.bottom())
            save_font = QtGui.QFont(painter.font())

            title_font = QtGui.QFont(save_font)
            title_font.setBold(True)
            title_font.setPointSize(save_font.pointSize()+3)
            painter.setFont(title_font)

            title_height = painter.boundingRect(
                rect, title, WORD_WRAP_CENTER).height()
            rect.setHeight(title_height)
            painter.drawText(rect, title, WORD_WRAP_CENTER)

            painter.setFont(save_font)

            rect.setTop(layout.top())
            layout.setTop(rect.bottom())
            return rect

        def print_footer():
            nonlocal layout

            confirmation = "Svojím podpisom potvrdzujem prevzatie a zaplatenie nezávadného destilátu."
            sign_customer = "_____________________________\nPodpis pestovateľa"
            sign_employee = "_____________________________\nPodpis prevádzkovateľa"
            cost_words = f"Spolu zaplatené slovom: __________________________"
            production_date = f"Dátum výroby destilátu: {window.production_date.strftime(constants.DATE_FORMAT)}"
            pickup_date = "Dátum prevzatia destilátu: ______________________"

            dates = f"{cost_words}\n\n{production_date}\n\n{pickup_date}"

            rect = QtCore.QRectF(layout)
            height = painter.boundingRect(
                rect, confirmation, WORD_WRAP_CENTER).height()
            rect.setTop(rect.bottom() - height)
            painter.drawText(
                rect, confirmation, WORD_WRAP_CENTER)

            rect_employee = QtCore.QRectF(layout)
            rect_employee.setLeft(rect.left()+rect.width()*3/4)
            rect_customer = QtCore.QRectF(layout)
            rect_customer.setLeft(rect.left()+rect.width()*2/4)
            rect_customer.setRight(rect.right()-rect.width()*1/4)
            height = max(
                painter.boundingRect(rect_customer, sign_customer,
                                     WORD_WRAP_CENTER).height(),
                painter.boundingRect(rect_employee, sign_employee,
                                     WORD_WRAP_CENTER).height())

            rect_employee.setTop(rect.top() - height)
            rect_customer.setTop(rect.top() - height)
            rect_employee.setBottom(rect.top())
            rect_customer.setBottom(rect.top())
            rect.setTop(rect.top()-height)

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

            painter.drawLine(rect.topLeft(), rect.topRight())

            name_address_label = QtCore.QRectF(rect.topLeft(), QtCore.QSizeF(
                rect.size().width()/4, rect.size().height()))
            name_address_text = QtCore.QRectF(name_address_label.topRight(), QtCore.QSizeF(
                rect.size().width()/4, rect.size().height()))

            birthday_phone_label = QtCore.QRectF(name_address_text.topRight(), QtCore.QSizeF(
                rect.size().width()/4, rect.size().height()))

            birthday_phone_text = QtCore.QRectF(birthday_phone_label.topRight(), QtCore.QSizeF(
                rect.size().width()/4, rect.size().height()))

            name_height = max(painter.boundingRect(name_address_label, f"{window.customer_handler.label_name.text()} ",
                                                   WORD_WRAP_RIGHT).height(),
                              painter.boundingRect(name_address_text, f"{window.customer_handler.le_name.text()}",
                                                   WORD_WRAP_LEFT).height()
                              )

            painter.drawText(name_address_label, f"{window.customer_handler.label_name.text()} ",
                             WORD_WRAP_RIGHT)
            painter.drawText(name_address_text, f"{window.customer_handler.le_name.text()}",
                             WORD_WRAP_LEFT)

            name_address_label.setTop(name_address_label.top()+name_height)
            name_address_text.setTop(name_address_text.top()+name_height)

            address_height = max(painter.boundingRect(name_address_label, f"{window.customer_handler.label_address.text()} ",
                                                      WORD_WRAP_RIGHT).height(),
                                 painter.boundingRect(name_address_text, f"{window.customer_handler.le_address.text()}",
                                                      WORD_WRAP_LEFT).height()
                                 )
            painter.drawText(name_address_label, f"{window.customer_handler.label_address.text()} ",
                             WORD_WRAP_RIGHT)
            painter.drawText(name_address_text, f"{window.customer_handler.le_address.text()}",
                             WORD_WRAP_LEFT)

            birthday_height = max(painter.boundingRect(birthday_phone_label, f"{window.customer_handler.label_birthday.text()} ",
                                                       WORD_WRAP_RIGHT).height(),
                                  painter.boundingRect(birthday_phone_text, f"{window.customer_handler.le_birthday.text()}",
                                                       WORD_WRAP_LEFT).height()
                                  )

            painter.drawText(birthday_phone_label, f"{window.customer_handler.label_birthday.text()} ",
                             WORD_WRAP_RIGHT)
            painter.drawText(birthday_phone_text, f"{window.customer_handler.le_birthday.text()}",
                             WORD_WRAP_LEFT)

            birthday_phone_label.setTop(
                birthday_phone_label.top()+birthday_height)
            birthday_phone_text.setTop(
                birthday_phone_text.top()+birthday_height)

            phone_height = max(painter.boundingRect(birthday_phone_label, f"{window.customer_handler.label_phone_number.text()} ",
                                                    WORD_WRAP_RIGHT).height(),
                               painter.boundingRect(birthday_phone_text, f"{window.customer_handler.cb_phone_number.currentText()}",
                                                    WORD_WRAP_LEFT).height()
                               )
            painter.drawText(birthday_phone_label, f"{window.customer_handler.label_phone_number.text()} ",
                             WORD_WRAP_RIGHT)
            painter.drawText(birthday_phone_text, f"{window.customer_handler.cb_phone_number.currentText()}",
                             WORD_WRAP_LEFT)

            rect.setHeight(max(name_height+address_height,
                           phone_height+birthday_height))

            painter.drawLine(rect.bottomLeft(), rect.bottomRight())

            return rect

        def paint_la(rect: QtCore.QRectF):
            pass

        def paint_distillings(rect: QtCore.QRectF):
            distillings_header = [
                window.label_ferment_volume.text(),
                window.label_ferment_type.text(),
                window.label_alcohol_volume.text(),
                window.label_alcohol_percentage.text(),
                window.label_alcohol_temperature.text(),
                window.label_alcohol_percentage_at_20.text(),
                window.label_alcohol_volume_la.text(),
                window.label_lower_tax.text(),
                window.label_full_tax.text(),
                window.label_sum_tax.text(),
            ]

            distillings = [[distilling.edit_ferment_volume.text(),
                            distilling.edit_ferment_type.text(),
                            f"{distilling.alcohol_volume:.2f}",
                            f"{distilling.alcohol_percentage:.2f}",
                            f"{distilling.alcohol_temperature:.2f}",
                            distilling.edit_alcohol_percentage_at_20.text(),
                            distilling.edit_alcohol_volume_la.text(),
                            distilling.edit_lower_tax.text(),
                            distilling.edit_full_tax.text(),
                            distilling.edit_sum_tax.text(),
                            ] for distilling in window.findChildren(main_window.DistillingInput)]

            table_distillings = self.TablePrint(
                painter, [distillings_header, *distillings], rect)
            table_distillings.paint()

            return table_distillings.rect

        def paint_dilute(rect: QtCore.QRectF):
            dilute_cols = window.diluteTable.columnCount()
            dilute_rows = window.diluteTable.rowCount()
            dilute_header = [window.diluteTable.horizontalHeaderItem(
                i).text() for i in range(dilute_cols)]
            dilute_cells = [[window.diluteTable.item(row, col).text(
            ) for col in range(dilute_cols)]for row in range(dilute_rows)]

            table_dilute = self.TablePrint(
                painter, [dilute_header, *dilute_cells], rect, title="Riedenie v dcl na 1 liter liehu:")
            table_dilute.paint()

            return table_dilute.rect

        def paint_costs(rect: QtCore.QRectF):
            costs_cells = [
                [window.label_service_cost.text(
                ), window.rle_service_cost.lineEdit.text()],
                [window.label_operating_costs.text(
                ), window.rle_operating_costs.lineEdit.text()],
                [window.label_cost_per_liter.text(), window.le_cost_per_liter.text()],
                [window.label_cost_sum.text(), window.le_cost_sum.text()],
                [window.label_tax_base.text(), window.le_tax_base.text()],
                [window.label_tax.text(), window.le_tax_vat.text()],
            ]

            costs_table = self.TablePrint(
                painter, costs_cells, rect, title=" ")
            costs_table.paint()

            return costs_table.rect

        def paint_notes(rect: QtCore.QRectF):
            title="Iné záznamy"
            text = window.notes.toPlainText()

            title_rect = QtCore.QRectF(rect)
            title_rect = painter.boundingRect(title_rect, title, WORD_WRAP_LEFT)
            painter.drawText(title_rect,title, WORD_WRAP_LEFT)

            notes_rect = QtCore.QRectF(rect)
            notes_rect.setTop(title_rect.bottom())
            
            notes_rect.setLeft(notes_rect.left() + TABLE_HORIZONTAL_MARGIN)
            notes_rect.setRight(notes_rect.right() - TABLE_HORIZONTAL_MARGIN)
            notes_rect.setTop(notes_rect.top() + TABLE_VERTICAL_MARGIN)
            notes_rect.setBottom(notes_rect.bottom() - TABLE_VERTICAL_MARGIN)
            
            notes_rect_height = painter.boundingRect(notes_rect, text, WORD_WRAP_LEFT).height()
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
        layout.setBottomRight(layout.bottomRight() -
                              layout.topLeft() - layout.topLeft())

        header_rect = print_header()
        footer_rect = print_footer()

        customer_rect = paint_customer(QtCore.QRectF(layout))

        distillings_rect = QtCore.QRectF(layout)
        distillings_rect.setTop(customer_rect.bottom() + VERTICAL_SPACER)
        distillings_rect = paint_distillings(distillings_rect)

        dilute_rect = QtCore.QRectF(layout)
        dilute_rect.setTop(distillings_rect.bottom() + VERTICAL_SPACER)
        dilute_rect.setWidth(dilute_rect.size().width()/4)
        dilute_rect = paint_dilute(dilute_rect)

        costs_rect = QtCore.QRectF(layout)
        costs_rect.setTop(distillings_rect.bottom() + VERTICAL_SPACER)
        costs_rect.setLeft(costs_rect.left() + costs_rect.size().width()*2/3)
        costs_rect = paint_costs(costs_rect)

        notes_rect = QtCore.QRectF(layout)
        notes_rect.setTop(distillings_rect.bottom() + VERTICAL_SPACER)
        notes_rect.setLeft(dilute_rect.right()+HORIZONTAL_SPACER)
        notes_rect.setRight(costs_rect.left() - HORIZONTAL_SPACER)
        notes_rect = paint_notes(notes_rect)

        pass
