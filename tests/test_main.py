def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_about_page(client):
    response = client.get("/about")
    assert response.status_code == 200


def test_404_page(client):
    response = client.get("/neexistuje")
    assert response.status_code == 404
