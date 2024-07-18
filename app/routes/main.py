from flask import Blueprint, render_template, g, session, send_from_directory, current_app
from app.models.account import Accounts
from app.models.transaction import Transactions
from app.models.budget import Budgets
from app.models.goal import Goals
from app.utils.charts import generate_accounts_balance_chart, generate_financials_chart

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('homepage.html')


@main_bp.route('/main-page')
def after_login():
    if g.user:
        accounts_plot_div = generate_accounts_balance_chart(g.user.id)
        financials_plot_div = generate_financials_chart(g.user.id)

        accounts = Accounts.query.filter_by(user_id=g.user.id).all()
        transactions = Transactions.query.filter_by(user_id=g.user.id).order_by(Transactions.date.desc()).all()
        budgets = Budgets.query.filter_by(user_id=g.user.id).all()
        goals = Goals.query.filter_by(user_id=g.user.id).all()

        return render_template('main-page.html', accounts=accounts, transactions=transactions,
                               budgets=budgets, goals=goals, accounts_plot_div=accounts_plot_div,
                               financials_plot_div=financials_plot_div)
    else:
        return render_template('main-page.html', message="Please log in to view this page.")
