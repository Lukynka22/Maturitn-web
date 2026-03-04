from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import DATABASE, SECRET_KEY







db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://student13:spsnet@dbs.spskladno.cz/vyuka13"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY

    db.init_app(app)

    from app.views.cesty import main_bp
    from app.views.render import auth_bp
    from app.cart.routes import cart_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)

    return app
