##Schema Design

**Users and Accounts (One-to-Many):**
A single user can own multiple accounts. This is represented by the user_id foreign key in the Accounts table, which references the id in the Users table. This relationship allows the application to track different types of accounts (e.g., savings, checking) for each user.

**Accounts and Transactions (One-to-Many):**
Each account can have multiple transactions associated with it. The account_id foreign key in the Transactions table references the id in the Accounts table. This setup is crucial for tracking all the financial activities within each specific account, whether they are incomes or expenses.

**Users and Budgets (One-to-Many):**
Users can create multiple budgets. The user_id foreign key in the Budgets table references the id in the Users table. Each budget is associated with a specific category, allowing users to allocate and track spending in different areas of their financial life over a set period.

**Users and Goals (One-to-Many):**
Similar to budgets, a user can have multiple financial goals. The user_id foreign key in the Goals table references the id in the Users table. This relationship supports the setting and tracking of financial targets, such as saving for a vacation or paying off debt.

**Budgets and Categories (Many-to-One):**
Each budget is associated with a specific category. This is represented by the category_id foreign key in the Budgets table, which references the id in the Categories table. This allows the application to classify and organize different budget plans under various categories, such as groceries, entertainment, or utilities.

**Expenses and Categories (Many-to-One):**
Each expense is associated with a specific category. The category_id foreign key in the Expenses table references the id in the Categories table. This categorization helps in understanding and analyzing spending patterns across different areas.

**Users and Expenses (One-to-Many):**
A user can have multiple expenses. The user_id foreign key in the Expenses table references the id in the Users table. This relationship allows the application to track all expenses incurred by a user.

**Budgets and Expenses (One-to-Many):**
Each budget can have multiple expenses associated with it. The budget_id foreign key in the Expenses table references the id in the Budgets table. This relationship helps in tracking expenses against the allocated budget.

**Categories and Transactions (One-to-Many):**
Transactions can be categorized under various categories. The category_id foreign key in the Transactions table references the id in the Categories table. This relationship helps in organizing and analyzing transactions based on their categories.

**Users and Transactions (One-to-Many):**
Each user can have multiple transactions. The user_id foreign key in the Transactions table references the id in the Users table. This relationship helps in tracking all transactions made by a user, providing a comprehensive view of their financial activities.

**Goals and Users (Many-to-One):**
Each goal is associated with a specific user. This is represented by the user_id foreign key in the Goals table, which references the id in the Users table. This relationship supports the tracking of various financial goals set by the user.


##***APIs***

**Plotly API:** Used to generate charts and graphs to visualize financial data.

**Flask-SQLAlchemy:** Used for database interactions, making use of SQLAlchemy ORM.

**Alembic:** Used for handling data migrations.
