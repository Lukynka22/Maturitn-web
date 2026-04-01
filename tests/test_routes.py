def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Home page OK" in response.data


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login page OK" in response.data


def test_about_page(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert b"About page OK" in response.data


def test_cart_page(client):
    response = client.get("/cart/")
    assert response.status_code == 200
    assert b"Cart page OK" in response.data


def test_users_route_memory_db(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert b"Users count: 1" in response.data


def test_nonexistent_route_returns_404(client):
    response = client.get("/neexistuje")
    assert response.status_code == 404
