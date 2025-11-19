-- TransGuard AI - Phase 1 Schema

CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    current_age INT,
    retirement_age INT,
    birth_year INT,
    birth_month INT,
    gender VARCHAR(20),
    address TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    per_capita_income DOUBLE PRECISION,
    yearly_income DOUBLE PRECISION,
    total_debt DOUBLE PRECISION,
    credit_score INT,
    num_credit_cards INT
);

CREATE TABLE cards (
    card_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL REFERENCES users(user_id),
    card_brand VARCHAR(50),
    card_type VARCHAR(50),
    card_number VARCHAR(100),
    expires DATE,
    cvv VARCHAR(10),
    has_chip BOOLEAN,
    num_cards_issued INT,
    credit_limit DOUBLE PRECISION,
    acct_open_date DATE,
    year_pin_last_changed INT,
    card_on_dark_web BOOLEAN
);

CREATE TABLE transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL REFERENCES users(user_id),
    card_id VARCHAR(50) NOT NULL REFERENCES cards(card_id),
    date TIMESTAMP,
    amount DOUBLE PRECISION,
    use_chip BOOLEAN,
    merchant_id VARCHAR(50),
    merchant_city VARCHAR(100),
    merchant_state VARCHAR(100),
    zip VARCHAR(20),
    mcc VARCHAR(20),
    errors TEXT
);

-- Helpful indexes for Phase 2
CREATE INDEX idx_tx_user ON transactions(user_id);
CREATE INDEX idx_tx_card ON transactions(card_id);
CREATE INDEX idx_tx_date ON transactions(date);
CREATE INDEX idx_tx_fraud_chip ON transactions(use_chip);
