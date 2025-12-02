SELECT 
    card_id,
    user_id,
    card_brand,
    card_type,
    has_chip,
    credit_limit
FROM {{ ref('stg_cards') }}
