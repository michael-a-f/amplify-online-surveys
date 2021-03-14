import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
#from app.decorators import *
#from app.models import *



# Globally accessible libraries
login_manager = LoginManager()
db = SQLAlchemy()


def create_app(test_config=None):
    """Create and configure the app.

    Application factory style used here to make sure there is no global
    instance of app. This is much more practical way of creating the
    application instance and allows for integration of blueprints and easier
    deployment to a web server.  Conifgs are in config.py under the instance folder.
    """

    # Initialize the core application.
    app = Flask(__name__)

    # Configure application.
    #app.config.from_pyfile('config.py', silent=True)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', None)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', None)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', None)
    
    # Imports
    import models
    import decorators
    import forms


    # Define a user_loader callback for the LoginManager instance.
    @login_manager.user_loader
    def load_user(unicode_user_id):
        """Intakes a unicode user_id and returns a User object for the panelist
        with that id.

        This converts the unicode back to an integer, queries the Panelists table
        for the panelist with that panelist_id, and returns a User object created
        from that panelist's data.
        """
        try:
            print(unicode_user_id)
            print('Unicode id for the user loader is ' + str(unicode_user_id))
            return Panelist.query.get(int(unicode_user_id))
        except:
            print('Unable to load a user from Panelists with the given unicode ID.')
            return None


    # Initialize plugins
    login_manager.init_app(app)
    db.init_app(app)

    # Register Blueprints
    import auth
    app.register_blueprint(auth.bp)

    import ask
    app.register_blueprint(ask.bp)

    import answer
    app.register_blueprint(answer.bp)

    import redeem
    app.register_blueprint(redeem.bp)

    import other_views
    app.register_blueprint(other_views.bp)
    
    import admin
    app.register_blueprint(admin.bp)


    return app


    