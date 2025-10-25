import os
import logging
from datetime import datetime
from typing import Optional

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from dotenv import load_dotenv

# --- Logging
LOG_FILE = "dashboard_streamlit.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s"
)

# --- Streamlit page config
st.set_page_config(page_title="Pool Chemistry Dashboard", layout="wide")

# --- Load environment
load_dotenv()

# --- Config and credentials
EXCEL_FILE = os.getenv("EXCEL_FILE", "pool_log.xlsx")

admin_username = os.getenv("ADMIN_USERNAME", "admin")
admin_name = os.getenv("ADMIN_NAME", "Michael")
admin_password_hash = os.getenv("ADMIN_PASSWORD_HASH")

viewer_username = os.getenv("VIEWER_USERNAME", "viewer")
viewer_name = os.getenv("VIEWER_NAME", "Guest")
viewer_password_hash = os.getenv("VIEWER_PASSWORD_HASH")

cookie_name = os.getenv("COOKIE_NAME", "pool_dashboard")
cookie_key = os.getenv("COOKIE_KEY", "abcdef")

# --- Sidebar debug (temporary)
st.sidebar.markdown("### Debug")
st.sidebar.write("EXCEL_FILE:", EXCEL_FILE)
st.sidebar.write("Admin hash present:", bool(admin_password_hash))
st.sidebar.write("Viewer hash present:", bool(viewer_password_hash))
st.sidebar.write("Log file:", LOG_FILE)

# --- Validate hashed passwords early
missing = []
if not admin_password_hash:
    missing.append("ADMIN_PASSWORD_HASH")
if not viewer_password_hash:
    missing.append("VIEWER_PASSWORD_HASH")
if missing:
    msg = f"Missing hashed password variables: {', '.join(missing)}"
    st.error(msg)
    logging.error(msg)
    st.stop()

# --- Credentials for authenticator
credentials = {
    "usernames": {
        admin_username: {"name": admin_name, "password": admin_password_hash, "role": "admin"},
        viewer_username: {"name": viewer_name, "password": viewer_password_hash, "role": "viewer"},
    }
}

# --- Instantiate authenticator
try:
    authenticator = stauth.Authenticate(
        credentials=credentials,
        cookie_name=cookie_name,
        key=cookie_key,
        cookie_expiry_days=1
    )
except Exception:
    st.error("Failed to initialize authenticator. See logs.")
    logging.exception("Authenticator initialization failed")
    st.stop()

# --- Login with robust fallback
try:
    name, authentication_status, username = authenticator.login(location="main")
except Exception:
    logging.exception("authenticator.login raised")
    st.warning("Login raised an exception. Falling back to session state inspection.")
    name = getattr(authenticator, "name", None) or st.session_state.get("name")
    authentication_status = getattr(authenticator, "authentication_status", None) or st.session_state.get("authentication_status")
    username = getattr(authenticator, "username", None) or st.session_state.get("username")

# --- After authentication
if authentication_status:
    st.sidebar.success(f"Welcome {name} ({username})")
    try:
        if hasattr(authenticator, "logout"):
            authenticator.logout("Logout", "sidebar")
    except Exception:
        logging.exception("Logout failed (ignored)")

    # Account actions wrapped
    try:
        with st.expander("Account actions"):
            if hasattr(authenticator, "reset_password"):
                try:
                    if authenticator.reset_password(username, "Reset password"):
                        st.success("Password modified successfully")
                except Exception:
                    st.warning("Password reset raised an error; check logs.")
                    logging.exception("reset_password raised")
            if hasattr(authenticator, "register_user"):
                try:
                    if authenticator.register_user("Register user", preauthorization=False):
                        st.success("User registered successfully")
                except Exception:
                    st.warning("User registration raised an error; check logs.")
                    logging.exception("register_user raised")
    except Exception:
        logging.exception("Account actions wrapper failed")

    # --- Load Excel from disk if present, otherwise offer upload or create empty DataFrame
    df = None
    load_error = None

    # Option A: try disk path
    if os.path.exists(EXCEL_FILE):
        try:
            df = pd.read_excel(EXCEL_FILE)
        except Exception as e:
            load_error = e
            logging.exception("Failed reading Excel file from disk")

    # Option B: allow user to upload a file via UI if disk file missing or failed
    if df is None:
        st.info("No valid Excel file found at configured path or it failed to load.")
        uploaded = st.file_uploader("Upload Excel file (optional) to populate dashboard", type=["xlsx", "xls"])
        if uploaded is not None:
            try:
                df = pd.read_excel(uploaded)
            except Exception as e:
                st.error("Uploaded file could not be read as Excel. See logs.")
                logging.exception("Uploaded Excel read failed")
                df = None

    # Option C: create minimal empty DataFrame so dashboard still renders
    if df is None:
        st.warning("Creating a new empty dataset so the dashboard can render. Add rows by uploading an Excel file later.")
        columns = ["Timestamp", "pH", "Chlorine", "Notes"]
        df = pd.DataFrame(columns=columns)
        # Ensure Timestamp dtype exists for date widgets
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    # Validate Timestamp column exists and convert
    if "Timestamp" not in df.columns:
        st.error("EXCEL data missing required 'Timestamp' column. Add it to your Excel or re-upload.")
        logging.error("Timestamp column missing in dataframe")
        st.stop()
    try:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="raise")
    except Exception as e:
        st.error("Failed to parse 'Timestamp' values in the dataset. Check formatting.")
        logging.exception("Timestamp parsing failed")
        st.stop()

    # Filters
    try:
        min_date = df["Timestamp"].min().date() if not df["Timestamp"].isna().all() else datetime.today().date()
        max_date = df["Timestamp"].max().date() if not df["Timestamp"].isna().all() else datetime.today().date()
    except Exception:
        min_date = datetime.today().date()
        max_date = datetime.today().date()

    st.sidebar.header("Filters")
    start_date = st.sidebar.date_input("Start Date", min_date)
    end_date = st.sidebar.date_input("End Date", max_date)
    weather_filter = st.sidebar.checkbox("Show weather-based notes only")

    # Apply date filter safely
    try:
        filtered_df = df[
            (df["Timestamp"].dt.date >= start_date) & (df["Timestamp"].dt.date <= end_date)
        ]
    except Exception:
        st.warning("Date filtering failed; showing all rows.")
        logging.exception("Date filtering failed")
        filtered_df = df.copy()

    # Weather filter
    if weather_filter:
        if "Notes" in filtered_df.columns:
            try:
                filtered_df = filtered_df[filtered_df["Notes"].str.contains("Rain|UV", na=False)]
            except Exception:
                st.warning("Notes filter failed; ignoring.")
                logging.exception("Notes filter failed")
        else:
            st.info("No Notes column available to filter by weather.")

    # Dashboard UI
    st.title("💧 Deep Blue Pool Chemistry Dashboard")
    st.subheader("Recent Entries")
    st.dataframe(filtered_df.tail(20))

    metric_cols = [c for c in ["pH", "Chlorine"] if c in filtered_df.columns]
    if metric_cols and not filtered_df.empty and not filtered_df["Timestamp"].isna().all():
        try:
            st.subheader("pH and Chlorine Trends")
            st.line_chart(filtered_df.set_index("Timestamp")[metric_cols])
        except Exception:
            st.warning("Failed to plot trends; see logs.")
            logging.exception("Plotting failed")
    else:
        st.info("pH and Chlorine columns not available to plot or no data present.")

    st.sidebar.markdown("---")
    st.sidebar.caption("You can upload an Excel file at any time to replace the dataset.")

elif authentication_status is False:
    st.error("Invalid username or password.")
    logging.warning("Login attempt failed")
elif authentication_status is None:
    st.warning("Please enter your credentials.")
else:
    st.warning("Authentication state unknown. Check logs.")
    logging.warning(f"Unexpected authentication_status value: {authentication_status}")
