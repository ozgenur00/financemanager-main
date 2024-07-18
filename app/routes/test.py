from flask import Blueprint, jsonify
from app.models import db, User, Accounts, Budgets, Transactions, Goals

test_bp = Blueprint('test', __name__)

@test_bp.route('/test_models')
def test_models():
    user_count = User.query.count()
    account_count = Accounts.query.count()
    budget_count = Budgets.query.count()
    transaction_count = Transactions.query.count()
    goal_count = Goals.query.count()

    return jsonify({
        "user_count": user_count,
        "account_count": account_count,
        "budget_count": budget_count,
        "transaction_count": transaction_count,
        "goal_count": goal_count
    })
