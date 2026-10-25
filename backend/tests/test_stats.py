import pytest

from tests.test_inventory import purchase


@pytest.fixture
def busy_lot(client, user_headers, make_vehicle):
    corolla = make_vehicle(make="Toyota", model="Corolla", category="Sedan", price=20000, quantity=5)
    thar = make_vehicle(make="Mahindra", model="Thar", category="SUV", price=15000, quantity=2)
    make_vehicle(make="Tata", model="Nexon", category="SUV", price=10000, quantity=0)
    purchase(client, user_headers, corolla["id"], quantity=2)
    purchase(client, user_headers, thar["id"], quantity=1)
    purchase(client, user_headers, corolla["id"], quantity=1)


def summary(client, headers):
    response = client.get("/api/stats/summary", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def test_stats_are_admin_only(client, user_headers):
    assert client.get("/api/stats/summary", headers=user_headers).status_code == 403


def test_empty_lot_gives_zeros(client, admin_headers):
    stats = summary(client, admin_headers)
    assert stats["total_models"] == 0
    assert stats["units_in_stock"] == 0
    assert stats["inventory_value"] == 0
    assert stats["units_sold"] == 0
    assert stats["revenue"] == 0
    assert stats["low_stock"] == []
    assert stats["top_sellers"] == []


def test_stock_numbers(client, admin_headers, busy_lot):
    stats = summary(client, admin_headers)
    assert stats["total_models"] == 3
    # corolla 2 left, thar 1 left, nexon 0
    assert stats["units_in_stock"] == 3
    assert stats["inventory_value"] == 2 * 20000 + 1 * 15000
    assert stats["out_of_stock"] == 1


def test_sales_numbers(client, admin_headers, busy_lot):
    stats = summary(client, admin_headers)
    assert stats["units_sold"] == 4
    assert stats["revenue"] == 3 * 20000 + 15000


def test_low_stock_uses_threshold_and_lowest_first(client, admin_headers, busy_lot):
    low = summary(client, admin_headers)["low_stock"]
    assert [v["model"] for v in low] == ["Nexon", "Thar", "Corolla"]


def test_top_sellers_ranked_by_units(client, admin_headers, busy_lot):
    top = summary(client, admin_headers)["top_sellers"]
    assert top[0] == {"make": "Toyota", "model": "Corolla", "units_sold": 3, "revenue": 60000}
    assert top[1]["model"] == "Thar"


def test_category_breakdown(client, admin_headers, busy_lot):
    categories = {row["category"]: row for row in summary(client, admin_headers)["by_category"]}
    assert categories["SUV"] == {"category": "SUV", "models": 2, "units": 1}
    assert categories["Sedan"] == {"category": "Sedan", "models": 1, "units": 2}
