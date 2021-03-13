from sqlalchemy.sql import func
#from __init__ import db
from flask_login import UserMixin
from datetime import date

# Subclass UserMixin so that I can use flask_login methods on the Panelist that
# gets logged in.  Without subclassing, I would have to implement like 4 
# attributes/methods manually :(
class Panelist(UserMixin, db.Model):
    """Represents a registered user of the site.

    'Panelist' represents that they are a member of the panel-- a group
    of people that answer surveys.

    Important attributes:
    panelist.surveys: all of the surveys that a panelist has published.

    Backrefs:

    """

    __tablename__ = 'panelists'
    __table_args__ = {'extend_existing': True} 
    # email and password are not nullable because they are needed for 
    # registration.  The rest gets updated after already registered.
    panelist_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    dob = db.Column(db.String(64))
    race = db.Column(db.String(64))
    gender = db.Column(db.String(64))
    region = db.Column(db.String(64))
    joined_date = db.Column(db.DateTime, server_default=func.now())
    point_balance = db.Column(db.Integer, default=0)
    
    # One-to-many relationship.  One panelist can have many surveys.
    surveys = db.relationship('Survey', backref='publisher', lazy=True)

    # One-to-many relationship.  One panelist can have many responses.
    responses = db.relationship('Response', backref='response_panelist', lazy=True)

    # One-to-many relationship.  One panelist can have many redemptions.
    redemptions = db.relationship('Redemption', backref='redemption_panelist', lazy=True)

    # These are not exactly best practice.  Booleans for if a panelist has
    # claimed the challenge.  Oh well, it works and I am not scaling a product.
    redeemed_challenge_1 = db.Column(db.Boolean, default=0)
    redeemed_challenge_2 = db.Column(db.Boolean, default=0)


    def get_age(self):
        """Returns an integer for the age of a panelist given their birthday"""

        return date.today().year - int(self.dob[0:4])

    # This was giving me issues.  Sometimes the built-in get_id method of the
    # UserMixin class would not get called and so I had to implement my own.
    # This works on local machine but we shall see about hosted.
    def get_id(self):
        #print(self.panelist_id)
        unicode_id = self.panelist_id
        #print(unicode_id)
        return unicode_id

    def get_eligible_surveys(self):
        """Returns the Survey objects that a panelist qualifies for.
        
        A Panelist is only eligible for surveys where...
        
        Their Age is within the survey's specified range.
        The survey status is Open ie it still needs responses.
        They are not the publisher (why take own survey?).
        Their Race is in the survey's specified races.
        Their Gender is in the survey's specified genders.
        Their Region is in the survey's specified regions.
        They have not already responded to the survey.
        """
        age = self.get_age()
        eligible_surveys = Survey.query.filter(
            (Survey.min_age <= age),
            (Survey.max_age >= age),
            (Survey.status=='Open'),
            (Survey.publisher_id != self.panelist_id),
            (Survey.races.any(Race.race == self.race)),
            (Survey.genders.any(Gender.gender == self.gender)),
            (Survey.regions.any(Region.region == self.region)),
            (~Survey.responses.any(Response.response_panelist_id == self.panelist_id))
        ).all()
        return eligible_surveys


# Best practice would import this into the forms.py module so that if I add a
# new race, it will automatically be included at registration and survey setup.
class Race(db.Model):
    """These are the race options that a Panelist can identify with.
    
    Nothing is written to this table besides the handful of races I include."""
    __tablename__ = 'races'
    __table_args__ = {'extend_existing': True} 
    race_id = db.Column(db.Integer, primary_key=True)
    race = db.Column(db.String(140), nullable=False)


# Best practice would import this into the forms.py module so that if I add a
# new gender, it will automatically be included at registration and survey setup.
class Gender(db.Model):
    __tablename__ = 'genders'
    __table_args__ = {'extend_existing': True} 
    gender_id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(140), nullable=False)


# Best practice would import this into the forms.py module so that if I add a
# new region, it will automatically be included at registration and survey setup.
class Region(db.Model):
    __tablename__ = 'regions'
    __table_args__ = {'extend_existing': True} 
    region_id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(140), nullable=False)



"""Junction tables needed to make the many-to-many relationships possible.
These are passed in to the 'secondary' parameter in the db relationships
in the Survey class. A Survey object can have many Race/Gender/Region 
objects, and a Race/Gender/Region object can be referebced by many surveys.
"""

survey_races = db.Table('survey_races',
    db.Column('survey_id', db.Integer, db.ForeignKey('surveys.survey_id')),
    db.Column('race_id', db.Integer, db.ForeignKey('races.race_id'))
    )

survey_genders = db.Table('survey_genders',
    db.Column('survey_id', db.Integer, db.ForeignKey('surveys.survey_id')),
    db.Column('gender_id', db.Integer, db.ForeignKey('genders.gender_id'))
    )

survey_regions = db.Table('survey_regions',
    db.Column('survey_id', db.Integer, db.ForeignKey('surveys.survey_id')),
    db.Column('region_id', db.Integer, db.ForeignKey('regions.region_id'))
    )


class Survey(db.Model):
    """Represents a survey --a collection of questions packaged together.

    Panelists can create surveys in the 'Ask' tab. There they can input
    the relevant details like how many people they want to respond, what
    demographics they want their survey to target, etc.

    Important attributes:
    survey.questions: all of the questions for a survey.
    survey.races: all of the races that a survey targets.
    survey.genders: all of the genders that a survey targets.
    survey.regions: all of the regions that a survey targets.

    Backrefs:
    survey.publisher: the panelist who published a survey.
    """

    __tablename__ = 'surveys'
    __table_args__ = {'extend_existing': True} 
    survey_id = db.Column(db.Integer, primary_key=True)
    publisher_id = db.Column(db.Integer, db.ForeignKey('panelists.panelist_id'), nullable=False) # the panelist_id of the publisher
    category = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(64), nullable=False)
    sample_size = db.Column(db.Integer, nullable=False)
    min_age = db.Column(db.Integer, nullable=False)
    max_age = db.Column(db.Integer, nullable=False)
    num_questions = db.Column(db.Integer, default=0)
    point_value = db.Column(db.Integer, default=0)
    status = db.Column(db.String(64), default='Open')
    completes = db.Column(db.Integer, default=0)
    create_date = db.Column(db.DateTime, server_default=func.now())

    # One-to-many relationship.  One survey can have many questions.
    questions = db.relationship('Question', backref='parent_survey', lazy=True)

    # One-to-many relationship.  One survey can have many responses.
    responses = db.relationship('Response', backref='parent_survey', lazy=True)
    
    # Many-to-many relationship using junction tables survey_genders/races/...
    genders = db.relationship('Gender', secondary=survey_genders, lazy='subquery', backref=db.backref('surveys', lazy=True))
    races = db.relationship('Race', secondary=survey_races, lazy='subquery', backref=db.backref('surveys', lazy=True))
    regions = db.relationship('Region', secondary=survey_regions, lazy='subquery', backref=db.backref('surveys', lazy=True))

    #def get_number_questions(self):
    #    num = Question.query.filter_by(parent_survey_id=self.survey_id).count()
    #    return num

    #def get_points_value(self):
    #    points = self.get_number_questions() * 5
    #    return points


class Question(db.Model):
    """Represents a question of a survey.

    Important attributes:
    question.answers: all of the answers for a question.

    Backrefs:
    question.parent_survey: the survey that a question belongs to.
    """

    __tablename__ = 'questions'
    __table_args__ = {'extend_existing': True} 
    question_id = db.Column(db.Integer, primary_key=True)
    parent_survey_id = db.Column(db.Integer, db.ForeignKey('surveys.survey_id'), nullable=False)
    question = db.Column(db.String(140), nullable=False)

    # One-to-many relationship.  One question can have many answers.
    answers = db.relationship('Answer', backref='parent_question', lazy=True)

    # One-to-many relationship.  One question can have many responses.
    responses = db.relationship('Response', backref='parent_question', lazy=True)


class Answer(db.Model):
    """Represents an answer to a question of a survey.

    Backrefs:
    answer.parent_question: the question that an answer belongs to.
    """

    __tablename__ = 'answers'
    __table_args__ = {'extend_existing': True} 
    answer_id = db.Column(db.Integer, primary_key=True)
    parent_question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    answer = db.Column(db.String(140), nullable=False)


class Response(db.Model):
    """Represents a panelist's response to a question of a survey.

    Usage:
    Survey.responses: Get all the responses to a particular survey.
    Panelist.responses: Get all the responses from a particular panelist.
    """

    __tablename__ = 'responses'
    __table_args__ = {'extend_existing': True} 
    response_id = db.Column(db.Integer, primary_key=True)
    parent_survey_id = db.Column(db.Integer, db.ForeignKey('surveys.survey_id'), nullable=False)
    parent_question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    response_panelist_id = db.Column(db.Integer, db.ForeignKey('panelists.panelist_id'), nullable=False)
    response = db.Column(db.String(140), nullable=False)


class Challenge(db.Model):
    """Represents a task as a challenge to be completed"""

    __tablename__='challenges'
    __table_args__ = {'extend_existing': True}
    task_id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(140), nullable=False)
    award = db.Column(db.Integer, default=0)
    status = db.Column(db.String(64), default='incomplete') #incomplete, complete, claimed


class Redemption(db.Model):
    # Represents a redemption entry where points are redeemed for a prize

    __tablename__ ='redemptions'
    __table_args__ = {'extend_existing': True}
    redemption_id = db.Column(db.Integer, primary_key=True)
    redemption = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    redemption_panelist_id = db.Column(db.Integer, db.ForeignKey('panelists.panelist_id'), nullable=False)
    redemption_date = db.Column(db.DateTime, server_default=func.now())
