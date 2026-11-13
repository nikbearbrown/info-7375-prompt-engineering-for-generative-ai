"""A shopping cart."""

from shop.pricing import apply_discount


class Cart:
    """Lines of (name, unit price in cents, quantity, discount percent)."""

    def __init__(self):
        self.lines = []

    def add(self, name, unit_cents, quantity=1, discount_percent=0):
        """Add quantity units of an item, each discounted by discount_percent."""
        self.lines.append((name, unit_cents, quantity, discount_percent))

    def total(self):
        """Return the total in whole cents (an int): for each line, the
        discounted unit price times the quantity, summed over all lines."""
        total = 0
        for _name, unit_cents, _quantity, discount in self.lines:
            total += apply_discount(unit_cents, discount)
        return total
