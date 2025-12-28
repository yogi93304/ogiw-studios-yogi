from flask import Flask, render_template, request, redirect, session, url_for, flash
from models import db, User, Studio
import os

app = Flask(__name__)
app.secret_key = "secret_key_123"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'instance/database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('home.html')


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin

            if user.is_admin:
                return redirect('/admin')
            else:
                return redirect('/index')

        flash('Username atau password salah')
        return redirect('/login')

    return render_template('login.html')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------------- STAFF PAGE ----------------
@app.route('/index')
def index():
    if 'user_id' not in session or session.get('is_admin'):
        return redirect('/login')

    studios = Studio.query.all()
    return render_template('index.html', studios=studios)


@app.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session or session.get('is_admin'):
        return redirect('/login')

    name = request.form['name']
    start_time = request.form['start_time']
    hours = int(request.form['hours'])

    price = 100000
    total = hours * price

    studio = Studio(
        name=name,
        start_time=start_time,
        hours=hours,
        price_per_hour=price,
        total_price=total
    )

    db.session.add(studio)
    db.session.commit()
    return redirect('/index')


# ---------------- ADMIN PAGE ----------------
@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')

    users = User.query.all()
    studios = Studio.query.all()
    return render_template('admin.html', users=users, studios=studios)


@app.route('/delete/<int:id>')
def delete(id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')

    studio = Studio.query.get(id)
    if studio:
        db.session.delete(studio)
        db.session.commit()

    return redirect('/admin')


if __name__ == '__main__':
    app.run(debug=True)
