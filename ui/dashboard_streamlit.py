import os
import logging
from datetime import datetime
from typing import Optional

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from dotenv import load_dotenv

# --- Setup logging to file for full tracebacks
LOG_FILE = "dashboard_streamlit.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s"
)

# --- Streamlit page config
st.set_page_config(page_title="Pool Chemistry Dashboard", layout="wide")

# --- Load .env
load_dotenv()

# --- Config
EXCEL_FILE = os.getenv("EXCEL_FILE", "pool_log.xlsx")

admin_username = os.getenv("ADMIN_USERNAME", "admin")
admin_name = os.getenv("ADMIN_NAME", "Michael")
admin_password_hash = os.getenv("ADMIN_PASSWORD_HASH")

viewer_username = os.getenv("VIEWER_USERNAME", "viewer")
viewer_name = os.getenv("VIEWER_NAME", "Guest")
viewer_password_hash = os.getenv("VIEWER_PASSWORD_HASH")

cookie_name = os.getenv("COOKIE_NAME", "pool_dashboard")
cookie_key = os.getenv("COOKIE_KEY", "abcdef")

# --- Quick debug output (temporary; remove once stable)
st.sidebar.markdown("### Debug")
st.sidebar.text("Inspect runtime values below")
st.sidebar.write("EXCEL_FILE:", EXCEL_FILE)
st.sidebar.write("ADMIN_USERNAME:", admin_username)
st.sidebar.write("ADMIN_HASH loaded:", bool(admin_password_hash))
st.sidebar.write("VIEWER_HASH loaded:", bool(viewer_password_hash))
st.sidebar.write("Log file:", LOG_FILE)

# --- Validate hashed passwords
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

# --- Instantiate authenticator (guard exceptions)
try:
    authenticator = stauth.Authenticate(
        credentials=credentials,
        cookie_name=cookie_name,
        key=cookie_key,
        cookie_expiry_days=1
    )
except Exception as e:
    st.error("Failed to initialize authenticator. See logs.")
    logging.exception("Authenticator initialization failed")
    st.stop()

# --- Login
try:
    name, authentication_status, username = authenticator.login(location="main")
except Exception as e:
    # Some versions may behave differently; fall back to attributes
    logging.exception("authenticator.login raised")
    st.error("Login raised an exception. Falling back to session state inspection.")
    name = getattr(authenticator, "name", None) or st.session_state.get("name")
    authentication_status = getattr(authenticator, "authentication_status", None) or st.session_state.get("authentication_status")
    username = getattr(authenticator, "username", None) or st.session_state.get("username")

# --- Post-login flow
if authentication_status:
    st.sidebar.success(f"Welcome {name} ({username})")
    try:
        # Logout button (safe)
        if hasattr(authenticator, "logout"):
            authenticator.logout("Logout", "sidebar")
    except Exception:
        logging.exception("Logout failed (ignored)")

    # Safe optional account actions (only call if present; wrap exceptions)
    try:
        if hasattr(authenticator, "reset_password"):
            with st.expander("Account actions"):
                try:
                    if authenticator.reset_password(username, "Reset password"):
                        st.success("Password modified successfully")
                except Exception as inner:
                    st.warning("Password reset raised an error; check logs.")
                    logging.exception("reset_password raised")
                try:
                    if hasattr(authenticator, "register_user"):
                        if authenticator.register_user("Register user", preauthorization=False):
                            st.success("User registered successfully")
                except Exception:
                    st.warning("User registration raised an error; check logs.")
                    logging.exception("register_user raised")
    except Exception:
        logging.exception("Account actions wrapper failed")

    # Load Excel data with detailed error reporting
    df = None
    try:
        if not os.path.exists(EXCEL_FILE):
            raise FileNotFoundError(f"Excel file not found at path: {EXCEL_FILE}")

        df = pd.read_excel(EXCEL_FILE)
        if df.empty:
            st.info("Excel file loaded but contains no rows.")
        # Validate Timestamp column
        if "Timestamp" not in df.columns:
            raise KeyError("Missing required column: 'Timestamp' in Excel file.")
        # Convert Timestamp
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="raise")
    except Exception as e:
        st.error("Failed to load or parse Excel data. Full error shown below.")
        st.exception(e)  # Show stack/exception in Streamlit UI for debugging
        logging.exception("Failed to load/parse Excel file")
        st.stop()

    # Filters
    try:
        min_date = df["Timestamp"].min().date() if not df.empty else datetime.today().date()
        max_date = df["Timestamp"].max().date() if not df.empty else datetime.today().date()
    except Exception as e:
        logging.exception("Failed to compute min/max dates")
        min_date = datetime.today().date()
        max_date = datetime.today().date()

    st.sidebar.header("Filters")
    start_date = st.sidebar.date_input("Start Date", min_date)
    end_date = st.sidebar.date_input("End Date", max_date)
    weather_filter = st.sidebar.checkbox("Show weather-based notes only")

    # Apply date filtering safely
    try:
        filtered_df = df[(df["Timestamp"].dt.date >= start_date) & (df["Timestamp"].dt.date <= end_date)]
    except Exception as e:
        st.warning("Date filtering failed; showing all rows.")
        logging.exception("Date filtering failed")
        filtered_df = df.copy()

    # Weather filter
    if weather_filter:
        if "Notes" in filtered_df.columns:
            try:
                filtered_df = filtered_df[filtered_df["Notes"].str.contains("Rain|UV", na=False)]
            except Exception:
                st.warning("Notes filter failed; ignoring weather filter.")
                logging.exception("Notes filter failed")

    # Main dashboard content
    st.title("💧 Deep Blue Pool Chemistry Dashboard")
    st.subheader("Recent Entries")
    st.dataframe(filtered_df.tail(20))

    # Plot metrics if present
    metric_cols = [c for c in ["pH", "Chlorine"] if c in filtered_df.columns]
    if metric_cols and not filtered_df.empty:
        try:
            st.subheader("pH and Chlorine Trends")
            st.line_chart(filtered_df.set_index("Timestamp")[metric_cols])
        except Exception:
            st.warning("Failed to plot trends; see logs.")
            logging.exception("Plotting failed")
    else:
        st.info("pH and Chlorine columns not available to plot.")

    st.sidebar.markdown("---")
    st.sidebar.caption("Weather-based dosing recommendations are shown in the Notes column.")

elif authentication_status is False:
    st.error("Invalid username or password.")
    logging.warning("Login attempt failed for a user.")
elif authentication_status is None:
    st.warning("Please enter your credentials.")
    logging.info("Login form presented; no credentials submitted yet.")
else:
    st.warning("Authentication state unknown. Check the log file for details.")
    logging.warning(f"Unexpected authentication_status value: {authentication_status}")
