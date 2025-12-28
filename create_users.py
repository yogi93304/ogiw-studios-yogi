from app import app, db
from models import User

with app.app_context():
    db.create_all()

    if not User.query.filter_by(username="prayoga").first():
        admin = User(username="prayoga", is_admin=True)
        admin.set_password("prayoga")
        db.session.add(admin)

    if not User.query.filter_by(username="yogi").first():
        staff = User(username="yogi", is_admin=False)
        staff.set_password("yogi")
        db.session.add(staff)

    db.session.commit()
    print("Admin & Staff berhasil dibuat")
