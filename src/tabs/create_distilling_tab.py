from PyQt6.QtWidgets import (
    QLineEdit,
    QTableWidgetItem,
    QMessageBox,
    QTabBar,
    QPushButton,
)
from PyQt6.QtCore import QDate, QVariant, Qt, pyqtSignal
from ui_py.create_distilling_tab_ui import Ui_CreateDistillingTab
import resources
from widgets.distilling_input import DistillingInput
from datetime import datetime
from constants import DATE_FORMAT
from dialogs.customer_select import CustomerSelectDialog
from sqlalchemy.orm import Session
from datetime import date
import config
import db
import messages
from dialogs.alert import alert
import dialogs.order_edit as order_edit
import calculations


class CreateDistillingTab(Ui_CreateDistillingTab, QTabBar):
    """The distilling form, in one of two modes.

    With no `order_id` it is the "Nová destilácia" tab and saving inserts a new
    order. With one it is an editor for that order, opened from the distillings
    tab: the same widgets, the same calculation chain, but saving updates the
    stored order and a Zmazať button removes it. `order_closed` tells whoever
    opened the editor that it is finished.
    """

    order_closed = pyqtSignal()

    def __init__(self, order_id: int = None):
        super().__init__()
        self.setupUi(self)
        self.order_id = order_id
        self.label_year.setText(f"/{date.today().year}")
        self.date_reset()
        self.calculation_constants = db.CalculationConstants.get()
        self.cb_production_line.clear()
        self.cb_production_line.addItems([line.name for line in db.get_production_lines()])
        if self.order_id is None:
            self.add_distilling_input()
        self.show_tax_rates()
        self.reset_button_date.clicked.connect(self.date_reset)
        self.button_add_distilling_input.clicked.connect(self.add_distilling_input)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.rle_operating_costs.setDefault(0.0)
        self.rle_operating_costs.textEdited.connect(self.update_costs)
        self.rle_service_cost.textEdited.connect(self.update_costs)
        self.setWindowState(Qt.WindowState.WindowMaximized)

        for button_name, enabled in config.config.get(
            "create_distilling_tab_buttons"
        ).items():
            button: QPushButton = getattr(self, button_name)
            button.setEnabled(enabled)
            if not enabled:
                button.hide()

        # Deleting is only meaningful for an order that already exists.
        self.button_Delete.setVisible(self.order_id is not None)

        if self.order_id is not None:
            self.load_order()

    def show_tax_rates(self):
        self.label_lower_tax.setText(f"Suma spotrebnej dane {self.calculation_constants.lower_tax:.3f} €/la")
        self.label_full_tax.setText(f"Suma spotrebnej dane {self.calculation_constants.full_tax:.3f} €/la")

    def load_order(self):
        """Fill the form from the stored order so it can be edited in place."""
        with db.get_session() as session:
            order = db.get_order(self.order_id, session)
            if order is None:
                alert(messages.ORDER_NOT_FOUND)
                return

            # An order keeps the rates it was priced with. Recalculating it
            # against today's constants would silently reprice a doklad that has
            # already been printed and paid.
            self.calculation_constants = order.constants
            session.expunge(self.calculation_constants)
            self.show_tax_rates()

            self.le_mark.setText(order.mark)
            self.label_year.setText(f"/{order.production_date.year}")
            self.dateEdit.setDate(QDate(order.production_date))
            self.production_date = order.production_date

            line_index = self.cb_production_line.findText(order.production_line.name)
            if line_index != -1:
                self.cb_production_line.setCurrentIndex(line_index)

            # Not the customer's season total: the litres of this very order must
            # not count towards its own excise limit, or every re-save would push
            # it a tier higher.
            la_before = db.get_customer_la_before(
                order.customer, order, order.season, session
            )
            customer = order.customer
            session.expunge(customer)
            self.customer_handler.load_customer(customer, la=la_before)
            self.customer_handler.show_customer()
            # Reassigning a booked doklad to somebody else is not an edit - it is
            # a different order - so the customer is fixed once it exists.
            self.customer_handler.pushButton.hide()

            for distilling in order.distillings:
                self.add_distilling_input().load_distilling(distilling)

            self.rle_service_cost.setValue(order.service_cost)
            self.rle_operating_costs.setValue(order.operating_costs)
            self.update_costs()

    def add_distilling_input(self):
        new_distilling_input = DistillingInput(parent=self, calculation_constants=self.calculation_constants)
        new_distilling_input.setObjectName("distilling_input")
        new_distilling_input.tax_edited.connect(self.update_costs)
        new_distilling_input.la_edited.connect(self.distribute_la)
        new_distilling_input.la_edited.connect(self.update_dilute_table)
        self.layout_distilling_inputs.addWidget(new_distilling_input)
        return new_distilling_input

    def distribute_la(self):
        customer_la = 0
        if not self.customer_handler.is_manual and self.customer_handler.la:
            customer_la = self.customer_handler.la

        distilling_inputs = self.findChildren(DistillingInput)
        for distilling_input in distilling_inputs:
            if distilling_input.customer_la != customer_la:
                distilling_input.customer_la = customer_la
                distilling_input.update_tax()
            customer_la += distilling_input.alcohol_volume_la
        self.customer_handler.le_la_after.setText(f"{customer_la:.2f}")

    def update_dilute_table(self):
        # self.diluteTable.setColumnCount(len(calculations.DILUTE_TARGETS))
        # for col, target in enumerate(calculations.DILUTE_TARGETS):
        #     self.diluteTable.setHorizontalHeaderItem(
        #         col, QTableWidgetItem(f"{target*100:.0f}%")
        #     )
        distilling_inputs = self.findChildren(DistillingInput)
        self.diluteTable.setRowCount(len(distilling_inputs))

        dilute_calculations = calculations.calculate_dillute_table(
            [
                distilling_input.alcohol_percentage_at_20
                for distilling_input in distilling_inputs
            ],
        )

        for row, dilute_row in enumerate(dilute_calculations):
            for col, value in enumerate(dilute_row):
                self.diluteTable.setItem(row, col, QTableWidgetItem(value))

    def date_edit(self):
        self.production_date = self.dateEdit.date().toPyDate()
        if self.production_date != date.today():
            self.reset_button_date.show()
        else:
            self.reset_button_date.hide()

    def date_reset(self):
        self.reset_button_date.hide()
        self.dateEdit.setDate(date.today())
        self.production_date = date.today()

    @staticmethod
    def round_to_5_cent(value: float) -> float:
        return calculations.round_to_5_cent(value)

    def update_costs(self):
        distilling_inputs = self.findChildren(DistillingInput)
        sum_taxes = 0
        sum_la = 0

        for distilling_input in distilling_inputs:
            sum_taxes += distilling_input.sum_tax
            sum_la += distilling_input.alcohol_volume_la

        self.rle_service_cost.setDefault(max(0, sum_la * self.calculation_constants.service_cost * 2.0 - sum_taxes))
        self.service_cost = self.rle_service_cost.value

        self.operating_costs = (
            self.rle_operating_costs.value if self.rle_operating_costs.value else 0.0
        )

        self.cost_sum = self.round_to_5_cent(
            self.service_cost + self.operating_costs + sum_taxes
        )
        self.le_cost_sum.setText(f"{self.cost_sum:.2f}")

        self.tax_base = round(
            (self.service_cost + self.operating_costs) / (1 + self.calculation_constants.vat_tax), 2
        )
        self.le_tax_base.setText(f"{self.tax_base:.2f}")

        self.tax_vat = round(
            (self.service_cost + self.operating_costs) - self.tax_base, 2
        )
        self.le_tax_vat.setText(f"{self.tax_vat:0.2f}")

        if sum_la:
            self.cost_per_liter = calculations.calculate_cost_per_liter(
                sum_taxes + self.service_cost, sum_la
            )
            self.le_cost_per_liter.setText(f"{self.cost_per_liter:.2f}")

    def print_save(self):
        with db.get_session() as session:
            order = self.create_order(session)
            if order is None:
                return

            self.save_order(order, session)
            self.print_order(order)
        self.finish()

    def print(self):
        with db.get_session() as session:
            order = self.create_order(session)
            if order is None:
                return

            self.print_order(order)

    def save(self):
        with db.get_session() as session:
            order = self.create_order(session)
            if order is None:
                return

            self.save_order(order, session)
        self.finish()

    def delete(self):
        if self.order_id is None:
            return

        if order_edit.delete_order(self.order_id):
            self.order_closed.emit()

    def finish(self):
        """Close the editor once its order has been written."""
        if self.order_id is not None:
            self.order_closed.emit()

    def create_order(self, session: Session = None) -> db.Order:
        distilling_inputs = self.findChildren(DistillingInput)

        stored_order = None
        if self.order_id is not None:
            if self.customer_handler.is_manual:
                alert(messages.MANUAL_CUSTOMER_NOT_EDITABLE)
                return None

            stored_order = db.get_order(self.order_id, session)
            if stored_order is None:
                alert(messages.ORDER_NOT_FOUND)
                return None

        if self.customer_handler.is_manual:
            season = None
        elif stored_order is not None:
            # An existing order stays in the season it was booked in, even once
            # that season is no longer the active one.
            season = stored_order.season
        else:
            season = db.get_active_season(session=session)
            if season is None:
                alert(messages.ACTIVE_SEASON_NOT_FOUND)
                return None

        if not self.customer_handler.is_manual:
            customer = db.get_customer(self.customer_handler.customer, session)
        else:
            customer = db.Customer(
                self.customer_handler.le_name.text(),
                self.customer_handler.le_address.text(),
                datetime.strptime(
                    self.customer_handler.le_birthday.text(), DATE_FORMAT
                ).date(),
                self.customer_handler.cb_phone_number.currentText(),
            )

        if customer is None:
            alert(messages.CUSTOMER_NOT_SELECTED)
            return None

        if not self.customer_handler.is_manual:
            # Guard against a second till having booked litres for this customer
            # since the form was filled in - the tier the duty was computed at
            # would no longer be the right one.
            if stored_order is None:
                la = db.get_customer_la(customer, session)
            else:
                la = db.get_customer_la_before(customer, stored_order, season, session)

            if la != self.customer_handler.la:
                alert(messages.LA_NOT_MATCH.format(la, self.customer_handler.la))
                self.customer_handler.load_customer(customer, la=la)
                return None

        if not self.customer_handler.is_manual:
            production_line = db.get_production_line(
                self.cb_production_line.currentText(), session
            )
        else:
            production_line = db.ProductionLine(self.cb_production_line.currentText())

        if production_line is None:
            alert(messages.PRODUCTION_LINE_NOT_SELECTED)
            return None

        if self.production_date is None:
            alert(messages.WRONG_DATE_FORMAT)
            return None

        distillings = []

        for distilling_input in distilling_inputs:
            distilling = distilling_input.get_object()
            if distilling is None:
                return None
            distillings.append(distilling)

        # marked = session.query(db.Order).join(db.ProductionLine, db.Order.production_line_id == db.ProductionLine.id).filter(
        #     db.Order.mark == self.le_mark.text()).filter(db.ProductionLine == production_line).first()
        # if marked:
        #     alert(messages.NON_UNIQUE_MARK.format(marked.mark,
        #           marked.production_date.strftime(DATE_FORMAT)))
        #     return None

        if self.order_id is None:
            return db.Order(
                self.le_mark.text(),
                self.production_date,
                self.service_cost,
                self.tax_vat,
                self.tax_base,
                self.cost_sum,
                self.operating_costs,
                distillings,
                customer,
                season,
                production_line,
                self.calculation_constants
            )

        order = stored_order
        order.mark = self.le_mark.text()
        order.production_date = self.production_date
        order.service_cost = self.service_cost
        order.tax_vat = self.tax_vat
        order.tax_base = self.tax_base
        order.cost_sum = self.cost_sum
        order.operating_costs = self.operating_costs
        order.production_line = production_line
        # The old lines are dropped by the delete-orphan cascade. Season, customer
        # and constants are deliberately left alone: an existing order keeps the
        # period it was booked in and the rates it was priced with.
        order.distillings = distillings

        return order

    def save_order(self, order: db.Order, session: Session = None):
        if self.customer_handler.is_manual:
            return

        session.add(order)
        session.commit()

        print("order saved")

        if self.order_id is not None:
            later_orders = db.get_orders_after(order, session)
            la_before = db.get_customer_la_before(
                order.customer, order, order.season, session
            ) + sum(distilling.alcohol_volume_la for distilling in order.distillings)
            order_edit.warn_about_later_orders(later_orders, la_before)

    def print_order(self, order: db.Order):
        from printer import OrderPrinter

        OrderPrinter().print_order(self, order)
        print("order printed")

    @staticmethod
    def write_edit(edit: QLineEdit, value):
        if isinstance(value, float):
            edit.setText(f"{value:0.2f}")
        pass
