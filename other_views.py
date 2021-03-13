import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, send_file
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user, login_user
from app.decorators import *
from app.models import *
from app.__init__ import db
import xlsxwriter
from io import BytesIO


bp = Blueprint('other_views', __name__)


@bp.route('/home/', methods=(['GET', 'POST']))
@login_required
def home():
    home_surveys = current_user.get_eligible_surveys()
    challenges = Challenge.query.limit(2)
    num_completed = Response.query.filter_by(response_panelist_id=current_user.panelist_id).distinct(Response.parent_survey_id).group_by(Response.parent_survey_id).count() # count the number of unique survey_ids in that panelists responses table.
    num_published = Survey.query.filter_by(publisher_id=current_user.panelist_id).count()
    featured_surveys = Survey.query.filter_by(status='Completed').limit(3)
    my_surveys = Survey.query.filter_by(publisher_id=current_user.panelist_id).all()

    return render_template('views/home.html', home_surveys = home_surveys, num_completed=num_completed, num_published=num_published, challenges=challenges, featured_surveys=featured_surveys)


@bp.route('/challenge/<int:challenge_id>', methods=(['GET', 'POST']))
@login_required
def challenge_redemption(challenge_id):
    redeemed = getattr(current_user,'redeemed_challenge_' + str(challenge_id))

    if redeemed:
        pass
    else:
        setattr(current_user,'redeemed_challenge_' + str(challenge_id), True)
        current_user.point_balance += Challenge.query.get(challenge_id).award
        db.session.merge(current_user)
        db.session.commit()
        return redirect(url_for('other_views.home'))


@bp.route('/export/<int:survey_id>', methods=(['GET', 'POST']))
@login_required
def export_to_excel(survey_id):
    current_survey = Survey.query.get(survey_id)
    """Display the data in such a way to lend itself to being able to pivot to see the breakdown of responses by question.
    Plan out using Excel on pc and see what works.  Also if XlsxWriter is easy enough, maybe make it generate the pivot table
    by default."""
    current_survey = Survey.query.get(survey_id)

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)

    worksheet = workbook.add_worksheet()
    col_names = ['Question', 'Response', 'Age', 'Gender', 'Race', 'Region']
    col_counter = 0
    for name in col_names:
        worksheet.write(0, col_counter, name)
        col_counter += 1

    row_counter = 1
    for row in current_survey.responses:
        worksheet.write(row_counter, 0, row.parent_question.question)
        worksheet.write(row_counter, 1, row.response)
        worksheet.write(row_counter, 2, row.response_panelist.get_age())
        worksheet.write(row_counter, 3, row.response_panelist.gender)
        worksheet.write(row_counter, 4, row.response_panelist.race)
        worksheet.write(row_counter, 5, row.response_panelist.region)
        row_counter += 1

    workbook.close()
    output.seek(0)

    return send_file(filename_or_fp=output, attachment_filename=str(current_survey.title) + '.xlsx', as_attachment=True)


@bp.route('/results/<int:survey_id>', methods=(['GET', 'POST']))
@login_required
def see_results(survey_id):
    """See the relevent Response object for that survey"""

    current_survey = Survey.query.get(survey_id)

    return render_template('views/results.html', current_survey=current_survey)


@bp.route('/', methods=(['GET', 'POST']))
def index():
    session['email'] = None
    if request.method == 'POST':
        session['email'] = request.form['email']
        return redirect(url_for('auth.register'))
    
    return render_template('views/index.html')


@bp.route('/profile/', methods=(['GET', 'POST']))
@login_required
def profile():
    #surveys_ive_responded_to = Response.query.filter_by(response_panelist_id=current_user.panelist_id).distinct(Response.parent_survey_id).group_by(Response.parent_survey_id).all() # count the number of unique survey_ids in that panelists responses table.
    surveys_ive_responded_to = Survey.query.filter(Survey.responses.any(Response.response_panelist_id == current_user.panelist_id))
    my_redemptions = Redemption.query.filter_by(redemption_panelist_id=current_user.panelist_id)
    
    return render_template('views/profile.html', surveys_ive_responded_to=surveys_ive_responded_to, my_redemptions=my_redemptions)