def test_login_page(client):
    response = client.get("/auth/login")
    assert response.status_code == 200


def test_register_page(client):
    response = client.get("/auth/register")
    assert response.status_code == 200


def test_register_post(client):
    response = client.post(
        "/auth/register",
        data={
            "username": "novyuzivatel",
            "email": "novy@test.cz",
            "password": "heslo123"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    # po úspěšné registraci se má přesměrovat na login stránku
    assert b'name="username"' in response.data
    assert b'name="password"' in response.data
