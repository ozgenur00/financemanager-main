import logging
from app import create_app
from app.models import db, User, Accounts, Budgets, Transactions, Goals

# Logging yapılandırması
logging.basicConfig(level=logging.DEBUG)

app = create_app()
    

@app.before_request
def setup_logging():
    logging.debug("User model: %s", User)
    logging.debug("Accounts model: %s", Accounts)
    logging.debug("Budgets model: %s", Budgets)
    logging.debug("Transactions model: %s", Transactions)
    logging.debug("Goals model: %s", Goals)

if __name__ == "__main__":
    app.run(debug=True)
