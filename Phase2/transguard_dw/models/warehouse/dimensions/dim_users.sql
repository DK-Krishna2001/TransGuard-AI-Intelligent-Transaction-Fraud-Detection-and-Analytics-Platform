SELECT 
    user_id,
    current_age,
    gender,
    yearly_income,
    credit_score,
    num_credit_cards
FROM {{ ref('stg_users') }}
