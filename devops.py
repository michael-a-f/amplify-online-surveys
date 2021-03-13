from __init__ import db, create_app
from models import *


def initialize_db():
    app=create_app()
    with app.app_context():
        try:
            db.create_all()
            db.session.add(Race(race='Black or African American'))
            db.session.add(Race(race='White'))
            db.session.add(Race(race='Asian'))
            db.session.add(Race(race='Hispanic or Latino'))
            db.session.add(Race(race='American Indian or Alaska Native'))
            db.session.add(Race(race='Native Hawaiian or Other Pacific Islander'))
            print('Races added')
            db.session.add(Gender(gender='Male'))
            db.session.add(Gender(gender='Female'))
            db.session.add(Gender(gender='Non-binary'))
            print('Genders added')
            db.session.add(Region(region='Northeast'))
            db.session.add(Region(region='Midwest'))
            db.session.add(Region(region='West'))
            db.session.add(Region(region='South'))
            print('Regions added')
            db.session.add(Challenge(task='Complete a survey', award=20))
            db.session.add(Challenge(task='Publish a survey', award=20))
            db.session.add(Challenge(task='Redeem a reward', award=10))
            print('Challenges added')
            db.session.commit()
            print('All tables initialized and populated with data.')
        except:
            print('There was an error populating Race, Gender, Region tables with data.')


def wipe_db():
    try:
        db.drop_all(app=create_app())
        print('DB wiped clean.')
    except:
        print('There was an issue dropping all tables.')

initialize_db()
#wipe_db()