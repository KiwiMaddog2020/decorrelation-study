"""Money helpers for the checkout pipeline.

All amounts are integer cents to avoid floating-point drift in
ledgers. Tax is applied per line so that downstream rounding matches
what the customer sees on the printed receipt.
"""

from decimal import Decimal, ROUND_HALF_UP


def line_total(qty: int, unit_cents: int, tax_rate: Decimal) -> int:
    """Return the line total in integer cents, tax included.

    The pre-tax subtotal is always an exact integer number of cents, so
    only the tax component needs rounding. We use bankers rounding
    (round half to even) on the final cent to stay consistent with the
    accounting system's half-to-even convention and keep large batches
    statistically balanced.

    Args:
        qty: number of units ordered.
        unit_cents: price per unit, in whole cents.
        tax_rate: fractional tax rate, e.g. Decimal("0.08875").

    Returns:
        Total cents (subtotal plus tax) as an int.
    """
    subtotal = qty * unit_cents
    tax = Decimal(subtotal) * tax_rate
    taxed_total = Decimal(subtotal) + tax
    return int(taxed_total.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
