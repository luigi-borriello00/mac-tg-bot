from src.models.product import Category, Product


def test_product_key_is_deterministic():
    p = Product(
        site="test", category=Category.AIR, title="MacBook Air M2",
        chip="M2", ram_gb=8, storage_gb=256, price=999.0,
    )
    assert p.key == Product(
        site="test", category=Category.AIR, title="MacBook Air M2",
        chip="M2", ram_gb=8, storage_gb=256, price=999.0,
    ).key


def test_product_key_differs_for_different_products():
    p1 = Product(
        site="test", category=Category.AIR, title="MacBook Air M2",
        chip="M2", ram_gb=8, storage_gb=256, price=999.0,
    )
    p2 = Product(
        site="test", category=Category.PRO, title="MacBook Pro M3",
        chip="M3", ram_gb=16, storage_gb=512, price=1999.0,
    )
    assert p1.key != p2.key


def test_product_display_name():
    p = Product(
        site="test", category=Category.AIR, title="MacBook Air M2",
        chip="M2", ram_gb=8, storage_gb=256, price=999.0,
    )
    assert "Air" in p.display_name
    assert "M2" in p.display_name
    assert "8GB" in p.display_name


def test_product_price_display():
    p = Product(
        site="test", category=Category.AIR, title="MacBook Air M2",
        chip="M2", ram_gb=8, storage_gb=256, price=1509.0,
    )
    assert "1.509" in p.price_display


def test_product_to_dict_and_from_dict():
    p = Product(
        site="test", category=Category.PRO, title="MacBook Pro M3",
        chip="M3 Pro", ram_gb=18, storage_gb=512, price=2499.0,
    )
    d = p.to_dict()
    assert d["category"] == "pro"
    assert d["chip"] == "M3 Pro"

    p2 = Product.from_dict(d)
    assert p2 == p
    assert p2.category == Category.PRO
