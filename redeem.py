from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from flask_login import current_user
from decorators import *
from forms import IncentiveRedemption
from models import *


bp = Blueprint('redeem', __name__, url_prefix='/redeem')


@bp.route('/', methods=['GET', 'POST'])
@login_required
def redeem():
    
    return render_template('redeem/redeem.html')


@bp.route('/amazon/', methods=['GET', 'POST'])
@login_required
def amazon():
    form = IncentiveRedemption(request.form)

    if request.method == 'POST':
        redemption_amount = form.amount.data
        
        if redemption_amount <= current_user.point_balance:
            db.session.add(
                Redemption(
                    redemption='Amazon',
                    amount=redemption_amount,
                    redemption_panelist_id=current_user.panelist_id
                    )
                )
            current_user.point_balance -= redemption_amount
            db.session.merge(current_user)
            db.session.commit()
        else:
            pass
        return redirect(url_for('redeem.amazon'))


    return render_template('redeem/amazon.html', form=form)


@bp.route('/paypal/', methods=['GET', 'POST'])
@login_required
def paypal():
    form = IncentiveRedemption(request.form)

    if request.method == 'POST':
        redemption_amount = form.amount.data
        
        if redemption_amount <= current_user.point_balance:
            db.session.add(
                Redemption(
                    redemption='PayPal',
                    amount=redemption_amount,
                    redemption_panelist_id=current_user.panelist_id
                    )
                )
            current_user.point_balance -= redemption_amount
            db.session.merge(current_user)
            db.session.commit()
        else:
            pass

    return render_template('redeem/paypal.html', form=form)


@bp.route('/venmo/', methods=['GET', 'POST'])
@login_required
def venmo():
    form = IncentiveRedemption(request.form)

    if request.method == 'POST':
        redemption_amount = form.amount.data
        
        if redemption_amount <= current_user.point_balance:
            db.session.add(
                Redemption(
                    redemption='Venmo',
                    amount=redemption_amount,
                    redemption_panelist_id=current_user.panelist_id
                    )
                )
            current_user.point_balance -= redemption_amount
            db.session.merge(current_user)
            db.session.commit()
        else:
            pass

    return render_template('redeem/venmo.html', form=form)