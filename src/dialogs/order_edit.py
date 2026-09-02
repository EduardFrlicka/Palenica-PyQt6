"""Editing and deleting an order that is already in the database.

Both are the same distilling form the order was created with, so the arithmetic
never has a second implementation. What is extra here is the knock-on effect:
excise duty is tiered on the litres a customer accumulates over a season, so
changing or removing one order can change what every later order of theirs
should have been charged.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout

import calculations
import db
import messages
from constants import DATE_FORMAT
from dialogs.alert import alert, confirm, warning


class OrderEditDialog(QDialog):
    """Window holding the distilling form for one stored order."""

    def __init__(self, order_id: int, parent=None):
        # Imported here: the form itself reaches back into this module for the
        # delete flow, and a top-level import would close the loop.
        from tabs.create_distilling_tab import CreateDistillingTab

        super().__init__(parent)
        self.setWindowTitle(messages.ORDER_EDIT_TITLE)

        self.tab = CreateDistillingTab(order_id=order_id)
        self.tab.order_closed.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tab)

        self.setWindowState(Qt.WindowState.WindowMaximized)


def warn_about_later_orders(later_orders, la_before: float):
    """Report the later orders whose excise duty no longer matches what is stored.

    `later_orders` are the same customer's following orders in the season, read
    before the change, and `la_before` is the litres standing ahead of them once
    it has been applied. They are not rewritten here - their doklady have been
    printed - so the operator is told which ones to open and save again.
    """
    changed = [
        change
        for change in calculations.recalculate_order_taxes(later_orders, la_before)
        if change.changed
    ]
    if not changed:
        return

    lines = "\n".join(
        messages.LATER_ORDER_LINE.format(
            change.mark,
            change.production_date.strftime(DATE_FORMAT),
            change.stored_tax,
            change.recalculated_tax,
        )
        for change in changed
    )
    warning(messages.LATER_ORDERS_NEED_RECALCULATION.format(lines))


def delete_order(order_id: int) -> bool:
    """Ask, then delete the order. Returns whether it is gone."""
    with db.get_session() as session:
        order = db.get_order(order_id, session)
        if order is None:
            alert(messages.ORDER_NOT_FOUND)
            return False

        if not confirm(
            messages.CONFIRM_DELETE_ORDER.format(
                order.mark, order.production_date.strftime(DATE_FORMAT)
            )
        ):
            return False

        # Read what the deletion unsettles while the order is still there.
        later_orders = db.get_orders_after(order, session)
        la_before = db.get_customer_la_before(
            order.customer, order, order.season, session
        )

        db.delete_order(order, session)

    warn_about_later_orders(later_orders, la_before)
    return True
