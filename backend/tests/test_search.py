import pytest


@pytest.fixture
def lot(make_vehicle):
    make_vehicle(make="Toyota", model="Corolla", category="Sedan", price=20000, quantity=4)
    make_vehicle(make="Toyota", model="Fortuner", category="SUV", price=45000, quantity=0)
    make_vehicle(make="Honda", model="City", category="Sedan", price=18000, quantity=2)
    make_vehicle(make="Mahindra", model="Thar", category="SUV", price=22000, quantity=6)
    make_vehicle(make="Tesla", model="Model 3", category="Electric", price=52000, quantity=1)


def search(client, headers, **params):
    response = client.get("/api/vehicles/search", params=params, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def models(results):
    return sorted(v["model"] for v in results)


def test_search_needs_login(client):
    assert client.get("/api/vehicles/search").status_code == 401


def test_no_filters_returns_everything(client, user_headers, lot):
    assert len(search(client, user_headers)) == 5


def test_search_by_make_ignores_case(client, user_headers, lot):
    assert models(search(client, user_headers, make="toyota")) == ["Corolla", "Fortuner"]


def test_search_by_partial_model(client, user_headers, lot):
    assert models(search(client, user_headers, model="for")) == ["Fortuner"]


def test_search_by_category(client, user_headers, lot):
    assert models(search(client, user_headers, category="suv")) == ["Fortuner", "Thar"]


def test_category_match_is_exact_not_partial(client, user_headers, lot):
    assert search(client, user_headers, category="Sed") == []


def test_search_by_price_range_is_inclusive(client, user_headers, lot):
    results = search(client, user_headers, min_price=18000, max_price=22000)
    assert models(results) == ["City", "Corolla", "Thar"]


def test_only_min_price(client, user_headers, lot):
    assert models(search(client, user_headers, min_price=45000)) == ["Fortuner", "Model 3"]


def test_only_max_price(client, user_headers, lot):
    assert models(search(client, user_headers, max_price=18000)) == ["City"]


def test_filters_combine(client, user_headers, lot):
    assert models(search(client, user_headers, category="Sedan", max_price=19000)) == ["City"]


def test_free_text_query_looks_at_make_model_and_category(client, user_headers, lot):
    assert models(search(client, user_headers, q="electric")) == ["Model 3"]
    assert models(search(client, user_headers, q="hon")) == ["City"]


def test_in_stock_only_hides_sold_out(client, user_headers, lot):
    assert "Fortuner" not in models(search(client, user_headers, in_stock=True))


def test_min_price_above_max_price_is_bad_request(client, user_headers, lot):
    response = client.get("/api/vehicles/search", params={"min_price": 500, "max_price": 100}, headers=user_headers)
    assert response.status_code == 400


def test_negative_price_filter_is_rejected(client, user_headers):
    response = client.get("/api/vehicles/search", params={"min_price": -1}, headers=user_headers)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "sort, expected_first",
    [("price_asc", "City"), ("price_desc", "Model 3"), ("stock_desc", "Thar")],
)
def test_sorting(client, user_headers, lot, sort, expected_first):
    assert search(client, user_headers, sort=sort)[0]["model"] == expected_first


def test_unknown_sort_is_rejected(client, user_headers):
    response = client.get("/api/vehicles/search", params={"sort": "random"}, headers=user_headers)
    assert response.status_code == 422


def test_categories_endpoint_lists_distinct_categories(client, user_headers, lot):
    response = client.get("/api/vehicles/categories", headers=user_headers)
    assert response.status_code == 200
    assert response.json() == ["Electric", "SUV", "Sedan"]
