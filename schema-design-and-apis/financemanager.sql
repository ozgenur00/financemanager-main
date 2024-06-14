CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    name TEXT,
    account_type TEXT,
    balance NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE budgets (
    id SERIAL PRIMARY KEY,
    category_name TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    spent NUMERIC(10,2),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    category_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(10,2) NOT NULL,
    description TEXT,
    date DATE DEFAULT CURRENT_DATE,
    category_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    budget_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (budget_id) REFERENCES budgets(id)
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    type TEXT,
    description TEXT,
    amount NUMERIC(10,2),
    date DATE,
    category_id INTEGER,
    account_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE goals (
    id SERIAL PRIMARY KEY,
    name TEXT,
    target_amount NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
