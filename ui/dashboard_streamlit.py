import streamlit as st
import pandas as pd
from datetime import datetime

EXCEL_FILE = 'pool_log.xlsx'

def load_data():
    try:
        df = pd.read_excel(EXCEL_FILE)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df
    except Exception:
        return pd.DataFrame()

def main():
    st.set_page_config(page_title="Pool Chemistry Dashboard", layout="wide")
    st.title("💧 Deep Blue Pool Chemistry Dashboard")

    df = load_data()
    if df.empty:
        st.warning("No data found.")
        return

    st.line_chart(df.set_index('Timestamp')[['pH', 'Chlorine']])
    st.dataframe(df.tail(10))

    st.sidebar.header("Weather-Based Recommendations")
    notes = df['Notes'].dropna().tail(1).values
    st.sidebar.write(notes[0] if len(notes) else "No recommendations available.")

if __name__ == "__main__":
    main()
