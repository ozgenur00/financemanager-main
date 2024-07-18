from flask import Blueprint, render_template, redirect, url_for, session, flash
from forms import GoalCreationForm
from app.models import db
from app.models.goal import Goals

goal_bp = Blueprint('goal', __name__)

@goal_bp.route('/set', methods=["GET", "POST"])
def set_goal():
    if 'user_id' not in session:
        flash("You must be logged in to set a budget.", "warning")
        return redirect(url_for('auth.login'))
    
    form = GoalCreationForm()
    if form.validate_on_submit():
        new_goal = Goals(
            name=form.name.data,
            target_amount=form.target_amount.data,
            user_id=session['user_id']
        )
        db.session.add(new_goal)

        try:
            db.session.commit()
            flash("Goal added.", "success")
            return redirect(url_for('goal.goals'))
        except Exception as e:
            db.session.rollback()
            flash("Error setting goal.", "danger")
    return render_template('forms-templates/set-goal.html', form=form)

@goal_bp.route('/')
def goals():
    if 'user_id' not in session:
        flash("You must be logged in to view accounts.", "warning")
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    user_goals = Goals.query.filter_by(user_id=user_id).all()

    return render_template('mainpages/goals.html', goals=user_goals)

@goal_bp.route('/edit/<int:goal_id>', methods=["GET", "POST"])
def edit_goal(goal_id):
    if 'user_id' not in session:
        flash("You must be logged in to perform this action.", "warning")
        return redirect(url_for('login'))
    
    goal_to_edit = Goals.query.get_or_404(goal_id)
    if goal_to_edit.user_id != session['user_id']:
        flash("You do not have permission to edit this goal.", "danger")
        return redirect(url_for('goal.goals'))
    
    form = GoalCreationForm(obj=goal_to_edit)

    if form.validate_on_submit():
        goal_to_edit.name = form.name.data
        goal_to_edit.target_amount = form.target_amount.data
        db.session.commit()
        flash("Goal updated successfully.", "success")
        return redirect(url_for('goal.goals'))
    
    return render_template('forms-templates/edit-goal.html', form=form, goal=goal_to_edit)

@goal_bp.route('/delete/<int:goal_id>', methods=["POST"])
def delete_goal(goal_id):
    if 'user_id' not in session:
        flash("You must be logged in to perform this action.", "warning")
        return redirect(url_for('login'))
    
    goal_to_delete = Goals.query.get_or_404(goal_id)
    if goal_to_delete.user_id != session['user_id']:
        flash("You do not have permission to delete this account.", "danger")
        return redirect(url_for('goals'))
    db.session.delete(goal_to_delete)
    db.session.commit()
    flash("Goal deleted successfully.", "success")
    return redirect(url_for('goal.goals'))