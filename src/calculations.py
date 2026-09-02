from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import List, NamedTuple, Sequence, Tuple
from constants import DILUTE_TARGETS

CENT = Decimal("0.01")
FIVE_CENT = Decimal("0.05")


def quantize(value: float, step: Decimal) -> float:
    """Round `value` onto a grid of `step`, half away from zero.

    Going through Decimal avoids both the binary representation error of
    `round(value / 0.05) * 0.05` and Python's round-half-to-even, which is the
    wrong rounding mode for currency.
    """
    steps = (Decimal(str(value)) / step).quantize(Decimal(1), rounding=ROUND_HALF_UP)
    return float(steps * step)


def round_money(value: float) -> float:
    return quantize(value, CENT)


def round_to_5_cent(value: float) -> float:
    return quantize(value, FIVE_CENT)


def round_half_up_int(value: float) -> int:
    """Nearest integer, ties away from zero — for table indices, not money."""
    return int(Decimal(str(value)).to_integral_value(rounding=ROUND_HALF_UP))


def split_euro_cents(value: float) -> Tuple[int, int]:
    """Split a monetary amount into whole euros and cents for the amount in words."""
    total_cents = int((Decimal(str(value)) * 100).to_integral_value(rounding=ROUND_HALF_UP))
    return divmod(total_cents, 100)


def calculate_dillute_table(
    distilling_percentages: List[float],
    dilute_targets: List[float] = DILUTE_TARGETS,
) -> List[List[str]]:
    return [
        [
            (
                f"{(distilling_percentage / dilute_target - 1) * 10:.1f}"
                if distilling_percentage / dilute_target > 1
                else "-"
            )
            for dilute_target in dilute_targets
        ]
        for distilling_percentage in distilling_percentages
    ]

def calculate_cost_per_liter(cost: float, la: float) -> float:
    return cost / la * 0.5 if la else 0.0


class TaxBreakdown(NamedTuple):
    """Excise duty for a single distilling, split into its two rate tiers."""

    lower: float
    full: float
    total: float


def excise_tax(
    customer_la_before: float,
    volume_la: float,
    lower_tax: float,
    full_tax: float,
    la_limit: float,
) -> TaxBreakdown:
    """Excise duty on `volume_la` litres of absolute alcohol.

    Duty is charged at the lower rate up to `la_limit` litres per customer per
    season and at the full rate beyond it. `customer_la_before` is how much LA
    the customer has already accumulated ahead of this distilling, so a single
    distilling can straddle the limit and be taxed at both rates.

    Amounts are quantised to cents before they are stored or summed, so the
    printed lines add up to the printed total.
    """
    if customer_la_before > la_limit:
        lower = 0.0
        full = volume_la * full_tax
    elif customer_la_before + volume_la <= la_limit:
        full = 0.0
        lower = volume_la * lower_tax
    else:
        lower = (la_limit - customer_la_before) * lower_tax
        full = (customer_la_before + volume_la - la_limit) * full_tax

    lower = round_money(lower)
    full = round_money(full)
    return TaxBreakdown(lower, full, round_money(lower + full))


def running_la_before(start_la: float, volumes: Sequence[float]) -> List[float]:
    """LA already accumulated ahead of each distilling in `volumes`.

    The first entry is `start_la` (the customer's LA from earlier orders); each
    subsequent entry adds the preceding distilling's volume. Feeding these into
    `excise_tax` walks a customer's distillings across the `la_limit` boundary.
    """
    result = []
    accumulated = start_la
    for volume in volumes:
        result.append(accumulated)
        accumulated += volume
    return result


class OrderTaxInput(NamedTuple):
    """A stored order, reduced to what re-deriving its excise duty needs."""

    order_id: int
    mark: str
    production_date: date
    stored_tax: float
    volumes_la: Tuple[float, ...]
    lower_tax: float
    full_tax: float
    la_limit: float


class OrderTaxChange(NamedTuple):
    """What an order's excise duty is stored as, and what it recomputes to."""

    order_id: int
    mark: str
    production_date: date
    stored_tax: float
    recalculated_tax: float

    @property
    def changed(self) -> bool:
        return self.stored_tax != self.recalculated_tax


def recalculate_order_taxes(
    orders: Sequence[OrderTaxInput], start_la: float = 0.0
) -> List[OrderTaxChange]:
    """Re-derive the excise duty of `orders`, starting from `start_la` litres.

    `orders` must be in the sequence the customer's litres accumulate in, since
    each order is taxed against everything that came before it. Editing or
    deleting an order shifts that running total, which can move a later order
    into the other rate tier - every order is returned, and callers filter on
    `changed` to find the ones that no longer match what is stored.
    """
    changes = []
    accumulated = start_la

    for order in orders:
        total = round_money(
            sum(
                excise_tax(
                    la_before, volume, order.lower_tax, order.full_tax, order.la_limit
                ).total
                for la_before, volume in zip(
                    running_la_before(accumulated, order.volumes_la), order.volumes_la
                )
            )
        )
        accumulated += sum(order.volumes_la)

        changes.append(
            OrderTaxChange(
                order.order_id,
                order.mark,
                order.production_date,
                round_money(order.stored_tax),
                total,
            )
        )

    return changes
