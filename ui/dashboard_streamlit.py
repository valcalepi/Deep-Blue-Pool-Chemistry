import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
EXCEL_FILE = 'pool_log.xlsx'

# 🔐 Load credentials from environment or Streamlit secrets
admin_username = os.getenv("ADMIN_USERNAME", "admin")
admin_name = os.getenv("ADMIN_NAME", "Michael")
admin_password_hash = os.getenv("ADMIN_PASSWORD_HASH")

viewer_username = os.getenv("VIEWER_USERNAME", "viewer")
viewer_name = os.getenv("VIEWER_NAME", "Guest")
viewer_password_hash = os.getenv("VIEWER_PASSWORD_HASH")

cookie_name = os.getenv("COOKIE_NAME", "pool_dashboard")
cookie_key = os.getenv("COOKIE_KEY", "abcdef")

# ✅ Validate presence of hashed passwords
missing = []
if not admin_password_hash:
    missing.append("ADMIN_PASSWORD_HASH")
if not viewer_password_hash:
    missing.append("VIEWER_PASSWORD_HASH")

if missing:
    st.error(f"Missing hashed password variables: {', '.join(missing)}")
    st.stop()

# ✅ Use pre-hashed passwords with correct structure
credentials = {
    "usernames": {
        admin_username: {
            "name": admin_name,
            "password": admin_password_hash,
            "role": "admin"
        },
        viewer_username: {
            "name": viewer_name,
            "password": viewer_password_hash,
            "role": "viewer"
        },
    }
}

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name=cookie_name,
    key=cookie_key,
    cookie_expiry_days=1
)

# ✅ Correct login method for latest version
authenticator.login(location="main")
auth_status = authenticator.authentication_status
name = authenticator.name
username = authenticator.username

# Page config
st.set_page_config(page_title="Pool Chemistry Dashboard", layout="wide")

# Authenticated view
if auth_status:
    st.sidebar.success(f"Welcome {name} ({username})")
    authenticator.logout("Logout", "sidebar")

    try:
        if authenticator.reset_password(username, 'Reset password'):
            st.success('Password modified successfully')
    except Exception as e:
        st.error(e)

    try:
        if authenticator.register_user('Register user', preauthorization=False):
            st.success('User registered successfully')
    except Exception as e:
        st.error(e)

    try:
        df = pd.read_excel(EXCEL_FILE)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    except Exception:
        st.error("Failed to load data.")
        st.stop()

    st.sidebar.header("Filters")
    start_date = st.sidebar.date_input("Start Date", df['Timestamp'].min().date())
    end_date = st.sidebar.date_input("End Date", df['Timestamp'].max().date())
    weather_filter = st.sidebar.checkbox("Show weather-based notes only")

    filtered_df = df[(df['Timestamp'].dt.date >= start_date) & (df['Timestamp'].dt.date <= end_date)]
    if weather_filter:
        filtered_df = filtered_df[filtered_df['Notes'].str.contains("Rain|UV", na=False)]

    st.title("💧 Deep Blue Pool Chemistry Dashboard")
    st.subheader("Recent Entries")
    st.dataframe(filtered_df.tail(10))

    st.subheader("pH and Chlorine Trends")
    st.line_chart(filtered_df.set_index('Timestamp')[['pH', 'Chlorine']])

    st.sidebar.markdown("---")
    st.sidebar.caption("Weather-based dosing recommendations are shown in the Notes column.")

elif auth_status is False:
    st.error("Invalid username or password.")
elif auth_status is None:
    st.warning("Please enter your credentials.")
