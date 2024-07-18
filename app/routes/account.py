from flask import Blueprint, render_template, redirect, url_for, session, flash
from forms import AccountCreationForm
from app.models import db
from app.models.account import Accounts
from app.utils.charts import create_account_balance_chart

account_bp = Blueprint('account', __name__)

@account_bp.route('/add', methods=["GET", "POST"])
def add_account():
    if 'user_id' not in session:
        flash("You must be logged in to add an account.", "warning")
        return redirect(url_for('auth.login'))
    
    form = AccountCreationForm()
    if form.validate_on_submit():
        new_account = Accounts(
            name=form.name.data,
            account_type=form.account_type.data,
            balance=form.balance.data,
            user_id=session['user_id']
        )
        db.session.add(new_account)
        try:
            db.session.commit()
            flash("Account added successfully.", "success")
            return redirect(url_for('account.accounts'))
        except Exception as e:
            db.session.rollback()
            flash("Error adding account. Please try again.", "danger")
    return render_template('forms-templates/add-account.html', form=form)

@account_bp.route('/')
def accounts():
    if 'user_id' not in session:
        flash("You must be logged in to view accounts.", "warning")
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    balance_chart_div = create_account_balance_chart(user_id)
    user_accounts = Accounts.query.filter_by(user_id=user_id).all()

    return render_template('mainpages/accounts.html', accounts=user_accounts, balance_chart_div=balance_chart_div)


@account_bp.route('/edit/<int:account_id>', methods=["GET", "POST"])
def edit_account(account_id):
    if 'user_id' not in session:
        flash("You must be logged in to perform this action", "danger")
        return redirect(url_for('auth.login'))
    
    account_to_edit = Accounts.query.get_or_404(account_id)
    if account_to_edit.user_id != session['user_id']:
        flash("You don't have permission to edit this account", "danger")
        return redirect(url_for('account.accounts'))
    
    form = AccountCreationForm(obj=account_to_edit)

    if form.validate_on_submit():
        account_to_edit.name = form.name.data
        account_to_edit.account_type = form.account_type.data
        account_to_edit.balance = form.balance.data
        db.session.commit()
        flash("Account updated successfully.", "success")
        return redirect(url_for('account.accounts'))
    
    return render_template('forms-templates/edit-account.html', form=form, account=account_to_edit)

@account_bp.route('/delete/<int:account_id>', methods=['POST'])
def delete_account(account_id):
    if 'user_id' not in session:
        flash("You must be logged in to perform this action.", "warning")
        return redirect(url_for('auth.login'))
    
    account_to_delete = Accounts.query.get_or_404(account_id)
    if account_to_delete.user_id != session['user_id']:
        flash("You do not have permission to delete this account.", "danger")
        return redirect(url_for('account.accounts'))

    db.session.delete(account_to_delete)
    db.session.commit()
    flash("Account and related transactions deleted successfully.", "success")
    return redirect(url_for('account.accounts'))
