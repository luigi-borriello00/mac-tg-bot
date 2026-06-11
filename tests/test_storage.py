from src.models.product import Category, Product
from src.storage.json_storage import JsonStorage


def test_save_and_load(tmp_path):
    path = str(tmp_path / "state.json")
    storage = JsonStorage(path)
    products = [
        Product(
            site="test", category=Category.AIR, title="MacBook Air M2",
            chip="M2", ram_gb=8, storage_gb=256, price=999.0,
        ),
    ]
    storage.save(products)

    loaded = storage.load()
    assert len(loaded) == 1
    entry = list(loaded.values())[0]
    assert entry["product"]["price"] == 999.0


def test_detect_changes_new_product(tmp_path):
    path = str(tmp_path / "state.json")
    storage = JsonStorage(path)
    p = Product(
        site="test", category=Category.AIR, title="MacBook Air M2",
        chip="M2", ram_gb=8, storage_gb=256, price=999.0,
    )
    new_products, price_changes = storage.detect_changes([p], {})
    assert len(new_products) == 1
    assert len(price_changes) == 0


def test_detect_changes_price_change(tmp_path):
    path = str(tmp_path / "state.json")
    storage = JsonStorage(path)
    p_old = Product(
        site="test", category=Category.AIR, title="MacBook Air M2",
        chip="M2", ram_gb=8, storage_gb=256, price=999.0,
    )
    p_new = Product(
        site="test", category=Category.AIR, title="MacBook Air M2",
        chip="M2", ram_gb=8, storage_gb=256, price=899.0,
    )

    previous = {
        p_old.key: {"product": p_old.to_dict(), "last_seen": "2024-01-01"},
    }
    new_products, price_changes = storage.detect_changes([p_new], previous)
    assert len(new_products) == 0
    assert len(price_changes) == 1
    assert price_changes[0].old_price == 999.0
    assert price_changes[0].new_price == 899.0


def test_detect_changes_no_change(tmp_path):
    path = str(tmp_path / "state.json")
    storage = JsonStorage(path)
    p = Product(
        site="test", category=Category.AIR, title="MacBook Air M2",
        chip="M2", ram_gb=8, storage_gb=256, price=999.0,
    )
    previous = {
        p.key: {"product": p.to_dict(), "last_seen": "2024-01-01"},
    }
    new_products, price_changes = storage.detect_changes([p], previous)
    assert len(new_products) == 0
    assert len(price_changes) == 0


def test_load_missing_file(tmp_path):
    path = str(tmp_path / "missing.json")
    storage = JsonStorage(path)
    assert storage.load() == {}


def test_load_corrupted_file(tmp_path):
    path = str(tmp_path / "corrupt.json")
    with open(path, "w") as f:
        f.write("not json")
    storage = JsonStorage(path)
    assert storage.load() == {}
