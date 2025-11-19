# TransGuard AI – ERD (Phase 1)

```mermaid
erDiagram

    USERS {
        VARCHAR user_id PK
        INT current_age
        INT retirement_age
        INT birth_year
        INT birth_month
        VARCHAR gender
        TEXT address
        FLOAT latitude
        FLOAT longitude
        FLOAT per_capita_income
        FLOAT yearly_income
        FLOAT total_debt
        INT credit_score
        INT num_credit_cards
    }

    CARDS {
        VARCHAR card_id PK
        VARCHAR user_id FK
        VARCHAR card_brand
        VARCHAR card_type
        VARCHAR card_number
        DATE expires
        VARCHAR cvv
        BOOLEAN has_chip
        INT num_cards_issued
        FLOAT credit_limit
        DATE acct_open_date
        INT year_pin_last_changed
        BOOLEAN card_on_dark_web
    }

    TRANSACTIONS {
        VARCHAR transaction_id PK
        VARCHAR user_id FK
        VARCHAR card_id FK
        TIMESTAMP date
        FLOAT amount
        BOOLEAN use_chip
        VARCHAR merchant_id
        VARCHAR merchant_city
        VARCHAR merchant_state
        VARCHAR zip
        VARCHAR mcc
        TEXT errors
    }

    USERS ||--o{ CARDS : "owns"
    USERS ||--o{ TRANSACTIONS : "initiates"
    CARDS ||--o{ TRANSACTIONS : "used_in"
