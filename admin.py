from flask import Blueprint, render_template
from decorators import *
from models import *


bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/tables', methods=(['GET']))
@login_required
def admin():
    """Endpoint for displaying tables for Panelists, Surveys,
    and the Juntion tables for survey_races, survey_genders,
    and survey_regions.
    """
    panelists = Panelist.query.all()
    surveys = Survey.query.all()
    genders = Gender.query.all()
    races = Race.query.all()
    regions = Region.query.all()
    questions = Question.query.all()
    answers = Answer.query.all()
    responses = Response.query.all()

    return render_template('admin/admintables.html', panelists=panelists, surveys=surveys, genders=genders, races=races, regions=regions, questions=questions, answers=answers, responses=responses)