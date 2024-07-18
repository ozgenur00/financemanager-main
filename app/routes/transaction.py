from flask import Blueprint, render_template, redirect, url_for, session, flash
from forms import TransactionForm
from app.models import db
from app.models.transaction import Transactions
from app.models.account import Accounts
from app.models.category import Category
from app.models.budget import Budgets
from decimal import Decimal

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if 'user_id' not in session:
        flash("You must be logged in to add a transaction.", "warning")
        return redirect(url_for('auth.login'))

    form = TransactionForm()
    form.account_id.choices = [(str(account.id), account.name) for account in Accounts.query.filter_by(user_id=session['user_id']).all()]
    form.category.choices = [(str(category.id), category.name) for category in Category.query.all()]

    if form.validate_on_submit():
        transaction_type = form.type.data
        category_id = int(form.category.data) if transaction_type == 'expense' else None
        account = Accounts.query.get(int(form.account_id.data))

        if not account:
            flash("Account not found.", "danger")
            return render_template('forms-templates/add-transaction.html', form=form)

        transaction_amount = Decimal(form.amount.data)

        if transaction_type == 'income':
            account.balance += transaction_amount
        else:
            account.balance -= transaction_amount

        new_transaction = Transactions(
            type=transaction_type,
            description=form.description.data,
            amount=transaction_amount,
            date=form.date.data,
            account_id=account.id,
            user_id=session['user_id'],
            category_id=category_id
        )
        db.session.add(new_transaction)

        if transaction_type == 'expense':
            active_budget = Budgets.query.filter(
                Budgets.category_id == category_id,
                Budgets.start_date <= new_transaction.date,
                Budgets.end_date >= new_transaction.date,
                Budgets.user_id == session['user_id']
            ).first()

            if active_budget:
                if active_budget.spent is None:
                    active_budget.spent = Decimal('0')
                active_budget.spent += transaction_amount

        db.session.commit()
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('transaction.transactions'))

    return render_template('forms-templates/add-transaction.html', form=form)

@transaction_bp.route('/')
def transactions():
    if 'user_id' not in session:
        flash("You must be logged in to view accounts.", "warning")
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    user_transactions = Transactions.query.filter_by(user_id=user_id).all()

    return render_template('mainpages/transactions.html', transactions=user_transactions)

@transaction_bp.route('/edit/<int:transaction_id>', methods=["GET", "POST"])
def edit_transaction(transaction_id):
    if 'user_id' not in session:
        flash("You must be logged in to perform this action.", "danger")
        return redirect(url_for('auth.login'))
    
    transaction_to_edit = Transactions.query.get_or_404(transaction_id)
    if transaction_to_edit.user_id != session['user_id']:
        flash("You don't have permission to edit this transaction.", "danger")
        return redirect(url_for('transaction.transactions'))
    
    form = TransactionForm(obj=transaction_to_edit)

    form.account_id.choices = [(account.id, account.name) for account in Accounts.query.all()]
    form.category.choices = [(category.id, category.name) for category in Category.query.all()]

    if form.validate_on_submit():
        old_amount = transaction_to_edit.amount
        old_type = transaction_to_edit.type
        old_account = Accounts.query.get(transaction_to_edit.account_id)

        new_amount = Decimal(form.amount.data)
        new_type = form.type.data
        new_account = Accounts.query.get(form.account_id.data)

        if old_type == 'income':
            old_account.balance -+ old_amount
        elif old_type == 'expense':
            old_account.balance += old_amount

        
        if new_type == 'income':
            new_account.balance += new_amount
        elif new_type == 'expense':
            new_account.balance -= new_amount

        transaction_to_edit.account_id = form.account_id.data
        transaction_to_edit.type = new_type
        transaction_to_edit.description = form.description.data
        transaction_to_edit.amount = form.amount.data
        transaction_to_edit.date = form.date.data
        transaction_to_edit.category_id = form.category.data if new_type == 'expense' else None
        db.session.commit()
        flash("Transaction updated successfully.", "success")
        return redirect(url_for('transaction.transactions'))

    return render_template('forms-templates/edit-transaction.html', form=form, transaction=transaction_to_edit)

@transaction_bp.route('/delete/<int:transaction_id>', methods=["POST"])
def delete_transaction(transaction_id):
    if 'user_id' not in session:
        flash("Yu must be logged in to perform this action.", "warning")
        return redirect(url_for('auth.login'))
    
    transaction_to_delete = Transactions.query.get_or_404(transaction_id)
    if transaction_to_delete.user_id != session['user_id']:
        return redirect(url_for('transaction.transactions'))
    
    account = Accounts.query.get(transaction_to_delete.account_id)

    if transaction_to_delete.type == 'income':
        account.balance -= transaction_to_delete.amount
    elif transaction_to_delete.type == 'expense':
        account.balance += transaction_to_delete.amount

    db.session.delete(transaction_to_delete)
    db.session.commit()
    flash("Transaction deleted successfully.", "success")
    return redirect(url_for('transaction.transactions'))
