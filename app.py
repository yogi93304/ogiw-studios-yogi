from flask import Flask, render_template, request, redirect, session, url_for, flash
from models import db, User, Studio
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secret_key_123")

# =========================
# DATABASE (VERCEL SAFE)
# =========================
DB_PATH = os.path.join("/tmp", "database.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DB_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# =========================
# INIT DB + DEFAULT ADMIN
# =========================
with app.app_context():
    db.create_all()

    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", role="admin")
        admin.set_password("prayoga")
        db.session.add(admin)
        db.session.commit()

# =========================
# RBAC DECORATOR
# =========================
def role_required(role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session or session.get("role") != role:
                return redirect("/login")
            return f(*args, **kwargs)
        return decorated
    return wrapper

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return redirect("/login")

# =========================
# LOGIN (NO ROLE INPUT)
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role

            if user.role == "admin":
                return redirect("/admin")
            return redirect("/index")

        flash("Username atau password salah")
        return redirect("/login")

    return render_template("login.html")

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# =========================
# STAFF PAGE
# =========================
@app.route("/index")
@role_required("staff")
def index():
    studios = Studio.query.all()
    return render_template("index.html", studios=studios)

@app.route("/add", methods=["POST"])
@role_required("staff")
def add():
    name = request.form.get("name")
    start_time = request.form.get("start_time")
    hours = int(request.form.get("hours"))

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
    return redirect("/index")

# =========================
# ADMIN PAGE
# =========================
@app.route("/admin")
@role_required("admin")
def admin():
    users = User.query.all()
    studios = Studio.query.all()
    return render_template("admin.html", users=users, studios=studios)

@app.route("/create_staff", methods=["POST"])
@role_required("admin")
def create_staff():
    username = request.form.get("username")
    password = request.form.get("password")

    if User.query.filter_by(username=username).first():
        flash("Username sudah ada")
        return redirect("/admin")

    staff = User(username=username, role="staff")
    staff.set_password(password)

    db.session.add(staff)
    db.session.commit()

    flash("Staff berhasil dibuat")
    return redirect("/admin")

@app.route("/delete/<int:id>")
@role_required("admin")
def delete(id):
    studio = Studio.query.get(id)
    if studio:
        db.session.delete(studio)
        db.session.commit()
    return redirect("/admin")

# =========================
# LOCAL RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)