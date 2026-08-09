from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple
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
