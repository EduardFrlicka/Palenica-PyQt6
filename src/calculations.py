from decimal import Decimal, ROUND_HALF_UP
from typing import List, NamedTuple, Sequence, Tuple
from constants import DILUTE_TARGETS
from temperature_table import TEMPERATURE_TABLE

CENT = Decimal("0.01")
FIVE_CENT = Decimal("0.05")


class TaxBreakdown(NamedTuple):
    """Excise duty for a single distilling, split into its two rate tiers."""

    lower: float
    full: float
    total: float


class OrderCosts(NamedTuple):
    """The monetary totals shown on an order once taxes and costs are known."""

    cost_sum: float
    tax_base: float
    tax_vat: float
    cost_per_liter: float


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


def percentage_at_20(
    alcohol_percentage: float,
    alcohol_temperature: float,
    table: Sequence[Sequence[float]] = TEMPERATURE_TABLE,
) -> float:
    """Volumetric strength corrected to 20 ˚C, as a fraction (0.0–1.0).

    `table` is tabulated at 0.1 % and 1 ˚C granularity. Pick the nearest
    row/column rather than flooring, which biased every reading towards an
    overstated strength. A -1 sentinel in the table means "not measurable";
    out-of-range inputs return 0.0 rather than raising.
    """
    percentage = round_half_up_int(alcohol_percentage * 10)
    temperature = round_half_up_int(alcohol_temperature)
    if percentage < 0 or percentage >= len(table) or temperature < 0:
        return 0.0

    # Bounds come from the row itself: the last rows are a few entries short, so
    # a hard-coded column limit would index past the end of them.
    row = table[percentage]
    if temperature >= len(row):
        return 0.0

    result = row[temperature]
    return 0.0 if result == -1 else result / 100


def litres_absolute(percentage_at_20: float, alcohol_volume: float) -> float:
    """Litres of absolute alcohol (LA) in a distilling, rounded to 2 places."""
    return round(percentage_at_20 * alcohol_volume, 2)


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


def default_service_cost(
    sum_la: float, service_cost_rate: float, sum_taxes: float
) -> float:
    """Suggested service fee before the operator overrides it.

    Twice the per-litre rate applied to the order's LA, less the excise already
    charged, floored at zero so tax alone never produces a negative fee.
    """
    return max(0.0, sum_la * service_cost_rate * 2.0 - sum_taxes)


def order_costs(
    service_cost: float,
    operating_costs: float,
    sum_taxes: float,
    sum_la: float,
    vat_rate: float,
) -> OrderCosts:
    """The order totals derived from the (possibly overridden) service cost."""
    cost_sum = round_to_5_cent(service_cost + operating_costs + sum_taxes)
    tax_base = round((service_cost + operating_costs) / (1 + vat_rate), 2)
    tax_vat = round((service_cost + operating_costs) - tax_base, 2)
    cost_per_liter = calculate_cost_per_liter(sum_taxes + service_cost, sum_la)
    return OrderCosts(cost_sum, tax_base, tax_vat, cost_per_liter)
