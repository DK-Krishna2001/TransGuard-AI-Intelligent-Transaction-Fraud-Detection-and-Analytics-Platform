SELECT
    t.transaction_id,
    t.user_id,
    t.card_id,
    t.date::date AS date_key,
    t.amount,
    t.use_chip,
    t.errors,
    t.merchant_id,
    t.mcc,
    t.merchant_city,
    t.merchant_state
FROM {{ ref('stg_transactions') }} t
