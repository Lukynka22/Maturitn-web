from flask import Blueprint, redirect, url_for, session, flash, render_template, request, make_response
from app import db
from app.models import CartItem, Product, Order, OrderItem
from datetime import datetime
import re
from fpdf import FPDF

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')


def luhn_check(card_number: str) -> bool:
    if not card_number.isdigit():
        return False

    total = 0
    reversed_digits = card_number[::-1]

    for i, digit in enumerate(reversed_digits):
        number = int(digit)

        if i % 2 == 1:
            number *= 2
            if number > 9:
                number -= 9

        total += number

    return total % 10 == 0


def card_not_expired(month: int, year: int) -> bool:
    now = datetime.now()
    return year > now.year or (year == now.year and month >= now.month)


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

    if item.user_id != session['user_id']:
        flash('Neoprávněná akce', 'danger')
        return redirect(url_for('cart.kosik'))

    db.session.delete(item)
    db.session.commit()

    flash('Produkt odebrán z košíku', 'info')
    return redirect(url_for('cart.kosik'))


@cart_bp.route('/delivery', methods=['GET', 'POST'])
def delivery():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    items = CartItem.query.filter_by(user_id=session['user_id']).all()

    if not items:
        flash('Košík je prázdný', 'warning')
        return redirect(url_for('cart.kosik'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        street = request.form.get('street', '').strip()
        city = request.form.get('city', '').strip()
        zip_code = request.form.get('zip_code', '').strip()
        country = request.form.get('country', '').strip()
        phone = request.form.get('phone', '').strip()
        shipping = request.form.get('shipping', '').strip()
        note = request.form.get('note', '').strip()

        if not full_name or not street or not city or not zip_code or not country or not phone or not shipping:
            flash('Vyplň všechny povinné doručovací údaje', 'danger')
            return redirect(url_for('cart.delivery'))

        if not re.fullmatch(r'\d{5}', zip_code):
            flash('PSČ musí obsahovat přesně 5 číslic', 'danger')
            return redirect(url_for('cart.delivery'))

        if not re.fullmatch(r'\d{9}', phone):
            flash('Telefon musí obsahovat přesně 9 číslic bez +420', 'danger')
            return redirect(url_for('cart.delivery'))

        session['delivery_info'] = {
            'full_name': full_name,
            'street': street,
            'city': city,
            'zip_code': zip_code,
            'country': country,
            'phone': phone,
            'shipping': shipping,
            'note': note
        }

        return redirect(url_for('cart.checkout'))

    return render_template('delivery.html')


@cart_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    items = CartItem.query.filter_by(user_id=session['user_id']).all()

    if not items:
        flash('Košík je prázdný', 'warning')
        return redirect(url_for('cart.kosik'))

    delivery_info = session.get('delivery_info')
    if not delivery_info:
        flash('Nejdříve vyplň doručovací údaje', 'warning')
        return redirect(url_for('cart.delivery'))

    total = sum(item.product.cena * item.quantity for item in items)

    if request.method == 'POST':
        card = request.form.get('card_number', '').replace(' ', '').strip()
        month = request.form.get('exp_month', '').strip()
        year = request.form.get('exp_year', '').strip()
        cvc = request.form.get('cvc', '').strip()

        if not card:
            flash('Vyplň číslo karty', 'danger')
            return render_template('checkout.html', total=total, delivery=delivery_info)

        if not card.isdigit():
            flash('Číslo karty musí obsahovat pouze číslice', 'danger')
            return render_template('checkout.html', total=total, delivery=delivery_info)

        if len(card) < 13 or len(card) > 19:
            flash('Číslo karty musí mít 13 až 19 číslic', 'danger')
            return render_template('checkout.html', total=total, delivery=delivery_info)

        if not luhn_check(card):
            flash('Neplatné číslo karty', 'danger')
            return render_template('checkout.html', total=total, delivery=delivery_info)

        if not month.isdigit() or not year.isdigit():
            flash('Neplatné datum expirace', 'danger')
            return render_template('checkout.html', total=total, delivery=delivery_info)

        month = int(month)
        year = int(year)

        if month < 1 or month > 12:
            flash('Neplatný měsíc expirace', 'danger')
            return render_template('checkout.html', total=total, delivery=delivery_info)

        if year < 100:
            year += 2000

        if not card_not_expired(month, year):
            flash('Karta je expirovaná', 'danger')
            return render_template('checkout.html', total=total, delivery=delivery_info)

        if cvc and (not cvc.isdigit() or len(cvc) > 3):
            flash('CVC může mít maximálně 3 číslice', 'danger')
            return render_template('checkout.html', total=total, delivery=delivery_info)

        order = Order(
            user_id=session['user_id'],
            total_price=total,
            created_at=datetime.now()
        )
        db.session.add(order)
        db.session.flush()

        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_name=item.product.nazev,
                quantity=item.quantity,
                unit_price=item.product.cena,
                total_price=item.product.cena * item.quantity
            )
            db.session.add(order_item)
            db.session.delete(item)

        db.session.commit()

        session.pop('delivery_info', None)

        flash('Platba proběhla úspěšně ✔', 'success')
        return redirect(url_for('auth.account'))

    return render_template('checkout.html', total=total, delivery=delivery_info)


@cart_bp.route('/order/<int:order_id>/invoice')
def invoice(order_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    order = Order.query.get_or_404(order_id)

    if order.user_id != session['user_id']:
        flash('Neoprávněný přístup', 'danger')
        return redirect(url_for('auth.account'))

    return render_template('invoice.html', order=order)


@cart_bp.route('/order/<int:order_id>/invoice/download')
def download_invoice(order_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    order = Order.query.get_or_404(order_id)

    if order.user_id != session['user_id']:
        flash('Neoprávněný přístup', 'danger')
        return redirect(url_for('auth.account'))

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, f"FAKTURA #{order.id:04d}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(95, 8, "Dodavatel:", new_x="RIGHT", new_y="TOP")
    pdf.cell(95, 8, "Odberatel:", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(95, 7, "CHRONO", new_x="RIGHT", new_y="TOP")
    pdf.cell(95, 7, f"{order.user.username}", new_x="LMARGIN", new_y="NEXT")

    pdf.cell(95, 7, "Luxusni hodinky", new_x="RIGHT", new_y="TOP")
    pdf.cell(95, 7, f"{order.user.email}", new_x="LMARGIN", new_y="NEXT")

    pdf.cell(95, 7, "ICO: 00000000", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(80, 10, "Produkt", border=1)
    pdf.cell(20, 10, "Ks", border=1)
    pdf.cell(40, 10, "Cena/ks", border=1)
    pdf.cell(50, 10, "Celkem", border=1, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    for item in order.items:
        product_name = item.product_name[:35]
        pdf.cell(80, 10, product_name, border=1)
        pdf.cell(20, 10, str(item.quantity), border=1)
        pdf.cell(40, 10, f"{item.unit_price} Kc", border=1)
        pdf.cell(50, 10, f"{item.total_price} Kc", border=1, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(140, 10, "Celkem", border=1)
    pdf.cell(50, 10, f"{order.total_price} Kc", border=1, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "Faktura je plne uhrazena.", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Dekujeme za nakup u CHRONO.", new_x="LMARGIN", new_y="NEXT")

    pdf_output = bytes(pdf.output())

    response = make_response(pdf_output)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f'attachment; filename="faktura_{order.id:04d}.pdf"'
    return response
