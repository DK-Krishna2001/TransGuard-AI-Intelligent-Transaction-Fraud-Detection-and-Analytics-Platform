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

## Quick Start (One Command)
```bash
docker compose up --build -d
```
Services:
- Postgres: localhost:5432 (db name `transguard`, user/password `postgres`)
- Adminer: http://localhost:8080 (System: PostgreSQL, Server: db, User: postgres, Password: postgres, Database: transguard)
- Dashboard: http://localhost:8501 (Streamlit, reads `analytics_warehouse.fact_transactions`)

## Phase Details and How to Run
- **Phase 1 (OLTP + ingestion)**  
  - Schema/security applied automatically when the Postgres container starts (`Phase1/schema.sql`, `Phase1/security.sql`).  
  - To (re)ingest CSVs: `python Phase1/ingest_data.py` (uses `data/` by default; set `DATA_DIR` to override). Requires `pandas`, `sqlalchemy`, `psycopg2-binary` if running outside Docker.

- **Phase 2 (dbt warehouse)**  
  - Project: `Phase2/transguard_dw`. Profiles entry should be `transguard_dw` pointing to Postgres `transguard` (schema `analytics` or your choice). Example `~/.dbt/profiles.yml`:
    ```yaml
    transguard_dw:
      target: dev
      outputs:
        dev:
          type: postgres
          host: localhost
          user: postgres
          password: postgres
          port: 5432
          dbname: transguard
          schema: analytics
          threads: 4
    ```
  - Build models: `cd Phase2/transguard_dw && dbt run` (or `dbt run --select fact_transactions` after ingestion).  
  - Tests: `dbt test`.  
  - Advanced queries + indexing tips: `Phase2/3_advance_queries+optimization.sql`.

- **Phase 3 (Streamlit dashboard)**  
  - App: `Phase3/app.py`; container built from `Phase3/Dockerfile`, deps in `Phase3/requirements.txt`.  
  - Environment vars (override if needed): `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`. Defaults in compose point at the `db` service.  
  - Views provided: KPI cards, daily trends (amount + error rate), merchant risk leaderboard (filters: state, min txns, top N), state spend summary. Powered by `analytics_warehouse.fact_transactions`.

## Stopping / Rebuilding
```bash
docker compose down               # stop
docker compose up --build -d      # rebuild + start (use after code changes)
```

## Stop Services
```bash
docker compose down
```

## Links
- Repo: https://github.com/DK-Krishna2001/transguard_ai/
- Phase 1 demo: https://youtu.be/MUG1i-Lt3hI


