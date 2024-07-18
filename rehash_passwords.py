from app import app, db
from app.models.user import User
from flask_bcrypt import generate_password_hash

def rehash_passwords():
    with app.app_context():
        users = User.query.all()
        for user in users:
            if user.password.startswith("scrypt:"):
                plain_password = "default_password"
                user.password = generate_password_hash(plain_password).decode('utf-8')
                db.session.add(user)
        db.session.commit()
        print("All passwords have been rehashed.")

if __name__ == '__main__':
    rehash_passwords()
