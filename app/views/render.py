from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')







@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Přihlášení úspěšné!', 'success')
            return redirect(url_for('auth.account'))
        else:
            flash('Nesprávné přihlašovací údaje.', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Uživatel nebo e-mail již existuje.', 'warning')
        else:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registrace úspěšná! Nyní se můžete přihlásit.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/account')
def account():
    # Pokud není přihlášený, přesměruj na login
    if 'user_id' not in session:
        flash('Nejdříve se přihlaste.', 'warning')
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    return render_template('account.html', user=user)



@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Odhlášení proběhlo úspěšně.', 'info')
    return redirect(url_for('main.index'))



