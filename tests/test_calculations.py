"""Unit tests for the pure calculation layer.

These exercise the excise-tax tiers, LA distribution and order-cost maths that
used to live inside the Qt widgets. No Qt or database import is needed - that is
the point of extracting them into `calculations`.
"""

import calculations
from calculations import OrderCosts, TaxBreakdown

# Realistic constants, matching CalculationConstants defaults.
LOWER_TAX = 7.452
FULL_TAX = 14.904
LA_LIMIT = 43.0
VAT_RATE = 0.20
SERVICE_RATE = 8.2


# --- excise_tax: the three rate tiers -------------------------------------


def test_excise_tax_entirely_below_limit():
    tax = calculations.excise_tax(0.0, 10.0, LOWER_TAX, FULL_TAX, LA_LIMIT)
    assert tax == TaxBreakdown(lower=74.52, full=0.0, total=74.52)


def test_excise_tax_entirely_above_limit():
    tax = calculations.excise_tax(50.0, 10.0, LOWER_TAX, FULL_TAX, LA_LIMIT)
    assert tax == TaxBreakdown(lower=0.0, full=149.04, total=149.04)


def test_excise_tax_straddles_limit():
    # 40 LA already, 10 more: 3 taxed low, 7 taxed full.
    tax = calculations.excise_tax(40.0, 10.0, LOWER_TAX, FULL_TAX, LA_LIMIT)
    assert tax == TaxBreakdown(lower=22.36, full=104.33, total=126.69)
    # The total is the rounded sum of the rounded parts.
    assert tax.total == calculations.round_money(tax.lower + tax.full)


def test_excise_tax_boundary_is_charged_at_lower_rate():
    # customer_la_before + volume_la == limit falls in the lower tier.
    tax = calculations.excise_tax(33.0, 10.0, LOWER_TAX, FULL_TAX, LA_LIMIT)
    assert tax == TaxBreakdown(lower=74.52, full=0.0, total=74.52)


def test_excise_tax_starting_exactly_at_limit_is_all_full_rate():
    tax = calculations.excise_tax(43.0, 5.0, LOWER_TAX, FULL_TAX, LA_LIMIT)
    assert tax == TaxBreakdown(lower=0.0, full=74.52, total=74.52)


def test_excise_tax_zero_volume():
    tax = calculations.excise_tax(0.0, 0.0, LOWER_TAX, FULL_TAX, LA_LIMIT)
    assert tax == TaxBreakdown(lower=0.0, full=0.0, total=0.0)


# --- running_la_before: the LA cascade ------------------------------------


def test_running_la_before_accumulates_prefixes():
    assert calculations.running_la_before(5.0, [10.0, 20.0, 3.0]) == [5.0, 15.0, 35.0]


def test_running_la_before_from_zero():
    assert calculations.running_la_before(0.0, [10.0, 20.0]) == [0.0, 10.0]


def test_running_la_before_empty():
    assert calculations.running_la_before(12.0, []) == []


def test_cascade_and_tax_walk_across_the_limit():
    # Two distillings for a fresh customer, limit 43: first fully low, the
    # second straddles.
    volumes = [30.0, 20.0]
    before = calculations.running_la_before(0.0, volumes)
    taxes = [
        calculations.excise_tax(b, v, LOWER_TAX, FULL_TAX, LA_LIMIT)
        for b, v in zip(before, volumes)
    ]
    assert taxes[0].full == 0.0  # 0..30, all lower
    assert taxes[1].lower > 0.0 and taxes[1].full > 0.0  # 30..50 straddles 43


# --- default_service_cost -------------------------------------------------


def test_default_service_cost():
    assert calculations.default_service_cost(10.0, SERVICE_RATE, 50.0) == 114.0


def test_default_service_cost_floored_at_zero():
    # Excise alone must never make the suggested fee negative.
    assert calculations.default_service_cost(1.0, SERVICE_RATE, 100.0) == 0.0


# --- order_costs ----------------------------------------------------------


def test_order_costs_basic():
    costs = calculations.order_costs(114.0, 0.0, 50.0, 10.0, VAT_RATE)
    assert costs == OrderCosts(
        cost_sum=164.0, tax_base=95.0, tax_vat=19.0, cost_per_liter=8.2
    )


def test_order_costs_rounds_sum_to_five_cents():
    costs = calculations.order_costs(100.0, 0.0, 13.03, 0.0, VAT_RATE)
    assert costs.cost_sum == 113.05  # 113.03 -> nearest 5 cents
    assert costs.tax_base == 83.33  # round(100 / 1.2, 2)
    assert costs.tax_vat == 16.67
    assert costs.cost_per_liter == 0.0  # sum_la == 0


# --- percentage_at_20: temperature-table lookup ---------------------------


def test_percentage_at_20_reads_the_table():
    # Row 10 (1.0 %), column 3 (3 C) -> 1.91 in the table -> 0.0191 as a fraction.
    assert calculations.percentage_at_20(1.0, 3.0) == 0.0191


def test_percentage_at_20_sentinel_means_not_measurable():
    # Row 0, column 20 holds the -1 sentinel.
    assert calculations.percentage_at_20(0.0, 20.0) == 0.0


def test_percentage_at_20_uses_a_small_table_for_bounds():
    table = [[0.50, 0.60]]
    assert calculations.percentage_at_20(0.0, 0.0, table) == 0.005
    assert calculations.percentage_at_20(0.0, 1.0, table) == 0.006


def test_percentage_at_20_out_of_range_returns_zero():
    table = [[0.50]]
    assert calculations.percentage_at_20(-1.0, 0.0, table) == 0.0  # negative %
    assert calculations.percentage_at_20(1.0, 0.0, table) == 0.0  # % past table
    assert calculations.percentage_at_20(0.0, 5.0, table) == 0.0  # temp past row


# --- rounding helpers -----------------------------------------------------


def test_round_half_up_int_is_not_bankers_rounding():
    assert calculations.round_half_up_int(0.5) == 1
    assert calculations.round_half_up_int(1.5) == 2
    assert calculations.round_half_up_int(2.5) == 3  # banker's would give 2
    assert calculations.round_half_up_int(-0.5) == -1


def test_round_money_is_decimal_exact():
    # round(2.675, 2) == 2.67 in binary float; the money version must not.
    assert calculations.round_money(2.675) == 2.68
    assert calculations.round_money(0.005) == 0.01


def test_round_to_5_cent_grid():
    assert calculations.round_to_5_cent(0.074) == 0.05
    assert calculations.round_to_5_cent(0.075) == 0.10


def test_litres_absolute_rounds_to_two_places():
    assert calculations.litres_absolute(0.5, 3.0) == 1.5
    assert calculations.litres_absolute(0.0191, 12.5) == 0.24
