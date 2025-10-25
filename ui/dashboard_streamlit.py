"""
Robust Streamlit dashboard with:
- explicit .env loading (optional path)
- absolute logging to user home for reliable logs
- clear runtime debug in sidebar
- safe streamlit-authenticator instantiation and verbose exception reporting
- Excel file load from disk, optional upload, or fallback empty DataFrame
- safe plotting and filters
Remove or reduce debug sections once stable.
"""
import os
import logging
from datetime import datetime
from typing import Optional

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from dotenv import load_dotenv
import bcrypt

# -------------------- Config --------------------
# Optional: set DOTENV_PATH environment variable if your .env is not co-located
DOTENV_PATH = os.getenv("DOTENV_PATH", None)
if DOTENV_PATH:
    load_dotenv(dotenv_path=DOTENV_PATH)
else:
    load_dotenv()

# Use an absolute log file in the user's home directory to avoid cwd issues
LOG_FILE = os.path.join(os.path.expanduser("~"), "deep_blue_dashboard.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s"
)
# Also stream logs to stdout so Streamlit captures them in server console
logging.getLogger().addHandler(logging.StreamHandler())

# -------------------- Streamlit page config --------------------
st.set_page_config(page_title="Pool Chemistry Dashboard", layout="wide")

# -------------------- Environment / Credentials --------------------
EXCEL_FILE = os.getenv("EXCEL_FILE", "pool_log.xlsx")

admin_username = os.getenv("ADMIN_USERNAME", "admin")
admin_name = os.getenv("ADMIN_NAME", "Michael")
admin_password_hash = os.getenv("ADMIN_PASSWORD_HASH")

viewer_username = os.getenv("VIEWER_USERNAME", "viewer")
viewer_name = os.getenv("VIEWER_NAME", "Guest")
viewer_password_hash = os.getenv("VIEWER_PASSWORD_HASH")

cookie_name = os.getenv("COOKIE_NAME", "pool_dashboard")
cookie_key = os.getenv("COOKIE_KEY", "abcdef")

# -------------------- Sidebar runtime debug (temporary) --------------------
st.sidebar.header("Runtime debug (temporary)")
st.sidebar.write("Working dir:", os.getcwd())
st.sidebar.write("Python executable:", os.sys.executable)
st.sidebar.write("Dotenv path in use:", DOTENV_PATH or "(default .env lookup)")
st.sidebar.write("EXCEL_FILE:", EXCEL_FILE)
st.sidebar.write("Admin hash present:", bool(admin_password_hash))
st.sidebar.write("Viewer hash present:", bool(viewer_password_hash))
st.sidebar.write("Log file (absolute):", LOG_FILE)

# -------------------- Validate presence of hashed passwords --------------------
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

# Quick external bcrypt sanity check (non-sensitive): ensure hashes verify expected plain passwords
# NOTE: these lines are safe for debugging but remove if you consider exposing test passwords undesirable.
try:
    admin_check = bcrypt.checkpw("poolmaster123".encode(), admin_password_hash.encode())
    viewer_check = bcrypt.checkpw("guestaccess".encode(), viewer_password_hash.encode())
    st.sidebar.write("bcrypt check (admin):", admin_check)
    st.sidebar.write("bcrypt check (viewer):", viewer_check)
except Exception as e:
    logging.exception("bcrypt check failed")
    st.sidebar.write("bcrypt check raised:", repr(e))

# -------------------- Build credentials dict --------------------
credentials = {
    "usernames": {
        admin_username: {"name": admin_name, "password": admin_password_hash, "role": "admin"},
        viewer_username: {"name": viewer_name, "password": viewer_password_hash, "role": "viewer"},
    }
}
st.sidebar.write("Credentials keys:", list(credentials["usernames"].keys()))
st.sidebar.write("streamlit-authenticator version:", getattr(stauth, "__version__", "unknown"))

# -------------------- Instantiate authenticator (verbose) --------------------
try:
    authenticator = stauth.Authenticate(
        credentials=credentials,
        cookie_name=cookie_name,
        key=cookie_key,
        cookie_expiry_days=1
    )
    st.sidebar.write("Authenticator created OK")
except Exception as e:
    logging.exception("Authenticator creation failed")
    st.sidebar.exception(e)
    st.error("Authenticator initialization failed. See sidebar and log file for details.")
    st.stop()

# -------------------- Login (wrapped, verbose on exception) --------------------
try:
    name, authentication_status, username = authenticator.login(location="main")
    st.sidebar.write("authenticator.login returned:", authentication_status, name, username)
except Exception as e:
    logging.exception("authenticator.login raised an exception")
    st.sidebar.error("authenticator.login raised an exception; fallback in use")
    st.sidebar.exception(e)
    # Fallback: try to recover state from authenticator attributes or session_state
    name = getattr(authenticator, "name", None) or st.session_state.get("name")
    authentication_status = getattr(authenticator, "authentication_status", None) or st.session_state.get("authentication_status")
    username = getattr(authenticator, "username", None) or st.session_state.get("username")

# -------------------- Post-authentication UI --------------------
if authentication_status:
    st.sidebar.success(f"Welcome {name} ({username})")
    # Logout (safe)
    try:
        if hasattr(authenticator, "logout"):
            authenticator.logout("Logout", "sidebar")
    except Exception:
        logging.exception("Logout raised exception (ignored)")

    # Optional account actions inside an expander (guarded)
    try:
        with st.expander("Account actions"):
            if hasattr(authenticator, "reset_password"):
                try:
                    if authenticator.reset_password(username, "Reset password"):
                        st.success("Password modified successfully")
                except Exception:
                    st.warning("Password reset raised an error; check logs")
                    logging.exception("reset_password raised")
            if hasattr(authenticator, "register_user"):
                try:
                    if authenticator.register_user("Register user", preauthorization=False):
                        st.success("User registered successfully")
                except Exception:
                    st.warning("User registration raised an error; check logs")
                    logging.exception("register_user raised")
    except Exception:
        logging.exception("Account actions wrapper failed")

    # -------------------- Load dataset (disk -> upload -> empty fallback) --------------------
    df: Optional[pd.DataFrame] = None

    # Try disk path first
    if os.path.exists(EXCEL_FILE):
        try:
            df = pd.read_excel(EXCEL_FILE)
            logging.info(f"Loaded Excel from disk: {EXCEL_FILE}")
        except Exception:
            logging.exception("Failed reading Excel file from disk")
            df = None

    # If disk load failed or file missing, allow user upload
    if df is None:
        st.info("No valid Excel file found at configured path or it failed to load.")
        uploaded = st.file_uploader("Upload Excel file (XLSX/XLS) to populate dashboard", type=["xlsx", "xls"])
        if uploaded is not None:
            try:
                df = pd.read_excel(uploaded)
                logging.info("Loaded Excel from uploaded file")
            except Exception:
                logging.exception("Uploaded Excel read failed")
                st.error("Uploaded file could not be read as Excel. See log for details.")
                df = None

    # Final fallback: create minimal empty DataFrame so UI still renders
    if df is None:
        st.warning("Creating an empty dataset so the dashboard can render. Upload an Excel file to populate data.")
        columns = ["Timestamp", "pH", "Chlorine", "Notes"]
        df = pd.DataFrame(columns=columns)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    # Validate Timestamp column presence and parsing
    if "Timestamp" not in df.columns:
        st.error("Dataset missing required column: 'Timestamp'. Ensure your Excel contains it or re-upload.")
        logging.error("Timestamp column missing")
        st.stop()
    try:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="raise")
    except Exception:
        logging.exception("Timestamp parsing failed")
        st.error("Failed to parse 'Timestamp' values. Ensure they are valid datetimes.")
        st.stop()

    # -------------------- Filters --------------------
    try:
        min_date = df["Timestamp"].min().date() if not df["Timestamp"].isna().all() else datetime.today().date()
        max_date = df["Timestamp"].max().date() if not df["Timestamp"].isna().all() else datetime.today().date()
    except Exception:
        logging.exception("Failed computing min/max dates")
        min_date = datetime.today().date()
        max_date = datetime.today().date()

    st.sidebar.header("Filters")
    start_date = st.sidebar.date_input("Start Date", min_date)
    end_date = st.sidebar.date_input("End Date", max_date)
    weather_filter = st.sidebar.checkbox("Show weather-based notes only")

    try:
        filtered_df = df[(df["Timestamp"].dt.date >= start_date) & (df["Timestamp"].dt.date <= end_date)]
    except Exception:
        logging.exception("Date filtering failed")
        st.warning("Date filtering failed; showing full dataset")
        filtered_df = df.copy()

    if weather_filter:
        if "Notes" in filtered_df.columns:
            try:
                filtered_df = filtered_df[filtered_df["Notes"].str.contains("Rain|UV", na=False)]
            except Exception:
                logging.exception("Notes filter failed")
                st.warning("Notes filter failed; ignoring weather filter")
        else:
            st.info("No Notes column available to filter by weather")

    # -------------------- Dashboard content --------------------
    st.title("💧 Deep Blue Pool Chemistry Dashboard")
    st.subheader("Recent Entries")
    st.dataframe(filtered_df.tail(20))

    metric_cols = [c for c in ["pH", "Chlorine"] if c in filtered_df.columns]
    if metric_cols and not filtered_df.empty and not filtered_df["Timestamp"].isna().all():
        try:
            st.subheader("pH and Chlorine Trends")
            st.line_chart(filtered_df.set_index("Timestamp")[metric_cols])
        except Exception:
            logging.exception("Plotting failed")
            st.warning("Failed to render trends; see log")
    else:
        st.info("pH and Chlorine columns not available to plot or no data present.")

    st.sidebar.markdown("---")
    st.sidebar.caption("Upload an Excel file at any time to replace the dataset. Remove debug info when stable.")

elif authentication_status is False:
    st.error("Invalid username or password.")
    logging.warning("Login attempt failed for a user.")
elif authentication_status is None:
    st.warning("Please enter your credentials.")
    logging.info("Login form presented; no credentials submitted yet.")
else:
    st.warning("Authentication state unknown. Check the log file for details.")
    logging.warning(f"Unexpected authentication_status value: {authentication_status}")
