import os
import sys
import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

test_db = SQLAlchemy()


class TestUser(test_db.Model):
    __tablename__ = "test_user"

    id = test_db.Column(test_db.Integer, primary_key=True)
    username = test_db.Column(test_db.String(50), unique=True, nullable=False)
    email = test_db.Column(test_db.String(120), unique=True, nullable=False)


@pytest.fixture(scope="function")
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_secret_key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    test_db.init_app(app)

    @app.route("/")
    def index():
        return "Home page OK", 200

    @app.route("/login")
    def login():
        return "Login page OK", 200

    @app.route("/about")
    def about():
        return "About page OK", 200

    @app.route("/cart/")
    def cart():
        return "Cart page OK", 200

    @app.route("/users")
    def users():
        count = TestUser.query.count()
        return f"Users count: {count}", 200

    with app.app_context():
        test_db.create_all()
        test_db.session.add(TestUser(username="testuser", email="test@test.cz"))
        test_db.session.commit()

    yield app

    with app.app_context():
        test_db.session.remove()
        test_db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
