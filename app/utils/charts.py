import plotly.graph_objs as go
from plotly.offline import plot
from app.models import db
from app.models.budget import Budgets
from app.models.account import Accounts
from app.models.transaction import Transactions
from collections import defaultdict
from sqlalchemy import func, extract

def create_budget_vs_spent_chart(user_id):
    user_budgets = Budgets.query.filter_by(user_id=user_id).all()
    categories = [budget.category.name for budget in user_budgets]
    budgeted_amounts = [budget.amount for budget in user_budgets]
    spent_amounts = [budget.spent if budget.spent else 0 for budget in user_budgets]
    remaining_budget = [max(0, b - s) for b, s in zip(budgeted_amounts, spent_amounts)]

    fig = go.Figure(data=[
        go.Pie(
            labels=categories, 
            values=remaining_budget, 
            hole=0.3,
            sort=False
        )
    ])
    fig.update_layout(
        title_text='Remaining Budget by Category',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    budget_chart_div = plot(fig, output_type='div', include_plotlyjs=False)
    return budget_chart_div

def create_account_balance_chart(user_id):
    user_accounts = Accounts.query.filter_by(user_id=user_id).all()
    plot_data = []
    if not user_accounts:
        return None

    for account in user_accounts:
        transactions = Transactions.query.filter_by(account_id=account.id).order_by(Transactions.date).all()
        if not transactions:
            continue

        dates = [transaction.date for transaction in transactions]
        balances = [0]
        balance = 0

        for transaction in transactions:
            balance += transaction.amount
            balances.append(balance)

        plot_data.append(go.Scatter(x=dates, y=balances, mode='lines+markers', name=account.name))

    if not plot_data:
        return None

    fig = go.Figure(data=plot_data)
    fig.update_layout(
        title='Account Balance Over Time',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Balance'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    balance_chart_div = plot(fig, output_type='div', include_plotlyjs=False)
    return balance_chart_div

def generate_accounts_balance_chart(user_id):
    account_types_balances = db.session.query(
        Accounts.account_type,
        func.sum(Accounts.balance).label('total_balance')
    ).filter(Accounts.user_id == user_id).group_by(Accounts.account_type).all()
    account_types = [result.account_type for result in account_types_balances]
    balances = [float(result.total_balance) for result in account_types_balances]

    fig = go.Figure(data=[go.Pie(labels=account_types, values=balances, hole=0.3,
                                 textinfo='label+value',
                                 texttemplate='%{label}: $%{value:,}',
                                 insidetextorientation='radial'
                                 )])
    fig.update_layout(title='Accounts Balance Overview', paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div

def generate_financials_chart(user_id):
    monthly_financials = db.session.query(
        extract('month', Transactions.date).label('month'),
        extract('year', Transactions.date).label('year'),
        Transactions.type,
        func.sum(Transactions.amount).label('total_amount')
    ).filter(Transactions.user_id == user_id).group_by('month', 'year', Transactions.type).all()

    income_by_month = defaultdict(float)
    expenses_by_month = defaultdict(float)

    for financial in monthly_financials:
        month = int(financial.month)
        year = int(financial.year)
        month_year_key = f"{year}-{month:02d}"
        if financial.type == 'income':
            income_by_month[month_year_key] += float(financial.total_amount)
        elif financial.type == 'expense':
            expenses_by_month[month_year_key] += abs(float(financial.total_amount))

    all_months = sorted(set(income_by_month.keys()) | set(expenses_by_month.keys()))
    income_amounts = [income_by_month[month] for month in all_months]
    spending_amounts = [expenses_by_month[month] for month in all_months]

    fig = go.Figure(data=[
        go.Bar(name='Income', x=all_months, y=income_amounts),
        go.Bar(name='Spending', x=all_months, y=spending_amounts)
    ])
    fig.update_layout(barmode='group', title='Monthly Spending and Income', paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div
