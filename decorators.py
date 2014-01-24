import flask
from functools import wraps
from google.appengine.api import users


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if users.get_current_user():
            return f(*args, **kwargs)
        else:
            flask.redirect(users.create_login_url('/'))
    return decorated_function
