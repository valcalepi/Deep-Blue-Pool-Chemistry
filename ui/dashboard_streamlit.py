import os
from datetime import datetime
from typing import Optional, Tuple

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from dotenv import load_dotenv

# Page config early to avoid Streamlit warnings
st.set_page_config(page_title="Pool Chemistry Dashboard", layout="wide")

# Load environment variables
load_dotenv()
EXCEL_FILE = "pool_log.xlsx"

# Load credentials from environment or Streamlit secrets
admin_username = os.getenv("ADMIN_USERNAME", "admin")
admin_name = os.getenv("ADMIN_NAME", "Michael")
admin_password_hash = os.getenv("ADMIN_PASSWORD_HASH")

viewer_username = os.getenv("VIEWER_USERNAME", "viewer")
viewer_name = os.getenv("VIEWER_NAME", "Guest")
viewer_password_hash = os.getenv("VIEWER_PASSWORD_HASH")

cookie_name = os.getenv("COOKIE_NAME", "pool_dashboard")
cookie_key = os.getenv("COOKIE_KEY", "abcdef")

# Validate presence of hashed passwords
missing = []
if not admin_password_hash:
    missing.append("ADMIN_PASSWORD_HASH")
if not viewer_password_hash:
    missing.append("VIEWER_PASSWORD_HASH")
if missing:
    st.error(f"Missing hashed password variables: {', '.join(missing)}")
    st.stop()

# Credentials structure required by streamlit-authenticator
credentials = {
    "usernames": {
        admin_username: {
            "name": admin_name,
            "password": admin_password_hash,
            "role": "admin",
        },
        viewer_username: {
            "name": viewer_name,
            "password": viewer_password_hash,
            "role": "viewer",
        },
    }
}

# Create authenticator
authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name=cookie_name,
    key=cookie_key,
    cookie_expiry_days=1,
)

def perform_login(auth: stauth.Authenticate) -> Tuple[Optional[str], Optional[bool], Optional[str]]:
    """
    Attempt to call auth.login(...) and return (name, authentication_status, username).
    Handles versions that return a tuple and versions that set attributes or session_state.
    """
    # Try calling .login and capture return value
    try:
        result = auth.login(location="main")
    except TypeError:
        # Some versions may require no args
        try:
            result = auth.login()
        except Exception:
            result = None
    except Exception:
        result = None

    # If .login returned the expected tuple
    if isinstance(result, tuple) and len(result) == 3:
        return result[0], result[1], result[2]

    # Fallback to reading attributes on the authenticator instance
    name = getattr(auth, "name", None)
    auth_status = getattr(auth, "authentication_status", None)
    username = getattr(auth, "username", None)

    # Some versions expose alternative attribute names; check common alternatives
    if auth_status is None:
        auth_status = getattr(auth, "auth_status", None)
    if name is None:
        name = getattr(auth, "user_name", None)
    if username is None:
        username = getattr(auth, "user", None)

    # Final fallback: check Streamlit session_state (some integrations populate these)
    if auth_status is None:
        auth_status = st.session_state.get("authentication_status")
    if name is None:
        name = st.session_state.get("name")
    if username is None:
        username = st.session_state.get("username")

    return name, auth_status, username

# Perform login in a robust way
name, authentication_status, username = perform_login(authenticator)

# Login state handling
if authentication_status:
    st.sidebar.success(f"Welcome {name} ({username})")
    try:
        authenticator.logout("Logout", "sidebar")
    except Exception:
        # If logout method signature changed, ignore gracefully
        pass

    # Optional: account actions only if methods exist
    try:
        if getattr(authenticator, "reset_password", None):
            if authenticator.reset_password(username, "Reset password"):
                st.success("Password modified successfully")
    except Exception as e:
        st.error(f"Password reset error: {e}")

    try:
        if getattr(authenticator, "register_user", None):
            if authenticator.register_user("Register user", preauthorization=False):
                st.success("User registered successfully")
    except Exception as e:
        st.error(f"Registration error: {e}")

    # Load data
    try:
        df = pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        st.error(f"Excel file not found: {EXCEL_FILE}")
        st.stop()
    except Exception as e:
        st.error(f"Failed to read Excel file: {e}")
        st.stop()

    # Validate expected columns
    if "Timestamp" not in df.columns:
        st.error("EXCEL file missing required column: 'Timestamp'.")
        st.stop()

    # Convert Timestamp column
    try:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    except Exception as e:
        st.error(f"Failed to parse 'Timestamp' column: {e}")
        st.stop()

    # Sidebar filters
    st.sidebar.header("Filters")
    try:
        start_date = st.sidebar.date_input("Start Date", df["Timestamp"].min().date())
        end_date = st.sidebar.date_input("End Date", df["Timestamp"].max().date())
    except Exception:
        # If Timestamp min/max fail for empty df
        start_date = st.sidebar.date_input("Start Date", datetime.today().date())
        end_date = st.sidebar.date_input("End Date", datetime.today().date())

    weather_filter = st.sidebar.checkbox("Show weather-based notes only")

    # Filter dataframe by date range
    filtered_df = df[
        (df["Timestamp"].dt.date >= start_date) & (df["Timestamp"].dt.date <= end_date)
    ]

    if weather_filter:
        if "Notes" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Notes"].str.contains("Rain|UV", na=False)]
        else:
            st.warning("Notes column not present to filter by weather.")

    # Dashboard content
    st.title("💧 Deep Blue Pool Chemistry Dashboard")
    st.subheader("Recent Entries")
    st.dataframe(filtered_df.tail(10))

    metric_cols = [c for c in ["pH", "Chlorine"] if c in filtered_df.columns]
    if metric_cols:
        st.subheader("pH and Chlorine Trends")
        st.line_chart(filtered_df.set_index("Timestamp")[metric_cols])
    else:
        st.info("pH and Chlorine columns not present to plot trends.")

    st.sidebar.markdown("---")
    st.sidebar.caption("Weather-based dosing recommendations are shown in the Notes column.")

elif authentication_status is False:
    st.error("Invalid username or password.")
elif authentication_status is None:
    st.warning("Please enter your credentials.")
else:
    st.warning("Authentication state unknown. Check logs and credentials.")
