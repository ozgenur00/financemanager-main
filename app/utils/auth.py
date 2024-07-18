from flask import session, g
from app.models.user import User

CURR_USER_KEY = "user_id"

def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id
    g.user = user

def do_logout():
    """Logout user."""
    print(f"Session before logout: {session}")
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    print(f"Session after logout: {session}")
    g.user = None
