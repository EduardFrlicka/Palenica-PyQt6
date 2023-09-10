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


class OrderPrinter():

    class TablePrint():
        def __init__(self, painter: QtGui.QPainter, data: list[list[str]], rect: QtCore.QRectF, stretch: bool = True) -> None:
            super().__init__()
            self.painter = painter
            self.rows = data
            self.cols = list(zip(*data))
            self.rect = rect
            self.stretch = stretch
            self.fairDistribute()

        def fairDistribute(self):
            even_col_size = QtCore.QSizeF(
                self.rect.width() / len(self.cols), self.rect.height())

            self.cols_size = [max([self.painter.boundingRect(QtCore.QRectF(QtCore.QPointF(
            ), even_col_size), text, WORD_WRAP).size().width() for text in col]) for col in self.cols]
            aditional_space = (self.rect.width() -
                               sum(self.cols_size))/len(self.cols_size)
            if self.stretch:
                self.cols_size = [
                    col + aditional_space for col in self.cols_size]

            self.rows_size = [max([self.painter.boundingRect(QtCore.QRectF(QtCore.QPointF(), QtCore.QSizeF(col_size, self.rect.height(
            ))), text, WORD_WRAP).size().height() for text, col_size in zip(row, self.cols_size)]) for row in self.rows]

            self.rect.setHeight(sum(self.rows_size))

        def paintCell(self, rect, text):
            self.painter.drawRect(rect)
            self.painter.drawText(rect, text, WORD_WRAP_CENTER)

        def paint(self):
            rect = QtCore.QRectF(self.rect.topLeft(), QtCore.QSizeF())
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

        printer.setOutputFileName("prueba.pdf")
        printer.setOutputFormat(QtPrintSupport.QPrinter.OutputFormat.PdfFormat)

        # printer.setPageMargins(0.0, 0.0, 0.0, 0.0, QtGui.QPageLayout.Unit.Point)
        # printer.setFullPage(True)
        # margin = printer.(QPageLayout.Unit.Point)

        printer.setPageSize(QtGui.QPageSize(QtGui.QPageSize.PageSizeId.A5))
        printer.setPageOrientation(QtGui.QPageLayout.Orientation.Landscape)
        printer.setCopyCount(2)
        printer.setPageMargins(QtCore.QMarginsF(
            4.0, 4.0, 4.0, 4.0), QtGui.QPageLayout.Unit.Point)

        painter.begin(printer)
        painter.setPen(QtGui.QPen(QtGui.QColor().black(), 1.1))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)

        # painter.setBrush(QtGui.QColorConstants.White)

        self.paint_order(painter, window, printer.pageLayout(
        ).paintRectPixels(printer.resolution()).toRectF())
        painter.end()

    def paint_order(self, painter: QtGui.QPainter, window: main_window.MainWindow, layout: QtCore.QRectF):

        VERTICAL_SPACER = 5

        def print_header():
            nonlocal layout

            contact = "www.palenicasmizany.sk\ntel.č 0905530298"
            address = "Pestovateľská pálenica, Hviezdoslavova 959, 053 11 Smižany\nJozef Szabó, Tatranská 20 053 11 Smižany"
            id_number = "IČO: 37179845\nIČ DPH: SK1026735831"
            title = "VYSKLADŇOVACÍ LIST / DAŇOVÝ DOKLAD č.:"

            rect = QtCore.QRectF(layout)
            height = max(painter.boundingRect(rect, contact, WORD_WRAP_LEFT).height(),
                         painter.boundingRect(
                             rect, address, WORD_WRAP_CENTER).height(),
                         painter.boundingRect(rect, id_number, WORD_WRAP_RIGHT).height())

            rect.setHeight(height)

            painter.drawText(rect, contact, WORD_WRAP_LEFT)
            painter.drawText(rect, address, WORD_WRAP_CENTER)
            painter.drawText(rect, id_number, WORD_WRAP_RIGHT)

            layout.setTop(layout.top()+height)
            return rect

        def print_footer():
            nonlocal layout

            confirmation = "Svojím podpisom potvrdzujem prevzatie a zaplatenie nezávadného destilátu."
            sign_customer = "_____________________________\nPodpis pestovateľa"
            sign_employee = "_____________________________\nPodpis prevádzkovateľa"
            cost_words = f"Spolu zaplatené slovom: {0}"
            production_date = f"Dátum výroby destilátu: {window.production_date.strftime(constants.DATE_FORMAT)}"
            pickup_date = "Dátum prevzatia destilátu: ______________________"

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

            pass

        def paint_customer(rect: QtCore.QRectF = QtCore.QRectF(layout)) -> QtCore.QRectF:

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

        layout.setBottomRight(layout.bottomRight() -
                              layout.topLeft() - layout.topLeft())

        # rect = painter.boundingRect(layout.toRectF(
        # ), 10 * "abcdefg hijklmnzfcs gvbhjnkms cfzvg bhkmfscgbh ",  WORD_WRAP)
        # painter.drawRect(rect)
        # painter.drawText(
        #     rect, 10 * "abcdefg hijklmnzfcs gvbhjnkms cfzvg bhkmfscgbh ",  WORD_WRAP_CENTER)

        header_rect = print_header()
        foote_rect = print_footer()

        customer_rect = paint_customer(QtCore.QRectF(layout))

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
                        distilling.edit_alcohol_volume.text(),
                        distilling.edit_alcohol_percentage.text(),
                        distilling.edit_alcohol_temperature.text(),
                        distilling.edit_alcohol_percentage_at_20.text(),
                        distilling.edit_alcohol_volume_la.text(),
                        distilling.edit_lower_tax.text(),
                        distilling.edit_full_tax.text(),
                        distilling.edit_sum_tax.text(),
                        ] for distilling in window.findChildren(main_window.DistillingInput)]

        rect = QtCore.QRectF(layout)
        rect.setTop(customer_rect.bottom() + VERTICAL_SPACER)

        table_distillings = self.TablePrint(
            painter, [distillings_header, *distillings], rect)
        table_distillings.paint()

        rect = QtCore.QRectF(layout)
        rect.setTop(table_distillings.rect.bottom())
        rect.setRight(rect.right() - rect.size().width()*2/3)

        dilute_cols = window.diluteTable.columnCount()
        dilute_rows = window.diluteTable.rowCount()
        dilute_header = [window.diluteTable.horizontalHeaderItem(
            i).text() for i in range(dilute_cols)]
        dilute_cells = [[window.diluteTable.item(row, col).text(
        ) for col in range(dilute_cols)]for row in range(dilute_rows)]

        table_dilute = self.TablePrint(
            painter, [dilute_header, *dilute_cells], rect)
        table_dilute.paint()

        rect = QtCore.QRectF(layout)
        rect.setTop(table_distillings.rect.bottom())
        rect.setLeft(rect.left() + rect.size().width()*3/4)

        costs_cells = [
            [window.label_service_cost.text(), window.rle_service_cost.lineEdit.text()],
            [window.label_operating_costs.text(
            ), window.rle_operating_costs.lineEdit.text()],
            [window.label_cost_per_liter.text(), window.le_cost_per_liter.text()],
            [window.label_cost_sum.text(), window.le_cost_sum.text()],
            [window.label_tax_base.text(), window.le_tax_base.text()],
            [window.label_tax.text(), window.le_tax_vat.text()],
        ]

        costs_table = self.TablePrint(painter, costs_cells, rect)
        costs_table.paint()

        pass
