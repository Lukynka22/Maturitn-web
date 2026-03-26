def test_account_redirect_when_not_logged_in(client):
    response = client.get("/auth/account", follow_redirects=False)
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_login_functionality(client, test_user):
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "testpass"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"account" in response.data.lower() or b"testuser" in response.data.lower()


def test_logout(client, test_user):
    client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "testpass"
        },
        follow_redirects=True
    )

    response = client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
