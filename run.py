from app import create_app, db

from app.models import Product, User

app = create_app()   # ← NEJDŘÍV vytvoříme app

# vytvoření tabulek + naplnění dat
with app.app_context():
    db.create_all()

    # NAHARD PRODUKTY (spustí se jen jednou)
    if Product.query.count() == 0:
        produkty = [
            Product(
                nazev="Rolex",
                popis="Luxusní švýcarské hodinky",
                cena=359999,
                skladem=3,
                image="obrazky/rolexy.webp"
            ),
            Product(
                nazev="Kudoke",
                popis="Německá ruční výroba",
                cena=32900,
                skladem=5,
                image="obrazky/2hodinky.webp"
            ),
            Product(
                nazev="Casio",
                popis="Digitální klasika",
                cena=28900,
                skladem=10,
                image="obrazky/apple.webp"
            ),
            Product(
                nazev="Invicta",
                popis="Sportovní hodinky",
                cena=43000,
                skladem=2,
                image="obrazky/4hodinky.webp"
            )
        ]

        db.session.add_all(produkty)
        db.session.commit()
with app.app_context():
    print(db.inspect(db.engine).get_table_names())

if __name__ == '__main__':
    app.run(debug=True)
