from flask import Blueprint, flash, render_template
from flask_login import current_user
from decorators import *
from models import *
from wtforms import Form, validators, RadioField, FieldList
from flask_wtf import FlaskForm


bp = Blueprint('answer', __name__, url_prefix='/answer')


@bp.route('/<string:sort_parameter>/', methods=(['GET', 'POST']))
@login_required
def browse(sort_parameter):
    """Endpoint for displaying surveys to browse and click on to begin taking.

    sort_parameter determines which query to use in displaying Surveys in the HTML page.
    """

    if sort_parameter == 'recommended':
        surveys = current_user.get_eligible_surveys()
    elif sort_parameter == 'shortest':
        surveys = Survey.query.order_by(Survey.num_questions)
    elif sort_parameter == 'longest':
        surveys = Survey.query.order_by(Survey.num_questions.desc())
    elif sort_parameter == 'newest':
        surveys = Survey.query.order_by(Survey.create_date.desc())
    elif sort_parameter == 'oldest':
        surveys = Survey.query.order_by(Survey.create_date)

            
    return render_template('answer/browse.html', surveys=surveys)


@bp.route('/<int:survey_id>', methods=(['GET', 'POST']))
@login_required
def answer(survey_id):
    """Endpoint for answering a survey with a given survey_id.

    GET request:
        1. Query to get the Survey object with given survey_id.
        2. Define class for a form to be created dynamically within this view.
           The contents are dependent entirely on the questions in the 
           current survey and the answers to those questions.
        3. For each question in the survey, create a RadioField with the
           question text as the label and the answers to that question as the
           choices, and assign as an attribute of the object. This is not the
           best in terms of quality code but it works.
        4. Return the template with the instantiated form object.

    POST request:
        1. Query to get the ID of the first question in the survey. To generate
           rows in Response table for each question's response, we also need
           the ID that corresponds to it.  Once we have the first one, we can 
           increment by one since all questions are in numerical order.
        2. Iterate over the attributes of the form to get the data for each
           RadioField ie each response.  Create a new Response row with the
           survey_id, the question_id, the panelist_id, and the response.
           Increment the variable for the question_id so that the next added
           response has the correct question_id.
        3. Increment the panelist's point balance, and the survey's complete
           count.
        4. Return a redirect or some sort of screen saying thanks you earned
           points...
    """

    current_survey = Survey.query.get(survey_id)

    # Define this form class in the view function per WTForms doc. The
    # form fields have to be created dynamically or else they will not be 
    # bound correctly to the form object.
    class SurveyAnsweringForm(FlaskForm):
        pass

    # This loops through all the questions in the survey and creates an 
    # attribute for each one and sets the value to a RadioField with a label
    # representing the question text, and choices for each answer in that 
    # question.  A list of all the attributes is kept in memory so that I can
    # loop through all the RadioFields later on a POST request.
    list_of_attributes = []
    for question in current_survey.questions:
        setattr(
            SurveyAnsweringForm,
            'q' + str(question.question_id),
            RadioField(str(question.question), choices=[answer.answer for answer in question.answers])
            )
        list_of_attributes.append('q' + str(question.question_id))
    
    form = SurveyAnsweringForm(request.form)
    

    if request.method == 'POST':
        # TODO: Check to see if the current user has already answered this 
        # survey.
        
        # Use this to get the ID of the first question in the survey so that on
        # each loop through the attributes, we can increment and have the 
        # parent_question_id that each Response entry needs.
        current_question_id = Question.query.filter_by(parent_survey_id=current_survey.survey_id).first().question_id
        
        # iterate through all the attributes of the form
        for element in list_of_attributes:
            # Add a response using the form label and data for each attribute.
            db.session.add(
                Response(
                    parent_survey_id=current_survey.survey_id,
                    parent_question_id=current_question_id,
                    response_panelist_id=current_user.panelist_id,
                    response=form[element].data
                    )
            )
            current_question_id += 1
        # Commit all of the responses in db session.
        db.session.commit()

        # Add the survey's point value to the panelist's balance
        current_user.point_balance += current_survey.point_value
        db.session.merge(current_user)
        db.session.commit()
        
        # Increment the number of responses to that survey by 1 and
        # if that number is equal to the sample size, set the status to
        # 'Completed'.
        current_survey.completes += 1
        if current_survey.completes >= current_survey.sample_size:
            current_survey.status = 'Completed'
        db.session.merge(current_survey)
        db.session.commit()
        
        # Redirect to home page.
        return redirect(url_for('other_views.home'))


    return render_template('answer/answer.html', current_survey=current_survey, form=form, list_of_attributes=list_of_attributes)