from flask import Blueprint, redirect, url_for, session, flash, render_template,request
from app import db
from app.models import CartItem, Product,Order
from datetime import datetime


cart_bp = Blueprint('cart', __name__, url_prefix='/cart')


@cart_bp.route('/add/<int:product_id>')
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash('Nejdříve se přihlaš', 'warning')
        return redirect(url_for('auth.login'))

    item = CartItem.query.filter_by(
        user_id=session['user_id'],
        product_id=product_id
    ).first()

    if item:
        item.quantity += 1
    else:
        item = CartItem(
            user_id=session['user_id'],
            product_id=product_id,
            quantity=1
        )
        db.session.add(item)

    db.session.commit()
    flash('Produkt přidán do košíku', 'success')
    return redirect(url_for('main.hodinky'))


@cart_bp.route('/')
def kosik():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    items = CartItem.query.filter_by(user_id=session['user_id']).all()
    return render_template('kosik.html', items=items)

@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    item = CartItem.query.get_or_404(item_id)

    # bezpečnost – aby si uživatel nemaže cizí košík
    if item.user_id != session['user_id']:
        flash('Neoprávněná akce', 'danger')
        return redirect(url_for('cart.kosik'))

    db.session.delete(item)
    db.session.commit()

    flash('Produkt odebrán z košíku', 'info')
    return redirect(url_for('cart.kosik'))








@cart_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    items = CartItem.query.filter_by(user_id=session['user_id']).all()

    if not items:
        flash('Košík je prázdný', 'warning')
        return redirect(url_for('cart.kosik'))

    total = sum(item.product.cena * item.quantity for item in items)

    if request.method == 'POST':
        card = request.form['card_number']
        month = request.form['exp_month']
        year = request.form['exp_year']
        cvc = request.form['cvc']

        # validace čísla karty
        if not card.isdigit() or len(card) != 16:
            flash('Neplatné číslo karty', 'danger')
            return redirect(url_for('cart.checkout'))

        # validace CVC
        if not cvc.isdigit() or len(cvc) != 3:
            flash('Neplatný CVC kód', 'danger')
            return redirect(url_for('cart.checkout'))

        try:
            month = int(month)
            year = int(year)
        except ValueError:
            flash('Neplatné datum expirace', 'danger')
            return redirect(url_for('cart.checkout'))

        if month < 1 or month > 12:
            flash('Neplatný měsíc expirace', 'danger')
            return redirect(url_for('cart.checkout'))

        from datetime import datetime
        now = datetime.now()
        if year < now.year or (year == now.year and month < now.month):
            flash('Karta je expirovaná', 'danger')
            return redirect(url_for('cart.checkout'))

        # SIMULACE ÚSPĚŠNÉ PLATBY
        order = Order(
            user_id=session['user_id'],
            total_price=total
        )
        db.session.add(order)

        for item in items:
            db.session.delete(item)

        db.session.commit()

        flash('Platba proběhla úspěšně ✔', 'success')
        return redirect(url_for('auth.account'))

    # ⬇⬇⬇ TENHLE ŘÁDEK TAM MUSÍ BÝT ⬇⬇⬇
    return render_template('checkout.html', total=total)




@cart_bp.route('/order/<int:order_id>/invoice')
def invoice(order_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    order = Order.query.get_or_404(order_id)

    # bezpečnost – jen vlastní objednávky
    if order.user_id != session['user_id']:
        flash('Neoprávněný přístup', 'danger')
        return redirect(url_for('auth.account'))

    return render_template('invoice.html', order=order)


