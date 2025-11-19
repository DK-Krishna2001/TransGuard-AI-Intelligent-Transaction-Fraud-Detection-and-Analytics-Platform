"""
TransGuard AI - Phase 1 Data Ingestion (Final Chunked Version)

Loads cleaned users, cards, and transactions data
into PostgreSQL using SQLAlchemy.

Chunking prevents MemoryError for very large CSV files.
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# -------- Utility: currency cleaner --------
def clean_currency(series):
    return (
        series.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .astype(float)
    )


# -------- Database engine --------
def get_engine():
    url = URL.create(
        "postgresql+psycopg2",
        username=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "transguard"),
    )
    return create_engine(url)


# -------- Load Users --------
def load_users(engine, path: str):
    print(f"\nLoading users from: {path}")
    df = pd.read_csv(path)

    rename = {
        "id": "user_id",
        "current_age": "current_age",
        "retirement_age": "retirement_age",
        "birth_year": "birth_year",
        "birth_month": "birth_month",
        "gender": "gender",
        "address": "address",
        "latitude": "latitude",
        "longitude": "longitude",
        "per_capita_income": "per_capita_income",
        "yearly_income": "yearly_income",
        "total_debt": "total_debt",
        "credit_score": "credit_score",
        "num_credit_cards": "num_credit_cards",
    }

    df = df.rename(columns=rename)
    df = df[list(rename.values())]

    df["per_capita_income"] = clean_currency(df["per_capita_income"])
    df["yearly_income"] = clean_currency(df["yearly_income"])
    df["total_debt"] = clean_currency(df["total_debt"])

    df.to_sql("users", engine, if_exists="append", index=False)
    print(f"Inserted {len(df)} users")


# -------- Load Cards --------
def load_cards(engine, path: str):
    print(f"\nLoading cards from: {path}")
    df = pd.read_csv(path)

    rename = {
        "id": "card_id",
        "client_id": "user_id",
        "card_brand": "card_brand",
        "card_type": "card_type",
        "card_number": "card_number",
        "expires": "expires",
        "cvv": "cvv",
        "has_chip": "has_chip",
        "num_cards_issued": "num_cards_issued",
        "credit_limit": "credit_limit",
        "acct_open_date": "acct_open_date",
        "year_pin_last_changed": "year_pin_last_changed",
        "card_on_dark_web": "card_on_dark_web",
    }

    df = df.rename(columns=rename)
    df = df[list(rename.values())]

    df["expires"] = pd.to_datetime(df["expires"], errors="coerce").dt.date
    df["acct_open_date"] = pd.to_datetime(df["acct_open_date"], errors="coerce").dt.date

    df["has_chip"] = df["has_chip"].astype(bool)
    df["card_on_dark_web"] = df["card_on_dark_web"].astype(bool)

    if df["credit_limit"].dtype == object:
        df["credit_limit"] = clean_currency(df["credit_limit"])

    df.to_sql("cards", engine, if_exists="append", index=False)
    print(f"Inserted {len(df)} cards")


# -------- Load Transactions (Chunked) --------
def load_transactions(engine, path: str):
    print(f"\nLoading transactions from: {path}")

    chunksize = 25000
    chunk_iter = pd.read_csv(path, chunksize=chunksize)

    total = 0
    for i, chunk in enumerate(chunk_iter):
        print(f"Inserting chunk {i+1}...")

        rename = {
            "id": "transaction_id",
            "client_id": "user_id",
            "card_id": "card_id",
            "date": "date",
            "amount": "amount",
            "use_chip": "use_chip",
            "merchant_id": "merchant_id",
            "merchant_city": "merchant_city",
            "merchant_state": "merchant_state",
            "zip": "zip",
            "mcc": "mcc",
            "errors": "errors",
        }

        chunk = chunk.rename(columns=rename)
        chunk = chunk[list(rename.values())]

        chunk["date"] = pd.to_datetime(chunk["date"], errors="coerce")
        chunk["use_chip"] = chunk["use_chip"].astype(bool)

        if chunk["amount"].dtype == object:
            chunk["amount"] = clean_currency(chunk["amount"])

        chunk.to_sql("transactions", engine, if_exists="append", index=False)
        total += len(chunk)

    print(f"Inserted {total} transactions")


# -------- Main --------
def main():
    engine = get_engine()
    base = os.getenv("DATA_DIR", "./data")

    load_users(engine, os.path.join(base, "users_data.csv"))
    load_cards(engine, os.path.join(base, "cards_data.csv"))
    load_transactions(engine, os.path.join(base, "transactions_data.csv"))

    print("\n=== DATA INGESTION COMPLETE ===\n")


if __name__ == "__main__":
    main()
