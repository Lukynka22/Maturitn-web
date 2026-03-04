from flask import Blueprint, render_template
from app.models import Product
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')
@main_bp.route('/about')
def about():
    return render_template('about.html')
@main_bp.route('/hodinky')
def hodinky():
    produkty = Product.query.all()
    return render_template('hodinky.html', produkty=produkty)
