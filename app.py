from flask import Flask, render_template, request, redirect, session, url_for, flash
from models import db, User, Studio
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secret_key_123")

# =========================
# DATABASE CONFIG (VERCEL)
# =========================
DB_PATH = os.path.join("/tmp", "database.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DB_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# =========================
# INIT DATABASE + ADMIN
# =========================
with app.app_context():
    db.create_all()

    # AUTO CREATE ADMIN (USERNAME: admin | PASSWORD: prayoga)
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", is_admin=True)
        admin.set_password("prayoga")
        db.session.add(admin)
        db.session.commit()

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return redirect("/login")

# =========================
# LOGIN
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
            session["is_admin"] = user.is_admin

            if user.is_admin:
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
def index():
    if "user_id" not in session or session.get("is_admin"):
        return redirect("/login")

    studios = Studio.query.all()
    return render_template("index.html", studios=studios)

@app.route("/add", methods=["POST"])
def add():
    if "user_id" not in session or session.get("is_admin"):
        return redirect("/login")

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
def admin():
    if "user_id" not in session or not session.get("is_admin"):
        return redirect("/login")

    users = User.query.all()
    studios = Studio.query.all()
    return render_template("admin.html", users=users, studios=studios)

@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" not in session or not session.get("is_admin"):
        return redirect("/login")

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
