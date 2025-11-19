# TransGuard AI – Phase 1 (Database Foundation - OLTP)

This repository implements Phase 1 of the EAS 550 group project:
a normalized PostgreSQL database and ingestion pipeline for a
synthetic credit card transaction and fraud dataset.

## 1. Tech Stack

- PostgreSQL 16 (OLTP database)
- Docker + docker-compose
- Python 3, Pandas, SQLAlchemy, psycopg2-binary
- Adminer (web UI for Postgres)

## 2. Folder Structure

```text
transguard-ai/
  docker-compose.yml
  README.md

  phase1/
    schema.sql
    ingest_data.py
    security.sql
    erd.md
    3nf_justification.md

  data/
    users_data.csv
    cards_data.csv
    transactions_data.csv
```

## 3. How to Run the Database

Start PostgreSQL + Adminer
  docker-compose up -d

Stop Services
  docker-compose down

Once Running

Postgres: localhost:5432

Adminer UI: http://localhost:8080

System: PostgreSQL
Server: db
Username: postgres
Password: postgres
Database: transguard


## 3. Git Repo

Link: https://github.com/DK-Krishna2001/transguard_ai/

