# TransGuard AI – OLTP, Warehouse, and Dashboard

End-to-end project for synthetic credit card transactions and fraud risk:
1) Phase 1 OLTP schema + ingestion, 2) Phase 2 dbt warehouse, 3) Phase 3 Streamlit dashboard.

## Stack
- PostgreSQL 16 (OLTP + warehouse schemas)
- dbt (Phase2 models in `Phase2/transguard_dw`)
- Streamlit (Phase3 dashboard)
- Docker + docker-compose, Adminer

## Repo Layout
```text
docker-compose.yaml
README.md
Phase1/        # OLTP DDL + ingestion
Phase2/        # dbt project + advanced SQL
Phase3/        # Streamlit dashboard (Phase 3)
data/          # CSVs for ingestion
```

## Run Everything (Postgres, Adminer, Dashboard)
```bash
docker compose up --build -d
```
Services:
- Postgres: localhost:5432 (db name `transguard`, user/password `postgres`)
- Adminer: http://localhost:8080 (System: PostgreSQL, Server: db, User: postgres, Password: postgres, Database: transguard)
- Dashboard: http://localhost:8501 (Streamlit, reads `analytics_warehouse.fact_transactions`)

## Phase Details
- Phase1: `Phase1/schema.sql`, `Phase1/security.sql`, `Phase1/ingest_data.py` load CSVs in `data/` into the OLTP schema.
- Phase2: `Phase2/transguard_dw` dbt project builds staging and warehouse models (`analytics_staging` / `analytics_warehouse`). Advanced queries + indexing tips in `Phase2/3_advance_queries+optimization.sql`.
- Phase3: `Phase3/app.py` Streamlit dashboard with KPI cards, daily trends, merchant risk leaderboard, and state summary. Configurable via env vars: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.

## Stop Services
```bash
docker compose down
```

## Links
- Repo: https://github.com/DK-Krishna2001/transguard_ai/
- Phase 1 demo: https://youtu.be/MUG1i-Lt3hI


