from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user, login_user, logout_user
from forms import RegistrationForm, PanelistDetailsForm, PanelistLoginForm
from app.models import Panelist
from app.__init__ import db


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Endpoint for creating a username and password to log in.

    On GET request:
        Email field is pre-populated with the session data from the landing
        page's email input form.  If they enter it there then there is no
        reason to enter it again.
    
    On POST request:
        email, password, and confirm_password fields are validated and then
        a query checks to see if there is already a Panelist registered with 
        that given email.  If there is, an error is flashed saying so.  If
        there is not, then the email and the hashed password are inserted and
        commited into the Panelists table.
        """

    # TODO: Probably not great to use session data.

    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate():
        # Assign form data to variables.
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        # check to see if there exists a user with the given email.
        # Flash error if so, and create a user with that email if not.
        user_to_register = Panelist.query.filter_by(email=email).first()
        if user_to_register:
            error = 'User {} is already registered.'.format(email)
        else:
            # DO NOT STORE ACTUAL PASSWORD, INSTEAD STORE HASHED PASSWORD.
            user_to_register = Panelist(email=email, password=generate_password_hash(password))
            db.session.add(user_to_register)
            db.session.commit()

            # This part is sketchy. Store email in session so that it can
            # be accessed to run a query in the next page.
            session['email'] = email
            return redirect(url_for('auth.details'))
        
        flash(error)
    
    # Pre-populate the form with the email in session if the user entered their
    # email into the input on the index page.
    form.email.data = session['email']
    return render_template('auth/register.html', form=form)


@bp.route('/details/', methods=('GET', 'POST'))
def details():
    """Endpoint for inputting demographic information after registration.

    Currently this is accessible by URL but ideally it is locked for access
    solely after succesfully registering with email and password.

    On GET request:
        Display HTML template with the PanelistDetailsForm.
        Display the email, firstname, and lastname of the panelist to update.

    On POST Request:
        Validate and request the form inputs.
        Query to get the panelist to update using session email.
        Update the fields of that panelist.
        Merge updated fields to the session.
        Commit session changes.
        Redirect to admin page to determine if it worked.

        TODO:Login the user and redirect to home.
    """

    # TODO: Use the lastrowid method/attribute of the db cursor object as the
    # way to designate the panelist_id to update.

    form = PanelistDetailsForm(request.form)

    # This is the sketchy part.  Query the DB using session data.
    panelist_to_update = Panelist.query.filter_by(email=session['email']).first()

    if request.method == 'POST' and form.validate():
        # Assign form data to the panelist attributes.
        panelist_to_update.firstname = form.firstname.data
        panelist_to_update.lastname = form.lastname.data
        panelist_to_update.dob = form.dob.data
        panelist_to_update.race = form.race.data
        panelist_to_update.gender = form.gender.data
        panelist_to_update.region = form.region.data

        # Need to merge so that the attribute values are written to the DB.
        db.session.merge(panelist_to_update)
        db.session.commit()

        # Query to get the same panelist object and pass it into Flask-Login's
        # login_user function to log that user in.
        panelist_to_login = Panelist.query.filter_by(email=session['email']).first()
        login_user(panelist_to_login)
        
        # Redirect to the home page.
        return redirect(url_for('other_views.home'))
    
    return render_template('auth/details.html', form=form, panelist_to_update=panelist_to_update)


@bp.route('/login/', methods=(['GET', 'POST']))
def login():
    """Endpoint for logging in a user based on their provided email and password.

    On GET request:
        Display HTML template with PanelistLoginForm.

    On POST request:
        1. Validate email and password fields.
        2. Query Panelists for that email and if no such row exists or the
           hashed password does not match the stored info, then flash error.
        3. Otherwise create a User object with that query and pass to 
           login_user().  Then redirect to the home page.
    """

    form = PanelistLoginForm(request.form)

    if request.method == 'POST' and form.validate():
        # Assign form data to variables
        email = form.email.data
        password = form.password.data

        # Get the panelist with the given email.  If none or the password is 
        # incorrect, flash error.
        panelist_to_login = Panelist.query.filter_by(email=email).first()
        error = None

        if panelist_to_login is None:
            error = 'Incorrect username or password.'
        
        # Use Werkzeug functions to use hashing since we never 
        # saved the actual password text.
        elif not check_password_hash(panelist_to_login.password, password):
            error = 'Incorrect username or password.'
        elif error is None:
            session.clear()
            # Log the user in and redirect to home page.
            login_user(panelist_to_login)
            return redirect(url_for('other_views.home'))

        flash(error)

    return render_template('auth/login.html', form=form)


@bp.route('/logout/')
def logout():
    """This will always be a GET request to clear session, logout_user(), and
    redirect to the landing page"""

    # Clear the session and use Flask-Login's logout_user.
    # Redirect to the landing page.
    session.clear()
    logout_user()
    return redirect(url_for('other_views.index'))