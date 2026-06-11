from src.config import FilterConfig
from src.filters.filters import FilterEngine
from src.models.product import Category, Product


def _make_product(**kwargs) -> Product:
    defaults = {
        "site": "test",
        "category": Category.AIR,
        "title": "MacBook Air M2",
        "chip": "M2",
        "ram_gb": 8,
        "storage_gb": 256,
        "price": 999.0,
    }
    defaults.update(kwargs)
    return Product(**defaults)


def test_no_filters_returns_all():
    config = FilterConfig()
    engine = FilterEngine(config)
    products = [
        _make_product(ram_gb=8),
        _make_product(ram_gb=16),
    ]
    assert len(engine.apply(products)) == 2


def test_filter_by_min_ram():
    config = FilterConfig(min_ram_gb=16)
    engine = FilterEngine(config)
    products = [
        _make_product(ram_gb=8),
        _make_product(ram_gb=16),
        _make_product(ram_gb=32),
    ]
    result = engine.apply(products)
    assert len(result) == 2
    assert all(p.ram_gb >= 16 for p in result)


def test_filter_by_min_ram_keeps_unknown():
    config = FilterConfig(min_ram_gb=16)
    engine = FilterEngine(config)
    products = [_make_product(ram_gb=0)]
    result = engine.apply(products)
    assert len(result) == 1


def test_filter_by_max_price():
    config = FilterConfig(max_price=1500)
    engine = FilterEngine(config)
    products = [
        _make_product(price=999.0),
        _make_product(price=1500.0),
        _make_product(price=2500.0),
    ]
    result = engine.apply(products)
    assert len(result) == 2


def test_filter_by_category():
    config = FilterConfig(categories={"air"})
    engine = FilterEngine(config)
    products = [
        _make_product(category=Category.AIR),
        _make_product(category=Category.PRO),
    ]
    result = engine.apply(products)
    assert len(result) == 1
    assert result[0].category == Category.AIR


def test_filter_by_condition():
    config = FilterConfig(conditions={"refurbished"})
    engine = FilterEngine(config)
    products = [
        _make_product(condition="refurbished"),
        _make_product(condition="new"),
    ]
    result = engine.apply(products)
    assert len(result) == 1
    assert result[0].condition == "refurbished"


def test_combined_filters():
    config = FilterConfig(min_ram_gb=16, max_price=2000)
    engine = FilterEngine(config)
    products = [
        _make_product(ram_gb=8, price=999.0),
        _make_product(ram_gb=16, price=1500.0),
        _make_product(ram_gb=32, price=2500.0),
    ]
    result = engine.apply(products)
    assert len(result) == 1
    assert result[0].ram_gb == 16
    assert result[0].price == 1500.0


def test_filter_from_env(monkeypatch):
    monkeypatch.setenv("FILTERS", '{"min_ram_gb": 16, "max_price": 2000}')
    config = FilterConfig.from_env()
    assert config.min_ram_gb == 16
    assert config.max_price == 2000


def test_filter_from_env_invalid(monkeypatch):
    monkeypatch.setenv("FILTERS", "not-json")
    config = FilterConfig.from_env()
    assert config.min_ram_gb == 0
