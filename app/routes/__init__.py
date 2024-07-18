from flask import Blueprint

# Import blueprints from other modules
from .auth import auth_bp
from .main import main_bp
from .account import account_bp
from .transaction import transaction_bp
from .budget import budget_bp
from .goal import goal_bp

_ = Blueprint

# List of all blueprints for easy import
__all__ = ['auth_bp', 'main_bp', 'account_bp', 'transaction_bp', 'budget_bp', 'goal_bp']
