import sys
import os
import tempfile
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "SECRET_KEY": "test",
    })

    print("DB:", app.config["SQLALCHEMY_DATABASE_URI"])

    if "mysql" in app.config["SQLALCHEMY_DATABASE_URI"]:
        raise Exception("TEST BĚŽÍ NA REÁLNÉ DB!")

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(
            username="testuser",
            email="test@test.cz",
            password=generate_password_hash("testpass")
        )
        db.session.add(user)
        db.session.commit()
        return user
