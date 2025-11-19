
---

## 📄 7. `phase1/3nf_justification.md`

```markdown
# TransGuard AI – 3NF Justification (Phase 1)

## 1. Overview

The Kaggle dataset provides three main CSV files:

- `users_data.csv`: demographic and financial attributes per user
- `cards_data.csv`: card-level attributes linked to users
- `transactions_data.csv`: transactional records referencing users and cards

If we kept everything in a single table, the same user and card information would
repeat for every transaction, causing classic update, insert, and delete anomalies.
To avoid that, we decomposed the data into three core relations:

- `users(user_id, current_age, retirement_age, birth_year, birth_month, gender,
         address, latitude, longitude, per_capita_income, yearly_income,
         total_debt, credit_score, num_credit_cards)`

- `cards(card_id, user_id, card_brand, card_type, card_number, expires, cvv,
         has_chip, num_cards_issued, credit_limit, acct_open_date,
         year_pin_last_changed, card_on_dark_web)`

- `transactions(transaction_id, user_id, card_id, date, amount, use_chip,
                merchant_id, merchant_city, merchant_state, zip, mcc, errors)`

## 2. Functional Dependencies

From the problem domain we assume:

- `user_id → current_age, retirement_age, birth_year, birth_month, gender,
  address, latitude, longitude, per_capita_income, yearly_income, total_debt,
  credit_score, num_credit_cards`

- `card_id → user_id, card_brand, card_type, card_number, expires, cvv,
  has_chip, num_cards_issued, credit_limit, acct_open_date,
  year_pin_last_changed, card_on_dark_web`

- `transaction_id → user_id, card_id, date, amount, use_chip, merchant_id,
  merchant_city, merchant_state, zip, mcc, errors`

These reflect that:

- Each user has a unique `user_id`.
- Each card has a unique `card_id` and is issued to a single user.
- Each transaction has a unique `transaction_id` and refers to one user and one card.

## 3. Normalization to 3NF

A relation is in Third Normal Form (3NF) if for every functional dependency
`X → A`, either `X` is a superkey or `A` is a prime attribute.

### 3.1 USERS

- Key: `user_id`
- All other attributes describe that specific user.
- There are no non-key attributes determining other non-key attributes.
- No partial or transitive dependencies exist.

Therefore, `users` is in 3NF.

### 3.2 CARDS

- Key: `card_id`
- All other attributes (including `user_id`) depend directly on `card_id`.
- `user_id` is a foreign key to `users` and does not determine other card fields
  inside this table.
- There are no non-key attributes determining other non-key attributes.

Therefore, `cards` is in 3NF.

### 3.3 TRANSACTIONS

- Key: `transaction_id`
- All attributes (`user_id`, `card_id`, `date`, `amount`, `use_chip`, merchant
  fields, `mcc`, `errors`) describe a single atomic transaction event.
- `user_id` and `card_id` are foreign keys to the master tables; we do not store
  user or card descriptive attributes here, so there is no transitive dependency
  like `transaction_id → user_id → user_demographics` inside this relation.

Therefore, `transactions` is in 3NF.

## 4. Avoidance of Anomalies

With this design:

- Updating a user's address or credit score only touches the `users` table.
- Updating card details (like credit limit or chip status) only touches the
  `cards` table.
- Transactions can be inserted and deleted independently without losing
  master data about users or cards.

This decomposition removes update, insert, and delete anomalies and satisfies
the 3NF requirement specified in the project instructions.
