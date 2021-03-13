from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from flask_login import current_user
from decorators import *
from forms import MultiCheckboxField, SurveyDetailsForm, SurveyContentForm
#from app.models import *


bp = Blueprint('ask', __name__, url_prefix='/ask')


@bp.route('/', methods=(['GET', 'POST']))
@login_required
def create_index():
    """Endpoint for creating a survey based on its basic information.

    On GET request:
        Display HTML template with SurveyDetailsForm.
    
    On POST request:
        1. Validate form fields and use them to create the new Survey object.
        2. Loop through the race/gender/region ids in their form field. Append
           the corresponding Race/Gender/Region objects to the .races/.genders/
           .regions attributes of the new Survey object.
        3. Add the new Survey object to session and commit.
        4. Redirect to the create_survey template given the new Surveys id.

    FOR THIS TO WORK, RACE/GENDER/REGION tables must be populated according to
    the Google Spreadsheet schema tab.
    """
    
    form = SurveyDetailsForm(request.form)
    if request.method == 'POST' and form.validate():
        # Create a new Survey object to insert into DB using the form data.
        survey_to_add = Survey(
            publisher_id=current_user.panelist_id,
            category=form.category.data,
            title=form.title.data,
            description=form.survey_description.data,
            sample_size=form.sample_size.data,
            min_age=form.min_age.data,
            max_age=form.max_age.data,
            )

        # Because the race, gender, and region form fields allow for multiple
        # selections, we have to loop through them and add the Race/Gender/
        # Region objects to the related attribute of the survey.  Survey and
        # Race/Gender/Region is a many-to-many relationship, so we append the
        # Race/Gender/Region objects that correspond to the provided form data.
        for race_id_provided in form.race.data:
            survey_to_add.races.append(Race.query.filter_by(race_id=race_id_provided).first())

        for gender_id_provided in form.gender.data:
            survey_to_add.genders.append(Gender.query.filter_by(gender_id=gender_id_provided).first())

        for region_id_provided in form.region.data:
            survey_to_add.regions.append(Region.query.filter_by(region_id=region_id_provided).first())
        
        # Add to session and get the survey_id to to redirect to.
        db.session.add(survey_to_add)
        survey_id = survey_to_add.survey_id
        db.session.commit()
        
        return redirect(url_for('ask.create_survey', survey_id=survey_id))

    return render_template('ask/create_index.html', form=form)


@bp.route('/<int:survey_id>', methods=(['GET', 'POST']))
@login_required
def create_survey(survey_id):
    """Endpoint to add questions to a given survey.

    On GET request:
        1. Use the argument survey_id to get that Survey object.
        2. Create the SurveyQuestionForm object and pass both into template.
    
    On POST request:
        1. Validate the form inputs on submit.
        2. Create new Question object with form.question_text.data.
        3. For each answer_text in form.answer_text.data, create a new Answer
           object and append it to Question.answers.
        4. Append the Question object to current_survey.questions.
        5. Add the new Question object and the existing, updated
           current_survey.questions object to session and commit.
        6. Redirect to the same page, but reload with updated Survey object.
        Q. What do I have to add explicitly to the session and what
        gets added automatically via the ORM, ie will the Answers objects all
        get added if I append them to question.answers and then add question?
        Will everything be added if at the end I simply add current_survey.questions?
    """
    # Query for the survey with the given ID and the questions for that survey.
    # Can probably use Survey.questions instead but I will leave this here.
    current_survey = Survey.query.get(survey_id)
    current_questions = Question.query.filter_by(parent_survey_id=survey_id).all()
    
    # Instantiate the form to pass to the template.
    form = SurveyContentForm(request.form)

    if request.method == 'POST' and form.validate():
        # Create new question with the form data.
        new_question = Question(parent_survey_id=current_survey.survey_id, question=form.question_text.data)
        
        db.session.add(new_question)

        # I believe the session has to be flushed so that new_question
        # will then have a primary key/ID, which I reference below.
        db.session.flush()
        
        # answers form field returns a list of all answers.  Iterate through
        # and if it is not blank, create an Answer object with the parent 
        # question and form data, and append that to the answers attribute
        # of the question.
        for answer in form.answers.data:
            if answer != '':
                answer_to_add = Answer(parent_question_id=new_question.question_id, answer=answer)
                new_question.answers.append(answer_to_add)
        
        db.session.flush() # Code does not work without this flush. Look into.
        db.session.commit()

        # Each time a question is added, increment survey's num_question
        # attribute by 1 and point_value by 5.  Every question is 5 points.
        current_survey.num_questions += 1
        current_survey.point_value += 5

        # Push these changes to the survey object to the DB.
        db.session.merge(current_survey)
        db.session.commit()

        # Redirect to the same page so that it can show with the new question.
        return redirect(url_for('ask.create_survey', survey_id=survey_id))

    return render_template('ask/create_survey.html', current_survey=current_survey, current_questions=current_questions, form=form)