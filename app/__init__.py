from flask import Flask
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from .models import connect_db, db
from config import DevelopmentConfig, ProductionConfig, TestingConfig

bcrypt = Bcrypt()
migrate = Migrate()

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object(config_class)

    connect_db(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.account import account_bp
    from app.routes.transaction import transaction_bp
    from app.routes.budget import budget_bp
    from app.routes.goal import goal_bp
    from app.routes.test import test_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(account_bp, url_prefix='/account')
    app.register_blueprint(transaction_bp, url_prefix='/transaction')
    app.register_blueprint(budget_bp, url_prefix='/budget')
    app.register_blueprint(goal_bp, url_prefix='/goal')
    app.register_blueprint(test_bp, url_prefix='/test')

    return app

app = create_app()
