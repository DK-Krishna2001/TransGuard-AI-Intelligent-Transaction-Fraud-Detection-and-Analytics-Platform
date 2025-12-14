import datetime as dt
import os
from typing import List, Tuple

import altair as alt
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


st.set_page_config(
    page_title="TransGuard AI – Transactions Dashboard",
    page_icon="💳",
    layout="wide",
)


# --- Database helpers ---
def _db_settings() -> dict:
    return {
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "postgres"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "transguard"),
    }


@st.cache_resource(show_spinner=False)
def get_engine() -> Engine:
    cfg = _db_settings()
    url = (
        f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
    )
    return create_engine(url)


def _make_filter_clause(states: List[str]) -> Tuple[str, dict]:
    filters = ["date_key BETWEEN :start_date AND :end_date"]
    params: dict = {}
    if states:
        filters.append("merchant_state = ANY(:states)")
        params["states"] = states
    clause = " AND ".join(filters)
    return clause, params


@st.cache_data(ttl=600, show_spinner=False)
def get_date_bounds() -> Tuple[dt.date, dt.date]:
    query = "SELECT MIN(date_key)::date AS min_date, MAX(date_key)::date AS max_date FROM analytics_warehouse.fact_transactions"
    with get_engine().begin() as conn:
        row = conn.execute(text(query)).one()
    return row.min_date, row.max_date


@st.cache_data(ttl=600, show_spinner=False)
def get_states() -> List[str]:
    query = """
        SELECT DISTINCT merchant_state
        FROM analytics_warehouse.fact_transactions
        WHERE merchant_state IS NOT NULL
        ORDER BY merchant_state
    """
    with get_engine().begin() as conn:
        df = pd.read_sql_query(text(query), conn)
    return df["merchant_state"].dropna().tolist()


@st.cache_data(ttl=600, show_spinner=False)
def load_kpis(start_date: dt.date, end_date: dt.date, states: Tuple[str, ...]) -> pd.DataFrame:
    clause, params = _make_filter_clause(list(states))
    params.update({"start_date": start_date, "end_date": end_date})
    query = f"""
        SELECT
            COUNT(*) AS txn_count,
            SUM(amount) AS total_amount,
            COUNT(*) FILTER (WHERE errors IS NOT NULL AND errors <> '') AS error_txns
        FROM analytics_warehouse.fact_transactions
        WHERE {clause}
    """
    with get_engine().begin() as conn:
        return pd.read_sql_query(text(query), conn, params=params)


@st.cache_data(ttl=600, show_spinner=False)
def load_timeseries(start_date: dt.date, end_date: dt.date, states: Tuple[str, ...]) -> pd.DataFrame:
    clause, params = _make_filter_clause(list(states))
    params.update({"start_date": start_date, "end_date": end_date})
    query = f"""
        SELECT
            date_key::date AS date,
            COUNT(*) AS txn_count,
            SUM(amount) AS total_amount,
            COUNT(*) FILTER (WHERE errors IS NOT NULL AND errors <> '') AS error_txns
        FROM analytics_warehouse.fact_transactions
        WHERE {clause}
        GROUP BY date_key
        ORDER BY date
    """
    with get_engine().begin() as conn:
        df = pd.read_sql_query(text(query), conn, params=params)
    df["error_rate"] = df["error_txns"] / df["txn_count"].replace(0, pd.NA)
    return df


@st.cache_data(ttl=600, show_spinner=False)
def load_merchant_leaderboard(
    start_date: dt.date,
    end_date: dt.date,
    states: Tuple[str, ...],
    min_txns: int,
    limit: int,
) -> pd.DataFrame:
    clause, params = _make_filter_clause(list(states))
    params.update(
        {
            "start_date": start_date,
            "end_date": end_date,
            "min_txns": min_txns,
            "limit": limit,
        }
    )
    query = f"""
        SELECT
            merchant_id,
            merchant_state,
            COUNT(*) AS txn_count,
            SUM(amount) AS total_spent,
            AVG(amount) AS avg_amount,
            COUNT(*) FILTER (WHERE errors IS NOT NULL AND errors <> '') AS error_txns,
            COUNT(*) FILTER (WHERE errors IS NOT NULL AND errors <> '')::decimal / NULLIF(COUNT(*), 0) AS error_rate
        FROM analytics_warehouse.fact_transactions
        WHERE {clause}
        GROUP BY merchant_id, merchant_state
        HAVING COUNT(*) >= :min_txns
        ORDER BY error_rate DESC, txn_count DESC
        LIMIT :limit
    """
    with get_engine().begin() as conn:
        df = pd.read_sql_query(text(query), conn, params=params)
    return df


@st.cache_data(ttl=600, show_spinner=False)
def load_state_summary(start_date: dt.date, end_date: dt.date, states: Tuple[str, ...]) -> pd.DataFrame:
    clause, params = _make_filter_clause(list(states))
    params.update({"start_date": start_date, "end_date": end_date})
    query = f"""
        SELECT
            merchant_state,
            COUNT(*) AS txn_count,
            SUM(amount) AS total_spent,
            COUNT(*) FILTER (WHERE errors IS NOT NULL AND errors <> '') AS error_txns,
            COUNT(*) FILTER (WHERE errors IS NOT NULL AND errors <> '')::decimal / NULLIF(COUNT(*), 0) AS error_rate
        FROM analytics_warehouse.fact_transactions
        WHERE {clause}
        GROUP BY merchant_state
        ORDER BY total_spent DESC
        LIMIT 20
    """
    with get_engine().begin() as conn:
        return pd.read_sql_query(text(query), conn, params=params)


# --- UI ---
st.title("TransGuard AI – Transactions Risk & Volume")
st.caption("Live view on analytics_warehouse.fact_transactions (dbt outputs)")

min_date, max_date = get_date_bounds()
if not min_date or not max_date:
    st.error("Could not determine date range from fact_transactions.")
    st.stop()

with st.sidebar:
    st.header("Filters")
    date_range = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    available_states = get_states()
    selected_states = st.multiselect(
        "Merchant state (optional)",
        options=available_states,
        default=[],
        help="Filter by merchant_state; leave blank for all states.",
    )

    st.markdown("---")
    min_txns = st.slider("Min transactions per merchant (leaderboard)", min_value=10, max_value=200, value=50, step=10)
    top_n = st.slider("Top merchants to show", min_value=5, max_value=50, value=15, step=5)

state_tuple = tuple(selected_states)

kpi_df = load_kpis(start_date, end_date, state_tuple)
timeseries_df = load_timeseries(start_date, end_date, state_tuple)
merchant_df = load_merchant_leaderboard(start_date, end_date, state_tuple, min_txns, top_n)
state_df = load_state_summary(start_date, end_date, state_tuple)


# --- KPI cards ---
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

txn_count = int(kpi_df["txn_count"].iloc[0]) if not kpi_df.empty else 0
total_amount = float(kpi_df["total_amount"].iloc[0] or 0)
error_txns = int(kpi_df["error_txns"].iloc[0]) if not kpi_df.empty else 0
error_rate = (error_txns / txn_count) if txn_count else 0

kpi_col1.metric("Transactions", f"{txn_count:,}")
kpi_col2.metric("Total Amount", f"${total_amount:,.0f}")
kpi_col3.metric("Error Rate", f"{error_rate:.2%}")


# --- Time series chart ---
st.subheader("Daily Trends")
if timeseries_df.empty:
    st.info("No data for the selected filters.")
else:
    timeseries_df["date"] = pd.to_datetime(timeseries_df["date"])
    base = alt.Chart(timeseries_df).encode(x="date:T")

    amount_line = base.mark_line(color="#2563eb").encode(
        y=alt.Y("total_amount:Q", title="Total amount ($)"),
        tooltip=["date:T", alt.Tooltip("total_amount:Q", format=",.0f")],
    )

    error_rate_line = base.mark_line(color="#dc2626").encode(
        y=alt.Y("error_rate:Q", title="Error rate", axis=alt.Axis(format="%"), scale=alt.Scale(domain=(0, None))),
        tooltip=["date:T", alt.Tooltip("error_rate:Q", format=".2%"), alt.Tooltip("error_txns:Q", format=",")],
    )

    st.altair_chart(
        alt.layer(amount_line, error_rate_line).resolve_scale(y="independent").properties(height=360),
        use_container_width=True,
    )


# --- Merchant leaderboard ---
st.subheader("Merchant Risk Leaderboard")
if merchant_df.empty:
    st.info("No merchants match the current filters.")
else:
    merchant_df["error_rate_pct"] = merchant_df["error_rate"].fillna(0) * 100
    chart = (
        alt.Chart(merchant_df)
        .mark_bar()
        .encode(
            x=alt.X("error_rate_pct:Q", title="Error rate (%)"),
            y=alt.Y("merchant_id:N", sort="-x", title="Merchant"),
            color=alt.Color("merchant_state:N", title="State"),
            tooltip=[
                "merchant_id",
                "merchant_state",
                alt.Tooltip("txn_count:Q", format=","),
                alt.Tooltip("total_spent:Q", format=",.0f", title="Total spent"),
                alt.Tooltip("avg_amount:Q", format=",.0f", title="Avg txn"),
                alt.Tooltip("error_rate:Q", format=".2%"),
            ],
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)
    st.dataframe(
        merchant_df.rename(columns={"error_rate_pct": "error_rate_percent"}),
        use_container_width=True,
        hide_index=True,
    )


# --- State summary ---
st.subheader("State Summary (Top by Spend)")
if state_df.empty:
    st.info("No state-level data for the selected filters.")
else:
    state_df["error_rate_pct"] = state_df["error_rate"].fillna(0) * 100
    bar = (
        alt.Chart(state_df)
        .mark_bar(color="#10b981")
        .encode(
            x=alt.X("total_spent:Q", title="Total spent ($)"),
            y=alt.Y("merchant_state:N", sort="-x", title="State"),
            tooltip=[
                "merchant_state",
                alt.Tooltip("txn_count:Q", format=","),
                alt.Tooltip("total_spent:Q", format=",.0f", title="Total spent"),
                alt.Tooltip("error_rate:Q", format=".2%"),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(bar, use_container_width=True)
    st.dataframe(
        state_df[["merchant_state", "txn_count", "total_spent", "error_rate_pct"]].rename(
            columns={"error_rate_pct": "error_rate_percent"}
        ),
        use_container_width=True,
        hide_index=True,
    )


st.caption(
    "Notes: error_rate uses transactions where errors is not null/empty. "
    "Filters apply to analytics_warehouse.fact_transactions; dim tables are not required for these aggregates."
)
