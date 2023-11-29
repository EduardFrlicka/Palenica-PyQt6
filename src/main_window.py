from PyQt6.QtWidgets import QMainWindow, QLineEdit, QTableWidgetItem, QMessageBox
from PyQt6.QtCore import QVariant, Qt
from ui_py.MainWindow_ui import Ui_MainWindow
import resources
from distilling_input import DistillingInput
from datetime import datetime
from constants import SERVICE_COST_PER_LA, VAT_TAX, FULL_TAX, LOWER_TAX, DATE_FORMAT
from customer_select import CustomerSelectDialog
from sqlalchemy.orm import Session
from datetime import date
import config
import db
import messages
from alert import alert
from sqlalchemy.sql import func


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label_year.setText(f"/{date.today().year}")
        self.date_reset()
        self.add_distillating_input()
        self.label_lower_tax.setText(f"Suma spotrebnej dane {LOWER_TAX:.2f} €/la")
        self.label_full_tax.setText(f"Suma spotrebnej dane {FULL_TAX:.2f} €/la")
        self.lineEdit_date.textEdited.connect(self.date_edit)
        self.reset_button_date.clicked.connect(self.date_reset)
        self.button_add_distilling_input.clicked.connect(self.add_distillating_input)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.rle_operating_costs.setDefault(0.0)
        self.setWindowState(Qt.WindowState.WindowMaximized)

    def add_distillating_input(self):
        new_distilling_input = DistillingInput(parent=self.centralwidget)
        new_distilling_input.setObjectName("distilling_input")
        new_distilling_input.tax_edited.connect(self.update_costs)
        new_distilling_input.la_edited.connect(self.distribute_la)
        new_distilling_input.la_edited.connect(self.update_dilute_table)
        self.layout_distilling_inputs.addWidget(new_distilling_input)

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
        distilling_inputs = self.findChildren(DistillingInput)
        self.diluteTable.setRowCount(len(distilling_inputs))
        dilute_targets = [0.48, 0.50, 0.52, 0.55]
        for row, distilling_inputin in enumerate(distilling_inputs):
            for col, dilute_target in enumerate(dilute_targets):
                dcl = (
                    distilling_inputin.alcohol_percentage_at_20 / dilute_target - 1
                ) * 10
                value = f"{dcl:0.1f}" if dcl > 0 else "-"
                self.diluteTable.setItem(row, col, QTableWidgetItem(value))

    def date_edit(self):
        self.reset_button_date.show()
        try:
            self.production_date = datetime.strptime(
                self.lineEdit_date.text().replace(" ", ""), DATE_FORMAT
            ).date()
        except ValueError:
            self.production_date = None

    def date_reset(self):
        self.reset_button_date.hide()
        self.lineEdit_date.setText(date.today().strftime(DATE_FORMAT))
        self.production_date = date.today()

    @staticmethod
    def round_to_5_cent(value: float) -> float:
        ROUND_PRECISION = 0.05
        result = round(value / ROUND_PRECISION, 0) * ROUND_PRECISION
        return result if result else 0.05

    def update_costs(self):
        distilling_inputs = self.findChildren(DistillingInput)
        sum_taxes = 0
        sum_la = 0

        for distilling_input in distilling_inputs:
            sum_taxes += distilling_input.sum_tax
            sum_la += distilling_input.alcohol_volume_la

        self.rle_service_cost.setDefault(max(0, sum_la * SERVICE_COST_PER_LA))
        self.service_cost = self.rle_service_cost.value

        self.operating_costs = (
            self.rle_operating_costs.value if self.rle_operating_costs.value else 0.0
        )

        # TODO round
        self.cost_sum = self.round_to_5_cent(
            self.service_cost + self.operating_costs + sum_taxes
        )
        self.le_cost_sum.setText(f"{self.cost_sum:.2f}")

        self.tax_base = round(
            (self.service_cost + self.operating_costs) / (1 + VAT_TAX), 2
        )
        self.le_tax_base.setText(f"{self.tax_base:.2f}")

        self.tax_vat = round(
            (self.service_cost + self.operating_costs) - self.tax_base, 2
        )
        self.le_tax_vat.setText(f"{self.tax_vat:0.2f}")

        if sum_la:
            self.cost_per_liter = (sum_taxes + self.service_cost) / sum_la * 0.5
            self.le_cost_per_liter.setText(f"{self.cost_per_liter:.2f}")

    def print_save(self):
        if "save" in config.config["main_window"]["confirm_action"]:
            if not self.save():
                return
        if "print" in config.config["main_window"]["confirm_action"]:
            self.print()
        self.close()

    def save(self):
        if self.customer_handler.is_manual:
            return True

        distilling_inputs = self.findChildren(DistillingInput)

        with Session(db.engine) as session:
            season = db.get_active_season(session)
            if season is None:
                alert(messages.ACTIVE_SEASON_NOT_FOUND)
                return False

            customer = db.get_customer(self.customer_handler.customer, session)
            if customer is None:
                alert(messages.CUSTOMER_NOT_SELECTED)
                return False

            la = (
                session.query(func.sum(db.Distilling.alcohol_volume_la))
                .outerjoin(db.Order, db.Distilling.order_id == db.Order.id)
                .outerjoin(db.Customer, db.Customer.id == db.Order.customer_id)
                .group_by(db.Customer.id)
                .filter(db.Customer.id == customer.id)
                .first()
            )
            if la is None:
                la = 0
            else:
                la = la[0]

            if la != self.customer_handler.la:
                alert(messages.LA_NOT_MATCH.format(la, self.customer_handler.la))
                self.customer_handler.load_customer(customer)
                return False

            production_line = db.get_production_line(
                self.cb_production_line.currentText(), session
            )
            if production_line is None:
                alert(messages.PRODUCTION_LINE_NOT_SELECTED)
                return False

            if self.production_date is None:
                alert(messages.WRONG_DATE_FORMAT)
                return False

            distillings = []

            for distilling_input in distilling_inputs:
                distilling = distilling_input.get_object()
                if distilling is None:
                    return False
                distillings.append(distilling)

            # marked = session.query(db.Order).join(db.ProductionLine, db.Order.production_line_id == db.ProductionLine.id).filter(
            #     db.Order.mark == self.le_mark.text()).filter(db.ProductionLine == production_line).first()
            # if marked:
            #     alert(messages.NON_UNIQUE_MARK.format(marked.mark,
            #           marked.production_date.strftime(DATE_FORMAT)))
            #     return False

            order = db.Order(
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
            )

            for distilling in distillings:
                session.add(distilling)
            session.add(order)
            session.commit()

        return True

    def print(self):
        from printer import OrderPrinter

        OrderPrinter().print_order(self)

    @staticmethod
    def write_edit(edit: QLineEdit, value):
        if isinstance(value, float):
            edit.setText(f"{value:0.2f}")
        pass
