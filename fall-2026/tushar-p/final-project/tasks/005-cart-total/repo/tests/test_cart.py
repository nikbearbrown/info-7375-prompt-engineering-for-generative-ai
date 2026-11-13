from shop import Cart, apply_discount


def test_discount_rounds_down_to_whole_cents():
    price = apply_discount(999, 10)
    assert price == 899 and isinstance(price, int)


def test_discount_edges():
    assert apply_discount(500, 0) == 500
    assert apply_discount(500, 100) == 0


def test_total_counts_quantity():
    cart = Cart()
    cart.add("pen", 150, quantity=3)
    assert cart.total() == 450


def test_total_discount_and_quantity():
    cart = Cart()
    cart.add("book", 999, quantity=2, discount_percent=10)
    cart.add("pen", 150)
    total = cart.total()
    assert total == 2 * 899 + 150 and isinstance(total, int)


def test_empty_cart():
    assert Cart().total() == 0
