from wtforms import (
    Form, StringField, BooleanField, validators, PasswordField, SelectField,
    RadioField, IntegerField, TextAreaField, FieldList)
from wtforms.fields.html5 import EmailField, DateField
from flask_wtf import FlaskForm
from wtforms import widgets, SelectMultipleField


class RegistrationForm(Form):
    """Class for the form used to create a username and password.

    Attributes:
        email: Must be of valid email format and between 6 and 35 characters.
        password: Must not be left blank and be between 6 and 35 characters.
        confirm_password: Must not be left blank and be equal to password.

        Error messages are flashed by validators where errors exist
    """
    email = EmailField('Email Address', 
        [
            validators.Email(),
            validators.Length(min=6, max=35)
        ])

    password = PasswordField('Password',
        [
            validators.InputRequired(),
            validators.Length(min=6, max=35)
        ])

    confirm_password = PasswordField('Confirm Password',
        [
            validators.InputRequired(),
            validators.EqualTo('password', message='Passwords must match'),
        ])


class PanelistDetailsForm(Form):
    """Class for the form used to input a Panelist's demographics.

    Attributes:
        firstname: Must not be blank and be between 2 and 35 characters.
        lastname: same as firstname.
        dob: Must not be blank.
        race: Multiple choice Select field, coerces as String.
        gender: Multiple choice Radio field, coerces as String.
        region: same as race.

        Error messages are flashed by validators where errors exist"""

    firstname = StringField('First Name',
    [
        validators.InputRequired(),
        validators.Length(min=2, max=35)
    ])
    
    lastname = StringField('Last Name',
    [
        validators.Length(min=2, max=35)
    ])
    
    dob = DateField('Birthday',
    [
        validators.InputRequired()
    ])

    race = SelectField('Race/Ethnicity', coerce=str, choices=['Black or African American', 'White', 'Asian', 'Hispanic or Latino', 'American Indian or Alaska Native', 'Native Hawaiian or Other Pacific Islander'])
    
    gender = RadioField('Gender', coerce=str, choices=['Male', 'Female', 'Non-binary'])
    
    region = SelectField('Region of Residence', coerce=str, choices=['Northeast', 'Midwest', 'West', 'South'])


class PanelistLoginForm(Form):
    """Class for the form to login"""

    email = EmailField('Email Address', 
        [
            validators.Email(),
            validators.Length(min=6, max=35)
        ])

    password = PasswordField('Password',
        [
            validators.InputRequired(),
            validators.Length(min=6, max=35)
        ])


class MultiCheckboxField(SelectMultipleField):
    """Class to allow a 'Check all that apply' input style.

    This class subclasses the SelectMultipleField and changes the widget
    configuration to display the options as checkboxes."""

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SurveyDetailsForm(FlaskForm):
    """Class for the form to create a survey in the 'Ask' page.

    Attributes:
        title: Must not be blank and be 6-35 characters. Has placeholder.
        category: Select field, coerced as String.
        survey_description: TextArea, between 6-35 characters. Has placeholder.
        sample_size: Must not be blank and be an Integer between 1 and 500.
        min_age: Must not be blank and be an Integer between 18 and 65.
        max_age: Must not be blank and must be an Integer >= min_age.
        race: 'Select all that apply' style input.  Must include at least one.
        gender: Same as race.
        region: Same as race.

        Errors are flashed by validators where errors exist"""

    title = StringField('Title',
    [
        validators.InputRequired(),
        validators.Length(min=6, max=35)
    ],
    render_kw={"placeholder":"Please enter a title"})
    
    category = SelectField('Category', coerce=str, choices=[('General Survey'),('Health and Wellness'), ('Finance'), ('Travel and Lodging'), ('Utilities'), ('Real Estate'), ('Technology'), ('TV and Media'), ('Food and Beverage'), ('Sports and Entertainment'), ('Education')])

    survey_description = TextAreaField('Description',
    [
        validators.InputRequired(),
        validators.Length(min=6, max=140)
    ],
    render_kw={"placeholder":"Provide a short description of your survey"})

    sample_size = IntegerField('Sample Size',
    [
        validators.InputRequired(),
        validators.NumberRange(min=1, max=500)
    ])

    min_age = IntegerField('Min.',
    [
        validators.InputRequired(),
        validators.NumberRange(min=18, max=65)
    ])

    max_age = IntegerField('Max.',
    [
        validators.InputRequired(),
        validators.NumberRange(min=18, max=65)
    ])

    race = MultiCheckboxField('Race', coerce=int, choices=[(1, 'Black or African American'), (2, 'White'), (3, 'Asian'), (4,'Hispanic or Latino'), (5, 'American Indian or Alaska Native'), (6, 'Native Hawaiian or Other Pacific Islander')])
    gender = MultiCheckboxField('Gender', coerce=int, choices=[(1, 'Male'), (2, 'Female'), (3, 'Non-binary')])
    region = MultiCheckboxField('Region', coerce=int, choices=[(1, 'Northeast'), (2, 'Midwest'), (3, 'West'), (4, 'South')])


class SurveyContentForm(FlaskForm):
    question_text = TextAreaField('Question',
    [
        validators.InputRequired(),
        validators.Length(min=6, max=140)
    ],
    render_kw={"placeholder":"Please type your question here."})

    answers = FieldList(StringField('Answer', render_kw={"placeholder":"Answer option"}), min_entries=4, max_entries=5)


class IncentiveRedemption(FlaskForm):
    amount = RadioField('Amount', coerce=int, choices=[(50, '$5 (50 pts.)'), (100, '$10 (100 pts.)'), (150, '$15 (150 pts.)')])