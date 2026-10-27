import streamlit as st
import pandas as pd
from src.database import init_db, get_all_results


st.set_page_config(
    page_title="Pipeline Health Observer",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Pipeline Health Observer")
st.caption("Monitoring data quality checks for the student pipeline.")

init_db()
results = get_all_results()

if not results:
    st.warning("No health check results found. Run `python src/pipeline.py` first.")
    st.stop()

df = pd.DataFrame(results)

# ── Summary metrics ───────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Runs", len(df))
col2.metric("✅ OK",   int((df["status"] == "OK").sum()))
col3.metric("⚠️ WARN", int((df["status"] == "WARN").sum()))
col4.metric("❌ FAIL", int((df["status"] == "FAIL").sum()))

st.divider()

# ── Colour-coded results table ────────────────────────────────────────────────
STATUS_COLOURS = {"OK": "🟢", "WARN": "🟡", "FAIL": "🔴"}

df["Status"] = df["status"].map(lambda s: f"{STATUS_COLOURS.get(s, '')} {s}")
df = df.rename(columns={
    "check_name": "Check",
    "details":    "Details",
    "run_at":     "Run At",
})

st.subheader("All Check Results")
st.dataframe(
    df[["Check", "Status", "Details", "Run At"]],
    use_container_width=True,
    hide_index=True,
)

# ── Latest run summary ────────────────────────────────────────────────────────
st.subheader("Latest Run")
latest_run = df["Run At"].max()
latest = df[df["Run At"] == latest_run]
st.write(f"Last executed at: **{latest_run}**")
st.dataframe(
    latest[["Check", "Status", "Details"]],
    use_container_width=True,
    hide_index=True,
)
