"""Currency conversion helpers for the billing pipeline."""

from decimal import Decimal, ROUND_HALF_UP

MINOR_UNIT_QUANTUM = Decimal("1")


def convert_all(amounts, get_rate):
    """Convert a list of amounts to integer minor units in the target currency.

    Each amount is converted at its source currency's rate, then rounded to
    whole minor units (cents). Returns a list of ints aligned with ``amounts``.
    """
    results = []
    for amount in amounts:
        value = Decimal(str(amount["value"]))
        currency = amount["currency"]
        rate = Decimal(str(get_rate(currency)))
        minor = (value * Decimal(100)).quantize(
            MINOR_UNIT_QUANTUM, rounding=ROUND_HALF_UP
        )
        converted = (minor * rate).quantize(
            MINOR_UNIT_QUANTUM, rounding=ROUND_HALF_UP
        )
        results.append(int(converted))
    return results
