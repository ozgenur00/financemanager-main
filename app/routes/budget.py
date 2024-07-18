from flask import Blueprint, render_template, redirect, url_for, session, flash
from forms import BudgetCreationForm
from app.models import db
from app.models.budget import Budgets
from app.models.category import Category
from app.utils.charts import create_budget_vs_spent_chart

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/set', methods=["GET", "POST"])
def set_budget():
    if 'user_id' not in session:
        flash("You must be logged in to set a budget.", "warning")
        return redirect(url_for('auth.login'))
    
    form = BudgetCreationForm()
    form.category.choices = [(str(c.id), c.name) for c in Category.query.order_by('name').all()]

    if form.validate_on_submit():
        category_id = int(form.category.data)
        category = Category.query.get(category_id)

        if category is None:
            flash(f"Category with ID '{category_id}' does not exist.", "danger")
            return redirect(url_for('budget.set_budget'))

        new_budget = Budgets(
            category_name=category.name,
            amount=form.amount.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            user_id=session['user_id'],
            category_id=category_id 
        )

        db.session.add(new_budget)
        try:
            db.session.commit()
            flash("Budget added.", "success")
            return redirect(url_for('budget.budgets'))
        except Exception as e:
            db.session.rollback()
            flash("Error setting budget.", "danger")
    return render_template('forms-templates/set-budget.html', form=form)

@budget_bp.route('/')
def budgets():
    if 'user_id' not in session:
        flash("You must be logged in to view accounts.", "warning")
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    budgets = Budgets.query.filter_by(user_id=user_id).all()

    budget_chart_div = create_budget_vs_spent_chart(session['user_id'])
    return render_template('mainpages/budgets.html', budget_chart_div=budget_chart_div, budgets=budgets)

@budget_bp.route('/delete/<int:budget_id>', methods=["POST"])
def delete_budget(budget_id):
    if 'user_id' not in session:
        flash("You must be logged in to perform this action.", "warning")
        return redirect(url_for('login'))
    
    budget_to_delete = Budgets.query.get_or_404(budget_id)
    if budget_to_delete.user_id != session['user_id']:
        return redirect(url_for('budgets'))
    db.session.delete(budget_to_delete)
    db.session.commit()
    flash("budget deleted successfully.", "success")
    return redirect(url_for('budget.budgets'))



@budget_bp.route('/edit/<int:budget_id>', methods=["GET", "POST"])
def edit_budget(budget_id):
    if 'user_id' not in session:
        flash("You must be logged in to perform this action", "danger")
        return redirect(url_for('login'))
    
    budget_to_edit = Budgets.query.get_or_404(budget_id)
    if budget_to_edit.user_id != session['user_id']:
        flash("You don't have permission to edit this budget.", "danger")
        return redirect(url_for('budget.budgets'))
    
    form = BudgetCreationForm(obj=budget_to_edit)

    form.category.choices = [(category.id, category.name) for category in Category.query.all()]

    if form.validate_on_submit():
        budget_to_edit.category_id = form.category.data
        budget_to_edit.amount = form.amount.data
        budget_to_edit.start_date = form.start_date.data
        budget_to_edit.end_date = form.end_date.data
        db.session.commit()
        return redirect(url_for('budget.budgets'))
    
    return render_template('forms-templates/edit-budget.html', form=form, budget=budget_to_edit)