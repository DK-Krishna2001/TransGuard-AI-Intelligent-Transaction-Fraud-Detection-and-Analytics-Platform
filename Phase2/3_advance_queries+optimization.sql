--Query 1 – High-risk users by transaction behavior(CTE + window functions + joins)
--- Q1: Top high-risk users based on transaction patterns and card risk signals
WITH txn_features AS (
    SELECT
        t.user_id,
        COUNT(*) AS txn_count,
        SUM(t.amount) AS total_spent,
        AVG(t.amount) AS avg_txn_amount,
        SUM(CASE WHEN t.errors IS NOT NULL AND t.errors <> '' THEN 1 ELSE 0 END) AS error_txn_count
    FROM transactions t
    GROUP BY t.user_id
),
card_features AS (
    SELECT
        c.user_id,
        SUM(CASE WHEN c.card_on_dark_web = TRUE THEN 1 ELSE 0 END) AS dark_web_cards,
        COUNT(*) AS card_count
    FROM cards c
    GROUP BY c.user_id
),
user_risk AS (
    SELECT
        u.user_id,
        u.current_age,
        u.yearly_income,
        u.total_debt,
        tf.txn_count,
        tf.total_spent,
        tf.avg_txn_amount,
        tf.error_txn_count,
        cf.card_count,
        cf.dark_web_cards,
        -- simple composite risk score (you can tweak this logic)
        (
            COALESCE(tf.error_txn_count, 0) * 2
            + COALESCE(cf.dark_web_cards, 0) * 3
            + COALESCE(tf.total_spent, 0) / NULLIF(u.yearly_income, 0)
        ) AS risk_score
    FROM users u
    LEFT JOIN txn_features tf ON u.user_id = tf.user_id
    LEFT JOIN card_features cf ON u.user_id = cf.user_id
)
SELECT *
FROM (
    SELECT
        user_id,
        current_age,
        yearly_income,
        total_debt,
        txn_count,
        total_spent,
        avg_txn_amount,
        error_txn_count,
        card_count,
        dark_web_cards,
        risk_score,
        RANK() OVER (ORDER BY risk_score DESC NULLS LAST) AS risk_rank
    FROM user_risk
) ranked
WHERE risk_rank <= 20
ORDER BY risk_rank;

--Query 2 – Risky merchants by error rate & chip usage(window function + subquery)
--- Q2: High-risk merchants by error rate and chip usage
WITH merchant_stats AS (
    SELECT
        t.merchant_id,
        t.merchant_city,
        t.merchant_state,
        COUNT(*) AS txn_count,
        SUM(t.amount) AS total_spent,
        AVG(t.amount) AS avg_amount,
        SUM(CASE WHEN t.errors IS NOT NULL AND t.errors <> '' THEN 1 ELSE 0 END) AS error_txn_count,
        SUM(CASE WHEN t.use_chip = FALSE THEN 1 ELSE 0 END) AS no_chip_txn_count
    FROM transactions t
    GROUP BY t.merchant_id, t.merchant_city, t.merchant_state
),
merchant_risk AS (
    SELECT
        merchant_id,
        merchant_city,
        merchant_state,
        txn_count,
        total_spent,
        avg_amount,
        error_txn_count,
        no_chip_txn_count,
        (error_txn_count::decimal / NULLIF(txn_count, 0)) AS error_rate,
        (no_chip_txn_count::decimal / NULLIF(txn_count, 0)) AS no_chip_rate
    FROM merchant_stats
)
SELECT
    merchant_id,
    merchant_city,
    merchant_state,
    txn_count,
    total_spent,
    avg_amount,
    error_txn_count,
    error_rate,
    no_chip_rate,
    RANK() OVER (ORDER BY error_rate DESC, no_chip_rate DESC) AS merchant_risk_rank
FROM merchant_risk
WHERE txn_count >= 50   -- only merchants with enough data
ORDER BY merchant_risk_rank
LIMIT 20;

--Query 3 – Card utilization vs income(joins + window + analytics)
--- Q3: Card utilization vs user income (potential over-leverage)
WITH card_txn AS (
    SELECT
        t.card_id,
        SUM(t.amount) AS total_card_spend,
        COUNT(*) AS card_txn_count
    FROM transactions t
    GROUP BY t.card_id
),
card_util AS (
    SELECT
        c.card_id,
        c.user_id,
        c.credit_limit,
        ct.total_card_spend,
        ct.card_txn_count,
        (ct.total_card_spend / NULLIF(c.credit_limit, 0)) AS utilization_ratio
    FROM cards c
    LEFT JOIN card_txn ct ON c.card_id = ct.card_id
),
card_with_user AS (
    SELECT
        u.user_id,
        u.yearly_income,
        u.total_debt,
        cu.card_id,
        cu.credit_limit,
        cu.total_card_spend,
        cu.card_txn_count,
        cu.utilization_ratio
    FROM users u
    JOIN card_util cu ON u.user_id = cu.user_id
)
SELECT
    *,
    NTILE(4) OVER (ORDER BY utilization_ratio DESC NULLS LAST) AS utilization_quartile
FROM card_with_user
WHERE utilization_ratio IS NOT NULL
ORDER BY utilization_ratio DESC
LIMIT 50;

--- Performance Tuning Indexes for TransGuard AI
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_card_id ON transactions(card_id);
CREATE INDEX idx_cards_user_id ON cards(user_id);
CREATE INDEX idx_users_lat_lon ON users(latitude, longitude);
CREATE INDEX idx_transactions_amount ON transactions(amount);