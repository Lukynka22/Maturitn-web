from flask import Blueprint, render_template, request, url_for
from app.models import Product

from sqlalchemy import func
from app.models import Product

from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')
@main_bp.route('/about')
def about():
    return render_template('about.html')




@main_bp.route('/hodinky')
def hodinky():

    search = request.args.get("q")
    category = request.args.get("category")

    query = Product.query

    if search:
        query = query.filter(Product.nazev.ilike(f"%{search}%"))

    if category:
        query = query.filter(Product.kategorie == category)

    produkty = query.all()

    breadcrumbs = [
        ("Domů", url_for("main.index")),
        ("Hodinky", url_for("main.hodinky"))
    ]

    if category:
        breadcrumbs.append((category, None))

    return render_template(
        "hodinky.html",
        produkty=produkty,
        breadcrumbs=breadcrumbs
    )


@main_bp.route('/statistika')
def statistika():
    vysledky = db.session.query(
        Product.kategorie,
        func.count(Product.id)
    ).group_by(Product.kategorie).all()

    labels = []
    values = []

    for kategorie, pocet in vysledky:
        labels.append(kategorie if kategorie else "Bez kategorie")
        values.append(pocet)

    breadcrumbs = [
        ("Domů", url_for("main.index")),
        ("Statistika", None)
    ]

    return render_template(
        "statistika.html",
        labels=labels,
        values=values,
        breadcrumbs=breadcrumbs
    )

