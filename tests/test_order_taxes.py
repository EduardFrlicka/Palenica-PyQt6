"""Tests for the excise-duty arithmetic behind editing and deleting an order.

Duty is charged at a lower rate up to a per-customer, per-season limit of
litres of absolute alcohol and at the full rate beyond it, so what an order is
charged depends on everything the customer distilled before it. That is what
makes an edit interesting: it moves the running total, and the orders that come
after can land in a different tier than the one they were printed with.
"""

from datetime import date

import pytest

import calculations
from calculations import OrderTaxInput

LOWER = 7.452
FULL = 14.904
LIMIT = 43.0


# ---------------------------------------------------------------------------
# excise_tax
# ---------------------------------------------------------------------------


def test_wholly_below_the_limit_is_charged_the_lower_rate():
    tax = calculations.excise_tax(0.0, 10.0, LOWER, FULL, LIMIT)

    assert tax.lower == pytest.approx(74.52)
    assert tax.full == 0.0
    assert tax.total == pytest.approx(74.52)


def test_wholly_above_the_limit_is_charged_the_full_rate():
    tax = calculations.excise_tax(50.0, 10.0, LOWER, FULL, LIMIT)

    assert tax.lower == 0.0
    assert tax.full == pytest.approx(149.04)
    assert tax.total == pytest.approx(149.04)


def test_a_distilling_straddling_the_limit_is_split_across_both_rates():
    tax = calculations.excise_tax(40.0, 10.0, LOWER, FULL, LIMIT)

    # 3 la at the lower rate, the remaining 7 at the full one.
    assert tax.lower == pytest.approx(22.36)
    assert tax.full == pytest.approx(104.33)
    assert tax.total == pytest.approx(126.69)


def test_landing_exactly_on_the_limit_stays_at_the_lower_rate():
    tax = calculations.excise_tax(40.0, 3.0, LOWER, FULL, LIMIT)

    assert tax.full == 0.0
    assert tax.lower == pytest.approx(22.36)


def test_the_split_lines_add_up_to_the_total():
    tax = calculations.excise_tax(42.37, 4.13, LOWER, FULL, LIMIT)

    assert tax.lower + tax.full == pytest.approx(tax.total)
    assert tax.total == round(tax.total, 2)


# ---------------------------------------------------------------------------
# running_la_before
# ---------------------------------------------------------------------------


def test_running_la_before_offsets_each_distilling_by_the_previous_ones():
    assert calculations.running_la_before(5.0, [2.0, 3.0, 4.0]) == [5.0, 7.0, 10.0]


def test_running_la_before_of_nothing_is_nothing():
    assert calculations.running_la_before(5.0, []) == []


# ---------------------------------------------------------------------------
# recalculate_order_taxes
# ---------------------------------------------------------------------------


def order(order_id, volumes, stored_tax, mark=None):
    return OrderTaxInput(
        order_id,
        mark or str(order_id),
        date(2026, 3, order_id),
        stored_tax,
        tuple(volumes),
        LOWER,
        FULL,
        LIMIT,
    )


def test_an_order_that_still_matches_is_reported_unchanged():
    [change] = calculations.recalculate_order_taxes([order(1, [10.0], 74.52)], 0.0)

    assert change.recalculated_tax == pytest.approx(74.52)
    assert not change.changed


def test_litres_added_ahead_of_an_order_push_it_up_a_tier():
    # Priced as if nothing came before it, but 40 la now do.
    [change] = calculations.recalculate_order_taxes([order(1, [10.0], 74.52)], 40.0)

    assert change.recalculated_tax == pytest.approx(126.69)
    assert change.changed


def test_litres_removed_ahead_of_an_order_pull_it_back_down():
    [change] = calculations.recalculate_order_taxes([order(1, [10.0], 126.69)], 0.0)

    assert change.recalculated_tax == pytest.approx(74.52)
    assert change.changed


def test_the_walk_carries_litres_from_one_order_into_the_next():
    changes = calculations.recalculate_order_taxes(
        [order(1, [20.0], 0.0), order(2, [20.0], 0.0), order(3, [20.0], 0.0)], 0.0
    )

    # 20 and 40 la stay under the 43 la limit; the third order starts at 40, so
    # 3 of its litres are still cheap and 17 are not.
    assert [change.recalculated_tax for change in changes] == pytest.approx(
        [149.04, 149.04, 275.73]
    )


def test_litres_accumulate_across_the_lines_within_one_order():
    [change] = calculations.recalculate_order_taxes(
        [order(1, [40.0, 10.0], 0.0)], 0.0
    )

    # The second line starts at 40 la, so it is the one that straddles the limit.
    assert change.recalculated_tax == pytest.approx(298.08 + 126.69)


def test_a_deletion_earlier_in_the_season_only_moves_orders_past_the_limit():
    orders = [order(1, [5.0], 37.26), order(2, [5.0], 37.26)]

    # 10 la disappearing from ahead of them changes nothing: both stay cheap.
    changes = calculations.recalculate_order_taxes(orders, 20.0)
    assert not any(change.changed for change in changes)

    # 10 la appearing does, once the pair crosses the limit.
    changes = calculations.recalculate_order_taxes(orders, 40.0)
    assert [change.changed for change in changes] == [True, True]


def test_orders_keep_their_identity_so_the_warning_can_name_them():
    [change] = calculations.recalculate_order_taxes(
        [order(7, [10.0], 74.52, mark="123")], 0.0
    )

    assert change.order_id == 7
    assert change.mark == "123"
    assert change.production_date == date(2026, 3, 7)
    assert change.stored_tax == pytest.approx(74.52)


def test_nothing_after_an_order_is_nothing_to_recalculate():
    assert calculations.recalculate_order_taxes([], 12.0) == []
