from functools import wraps
from flask import g, request, redirect, url_for
from flask_login import current_user
from app.models import Panelist

# This is used as a decorator function for the views.  A view with 
# 'login_required' decorator will only get displayed if a user is logged in.
# Otherwise, the user is redirected to the login template.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated == False:
            return redirect(url_for('auth.login', next=request.url))
        else:
            return f(*args, **kwargs)
    return decorated_function

