from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models import User
import re
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def is_valid_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$'
    return re.match(pattern, password)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        raw_password = request.form['password']

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Uživatel nebo e-mail již existuje.', 'warning')
            return render_template('register.html')

        if not is_valid_password(raw_password):
            flash(
                'Heslo musí mít alespoň 8 znaků a obsahovat velké písmeno, malé písmeno, číslo a speciální znak.',
                'danger'
            )
            return render_template('register.html')

        hashed_password = generate_password_hash(raw_password)

        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registrace úspěšná! Nyní se můžete přihlásit.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/account', methods=['GET', 'POST'])
def account():
    if 'user_id' not in session:
        flash('Nejdříve se přihlaste.', 'warning')
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if not user:
        session.clear()
        flash('Uživatel nebyl nalezen.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        if 'avatar' not in request.files:
            flash('Soubor nebyl vybrán.', 'warning')
            return redirect(url_for('auth.account'))

        file = request.files['avatar']

        if file.filename == '':
            flash('Nevybral jsi žádný soubor.', 'warning')
            return redirect(url_for('auth.account'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            new_filename = f"user_{user.id}.{ext}"

            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            # smaže starý avatar, pokud existuje a má jinou příponu
            if user.avatar and user.avatar != new_filename:
                old_file = os.path.join(upload_folder, user.avatar)
                if os.path.exists(old_file):
                    os.remove(old_file)

            filepath = os.path.join(upload_folder, new_filename)
            file.save(filepath)

            user.avatar = new_filename
            db.session.commit()

            flash('Profilovka byla úspěšně nahrána.', 'success')
        else:
            flash('Povolené formáty jsou: png, jpg, jpeg, gif, webp.', 'danger')

        return redirect(url_for('auth.account'))

    return render_template('account.html', user=user)


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Odhlášení proběhlo úspěšně.', 'info')
    return redirect(url_for('main.index'))
