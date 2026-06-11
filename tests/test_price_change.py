from src.models.product import Category, PriceChange, Product


def test_price_change_decrease():
    p = Product(
        site="test", category=Category.AIR, title="MacBook Air M2",
        chip="M2", ram_gb=8, storage_gb=256, price=899.0,
    )
    change = PriceChange(product=p, old_price=999.0, new_price=899.0)
    assert change.is_decrease
    assert change.change_pct < 0
    assert "📉" in change.direction_emoji


def test_price_change_increase():
    p = Product(
        site="test", category=Category.PRO, title="MacBook Pro M3",
        chip="M3", ram_gb=16, storage_gb=512, price=2100.0,
    )
    change = PriceChange(product=p, old_price=1999.0, new_price=2100.0)
    assert not change.is_decrease
    assert change.change_pct > 0
    assert "📈" in change.direction_emoji


def test_price_change_pct():
    p = Product(
        site="test", category=Category.AIR, title="MacBook Air M2",
        chip="M2", ram_gb=8, storage_gb=256, price=800.0,
    )
    change = PriceChange(product=p, old_price=1000.0, new_price=800.0)
    assert abs(change.change_pct - (-20.0)) < 0.01
