import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import random
import sqlite3
from datetime import datetime, timedelta
from textblob import TextBlob
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors as rl_colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import io
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════
# 🎨 LOGO CONFIGURATION
# ═══════════════════════════════════════════════════════════════
LOGO_PATH = "logo.png"

st.set_page_config(page_title="MindTrack | Wellness Intelligence", page_icon="🧠", layout="wide")

# ═══════════════════════════════════════════════════════════════
# 🌗 DARK MODE: COLOR SYSTEM
# ═══════════════════════════════════════════════════════════════
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Light mode colors
COLOR_INK_L = "#1B2430"
COLOR_MUTED_L = "#5B6B6A"
COLOR_BG_L = "#F4F6F5"
COLOR_CARD_L = "#FFFFFF"
COLOR_BORDER_L = "rgba(27,36,48,0.10)"

# Dark mode colors
COLOR_INK_D = "#E8ECF1"
COLOR_MUTED_D = "#8B95A5"
COLOR_BG_D = "#0D1117"
COLOR_CARD_D = "#161B22"
COLOR_BORDER_D = "rgba(255,255,255,0.08)"

# Dynamic colors based on mode
COLOR_INK = COLOR_INK_D if st.session_state.dark_mode else COLOR_INK_L
COLOR_MUTED = COLOR_MUTED_D if st.session_state.dark_mode else COLOR_MUTED_L
COLOR_BG = COLOR_BG_D if st.session_state.dark_mode else COLOR_BG_L
COLOR_CARD = COLOR_CARD_D if st.session_state.dark_mode else COLOR_CARD_L
COLOR_BORDER = COLOR_BORDER_D if st.session_state.dark_mode else COLOR_BORDER_L

COLOR_PRIMARY = "#2F6F62"
COLOR_PRIMARY_LIGHT = "#4C9A79"
COLOR_SLATE = "#5C7A8A"
COLOR_GOOD = "#4C9A79"
COLOR_MEDIUM = "#D9A441"
COLOR_HIGH = "#C1554A"
COLOR_SOCIAL = "#7B68EE"
COLOR_SCREEN = "#FF6B6B"
COLOR_CAFFEINE = "#8B6914"
COLOR_WATER = "#4A90D9"
COLOR_SUNLIGHT = "#F4A460"
COLOR_WORKLIFE = "#9B59B6"

CHART_PALETTE = [COLOR_PRIMARY, COLOR_MEDIUM, COLOR_HIGH, COLOR_SLATE, COLOR_PRIMARY_LIGHT, "#8B5E3C", COLOR_SOCIAL, COLOR_SCREEN, COLOR_CAFFEINE, COLOR_WATER, COLOR_SUNLIGHT, COLOR_WORKLIFE]
RISK_COLOR_MAP = {"Low": COLOR_GOOD, "Medium": COLOR_MEDIUM, "High": COLOR_HIGH}

# ═══════════════════════════════════════════════════════════════
# 🌗 DARK MODE: DYNAMIC CSS
# ═══════════════════════════════════════════════════════════════
sidebar_bg = "#1B2430" if not st.session_state.dark_mode else "#0D1117"
sidebar_text = "#EDEFEE" if not st.session_state.dark_mode else "#C9D1D9"
sidebar_border = "rgba(255,255,255,0.06)" if not st.session_state.dark_mode else "rgba(255,255,255,0.08)"
radio_bg = "rgba(255,255,255,0.035)" if not st.session_state.dark_mode else "rgba(255,255,255,0.05)"
radio_hover = "rgba(255,255,255,0.09)" if not st.session_state.dark_mode else "rgba(255,255,255,0.12)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {{
    --ink: {COLOR_INK}; --muted: {COLOR_MUTED}; --paper: {COLOR_BG}; --card: {COLOR_CARD};
    --border: {COLOR_BORDER}; --primary: {COLOR_PRIMARY}; --primary-light: {COLOR_PRIMARY_LIGHT};
    --good: {COLOR_GOOD}; --medium: {COLOR_MEDIUM}; --high: {COLOR_HIGH};
}}

html, body, [class*="css"] {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}
.stApp {{ background: var(--paper); }}
.main .block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1200px; }}

h1, h2, h3 {{
    font-family: 'Fraunces', Georgia, serif !important; color: var(--ink) !important;
    font-weight: 600 !important; letter-spacing: -0.01em;
}}
.stMarkdown, .stMarkdown p, label, .stCaption {{ color: var(--muted) !important; }}

[data-testid="stSidebar"] {{ 
    background: {sidebar_bg}; 
    border-right: 1px solid {sidebar_border}; 
}}
[data-testid="stSidebar"] * {{ color: {sidebar_text} !important; }}
.sidebar-brand {{
    font-family: 'Fraunces', serif; font-size: 1.55rem; font-weight: 700; color: #fff !important;
    margin: 0.2rem 0 0.1rem 0; display: flex; align-items: center; gap: 8px;
}}
.sidebar-tagline {{
    font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--primary-light) !important; margin-bottom: 1.5rem;
}}
[data-testid="stSidebar"] div[role="radiogroup"] label {{
    background: {radio_bg}; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 9px 14px; margin-bottom: 6px; transition: all 0.15s ease;
}}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
    background: {radio_hover}; border-color: var(--primary-light);
}}
.sidebar-disclaimer {{
    font-size: 0.68rem !important; color: rgba(237,239,238,0.55) !important;
    margin-top: 16px; line-height: 1.45; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.08);
}}

.dark-toggle {{
    display: inline-flex; align-items: center; gap: 8px;
    background: {radio_bg}; border: 1px solid rgba(255,255,255,0.15);
    border-radius: 999px; padding: 6px 14px; cursor: pointer;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem;
    color: {sidebar_text} !important; margin-bottom: 12px;
    transition: all 0.2s ease;
}}
.dark-toggle:hover {{
    background: {radio_hover}; border-color: var(--primary-light);
}}

.page-header {{ display: flex; align-items: flex-start; gap: 16px; margin-bottom: 0.2rem; }}
.page-header-icon {{ font-size: 2.2rem; line-height: 1; margin-top: 2px; }}
.page-eyebrow {{
    font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--primary); font-weight: 600; margin-bottom: 2px;
}}
.page-title {{ margin: 0 !important; font-size: 2.05rem !important; }}
.page-subtitle {{ color: var(--muted) !important; font-size: 1rem; margin-top: 4px !important; }}
.pulse-divider {{ color: var(--primary); opacity: 0.55; height: 18px; margin: 1.2rem 0 1.6rem 0; }}
.pulse-divider svg {{ width: 100%; height: 100%; display: block; }}

.hero-wrap {{ text-align: center; padding: 2.6rem 0 1.6rem 0; }}
.hero-icon {{ font-size: 3.2rem; }}
.hero-title {{ font-family: 'Fraunces', serif; font-size: 2.6rem; margin: 0.25rem 0 0.35rem 0; color: var(--ink); font-weight: 700; }}
.hero-tagline {{
    font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.10em; text-transform: uppercase;
    font-size: 0.82rem; color: var(--primary); font-weight: 600;
}}

[data-testid="stMetric"] {{
    background: var(--card); border: 1px solid var(--border); border-radius: 12px;
    padding: 16px 18px; box-shadow: 0 1px 3px rgba(27,36,48,0.05);
}}
[data-testid="stMetricLabel"] {{
    font-family: 'IBM Plex Mono', monospace !important; text-transform: uppercase;
    font-size: 0.70rem !important; letter-spacing: 0.06em; color: var(--muted) !important;
}}
[data-testid="stMetricValue"] {{ font-family: 'Fraunces', serif !important; color: var(--ink) !important; }}
.feature-card {{
    background: var(--card); border: 1px solid var(--border); border-radius: 12px;
    padding: 22px; box-shadow: 0 1px 3px rgba(27,36,48,0.05);
}}

.stButton > button {{
    background: var(--primary); color: #fff; border: none; border-radius: 8px;
    padding: 11px 22px; font-weight: 600; font-family: 'Inter', sans-serif;
    box-shadow: 0 1px 2px rgba(27,36,48,0.12); transition: all 0.15s ease;
}}
.stButton > button:hover {{ background: var(--primary-light); transform: translateY(-1px); box-shadow: 0 4px 10px rgba(47,111,98,0.25); }}
.stDownloadButton > button {{
    background: var(--card) !important; color: var(--primary) !important; 
    border: 1.5px solid var(--primary) !important; border-radius: 8px; font-weight: 600;
}}
.stDownloadButton > button:hover {{ 
    background: var(--primary) !important; color: #fff !important; 
}}

div[data-testid="stAlert"] {{ border-radius: 10px; border: 1px solid var(--border); }}
button[data-baseweb="tab"] {{ font-family: 'Inter', sans-serif; font-weight: 600; color: var(--muted); }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: var(--primary); }}
[data-testid="stSlider"] [role="slider"] {{ background-color: var(--primary) !important; }}
hr {{ display: none; }}

.streak-badge {{
    display: inline-flex; align-items: center; gap: 6px; background: rgba(217,164,65,0.12);
    border: 1px solid rgba(217,164,65,0.35); color: var(--medium) !important; border-radius: 999px;
    padding: 4px 14px; font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem; font-weight: 600;
}}

.breathing-circle-wrap {{ display: flex; justify-content: center; padding: 1.8rem 0; }}
.breathing-circle {{
    width: 140px; height: 140px; border-radius: 50%;
    background: radial-gradient(circle, var(--primary-light), var(--primary));
    animation: breathe 16s ease-in-out infinite;
    box-shadow: 0 0 40px rgba(47,111,98,0.35);
}}
@keyframes breathe {{
    0%   {{ transform: scale(0.7);  opacity: 0.8; }}
    25%  {{ transform: scale(1.15); opacity: 1;   }}
    50%  {{ transform: scale(1.15); opacity: 1;   }}
    75%  {{ transform: scale(0.7);  opacity: 0.8; }}
    100% {{ transform: scale(0.7);  opacity: 0.8; }}
}}

.entry-row {{
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    padding: 10px 16px; margin-bottom: 8px;
}}

.login-box {{
    max-width: 400px; margin: 2rem auto; padding: 2rem;
    background: var(--card); border: 1px solid var(--border);
    border-radius: 14px; text-align: center;
}}
.login-icon {{ font-size: 3rem; margin-bottom: 0.5rem; }}
.login-title {{
    font-family: 'Fraunces', serif; font-size: 1.6rem;
    color: var(--ink); margin-bottom: 0.3rem;
}}
.login-sub {{
    color: var(--muted); font-size: 0.9rem; margin-bottom: 1.5rem;
}}
.user-pill {{
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(47,111,98,0.10); border: 1px solid rgba(47,111,98,0.25);
    color: var(--primary); border-radius: 999px;
    padding: 5px 14px; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem; font-weight: 600;
}}
.lock-screen {{
    text-align: center; padding: 3rem 1rem;
}}
.lock-screen h2 {{
    font-family: 'Fraunces', serif; color: var(--ink);
}}

[data-testid="stDataFrame"] {{
    background: var(--card) !important;
}}
[data-testid="stDataFrame"] td {{
    color: var(--ink) !important;
}}
[data-testid="stDataFrame"] th {{
    color: var(--ink) !important;
    background: var(--paper) !important;
}}

input, textarea, .stTextInput > div > div > input {{
    background: var(--card) !important;
    color: var(--ink) !important;
    border: 1px solid var(--border) !important;
}}
.stTextArea textarea {{
    background: var(--card) !important;
    color: var(--ink) !important;
    border: 1px solid var(--border) !important;
}}

.stSlider > div > div > div {{
    color: var(--ink) !important;
}}
</style>
""", unsafe_allow_html=True)


def pulse_divider():
    st.markdown("""
    <div class="pulse-divider">
        <svg viewBox="0 0 400 24" preserveAspectRatio="none">
            <polyline points="0,12 150,12 165,2 180,22 195,4 210,12 400,12"
                      fill="none" stroke="currentColor" stroke-width="2"
                      stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </div>
    """, unsafe_allow_html=True)


def page_header(icon, eyebrow, title, subtitle=None):
    st.markdown(f"""
    <div class="page-header">
        <div class="page-header-icon">{icon}</div>
        <div>
            <div class="page-eyebrow">{eyebrow}</div>
            <h1 class="page-title">{title}</h1>
            {f'<p class="page-subtitle">{subtitle}</p>' if subtitle else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)
    pulse_divider()


DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "mental_health.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT, date TEXT, mood TEXT, sleep_hours REAL,
                stress_level REAL, anxiety_level REAL, exercise_minutes REAL,
                social_connection REAL, screen_time REAL, caffeine_intake REAL,
                water_intake REAL, sunlight_exposure REAL, work_life_balance REAL
            )
        """)
        new_cols = [
            ("social_connection", "REAL"),
            ("screen_time", "REAL"),
            ("caffeine_intake", "REAL"),
            ("water_intake", "REAL"),
            ("sunlight_exposure", "REAL"),
            ("work_life_balance", "REAL"),
        ]
        for col_name, col_type in new_cols:
            try:
                cur.execute(f"ALTER TABLE user_history ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass
        cur.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT, date TEXT, risk_level TEXT, wellness_score REAL, factors TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                username TEXT PRIMARY KEY,
                target_sleep REAL, target_exercise REAL, target_stress_max REAL,
                target_social REAL, target_screen_max REAL, target_water REAL,
                target_sunlight REAL, target_worklife REAL, updated_at TEXT
            )
        """)
        new_goal_cols = [
            ("target_social", "REAL"),
            ("target_screen_max", "REAL"),
            ("target_water", "REAL"),
            ("target_sunlight", "REAL"),
            ("target_worklife", "REAL"),
        ]
        for col_name, col_type in new_goal_cols:
            try:
                cur.execute(f"ALTER TABLE goals ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        raise


def save_user_history(username, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes,
                      social_connection, screen_time, caffeine_intake, water_intake,
                      sunlight_exposure, work_life_balance, entry_date=None):
    try:
        init_db()
        if entry_date is None:
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            date_str = datetime.combine(entry_date, datetime.now().time()).strftime("%Y-%m-%d %H:%M:%S")

        conn = get_connection()
        conn.execute(
            """INSERT INTO user_history
               (username, date, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes,
                social_connection, screen_time, caffeine_intake, water_intake,
                sunlight_exposure, work_life_balance)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (username, date_str, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes,
             social_connection, screen_time, caffeine_intake, water_intake,
             sunlight_exposure, work_life_balance),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving assessment: {e}")
        return False


def save_prediction(username, risk_level, wellness_score, factors):
    try:
        init_db()
        conn = get_connection()
        conn.execute(
            """INSERT INTO predictions (username, date, risk_level, wellness_score, factors)
               VALUES (?, ?, ?, ?, ?)""",
            (username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), risk_level, wellness_score, str(factors)),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving prediction: {e}")
        return False


def save_goals(username, target_sleep, target_exercise, target_stress_max,
               target_social, target_screen_max, target_water, target_sunlight, target_worklife):
    try:
        init_db()
        conn = get_connection()
        conn.execute(
            """INSERT INTO goals (username, target_sleep, target_exercise, target_stress_max,
                 target_social, target_screen_max, target_water, target_sunlight, target_worklife, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(username) DO UPDATE SET
                 target_sleep=excluded.target_sleep,
                 target_exercise=excluded.target_exercise,
                 target_stress_max=excluded.target_stress_max,
                 target_social=excluded.target_social,
                 target_screen_max=excluded.target_screen_max,
                 target_water=excluded.target_water,
                 target_sunlight=excluded.target_sunlight,
                 target_worklife=excluded.target_worklife,
                 updated_at=excluded.updated_at""",
            (username, target_sleep, target_exercise, target_stress_max,
             target_social, target_screen_max, target_water, target_sunlight, target_worklife,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving goals: {e}")
        return False


def get_goals(username):
    try:
        init_db()
        conn = get_connection()
        row = conn.execute("SELECT * FROM goals WHERE username=?", (username,)).fetchone()
        conn.close()
        # FIX: Properly handle sqlite3.Row object
        if row is not None:
            return dict(row)
        return None
    except Exception as e:
        st.error(f"Error loading goals: {e}")
        return None
# JOURNAL FUNCTIONS
JOURNAL_CSV = os.path.join(DATA_DIR, "journal_entries.csv")

def save_journal_entry(username, text, sentiment, polarity):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "username": username,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "text": text,
            "sentiment": sentiment,
            "polarity": round(polarity, 4),
        }
        df_new = pd.DataFrame([entry])
        if os.path.exists(JOURNAL_CSV):
            df_existing = pd.read_csv(JOURNAL_CSV)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        df_combined.to_csv(JOURNAL_CSV, index=False)
        return entry
    except Exception as e:
        st.error(f"Error saving journal: {e}")
        return None

def get_journal_entries(username=None):
    try:
        if not os.path.exists(JOURNAL_CSV):
            return pd.DataFrame(columns=["id", "username", "date", "text", "sentiment", "polarity"])
        df = pd.read_csv(JOURNAL_CSV)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        if username:
            df = df[df["username"].astype(str) == str(username)]
        return df.sort_values("date", ascending=False).reset_index(drop=True)
    except Exception as e:
        st.error(f"Error reading journals: {e}")
        return pd.DataFrame(columns=["id", "username", "date", "text", "sentiment", "polarity"])

def delete_journal_entry(entry_id):
    try:
        if not os.path.exists(JOURNAL_CSV):
            return
        df = pd.read_csv(JOURNAL_CSV)
        df = df[df["id"].astype(str) != str(entry_id)]
        df.to_csv(JOURNAL_CSV, index=False)
    except Exception as e:
        st.error(f"Error deleting journal: {e}")

def delete_all_journal_entries(username):
    try:
        if not os.path.exists(JOURNAL_CSV):
            return
        df = pd.read_csv(JOURNAL_CSV)
        df = df[df["username"].astype(str) != str(username)]
        df.to_csv(JOURNAL_CSV, index=False)
    except Exception as e:
        st.error(f"Error clearing journals: {e}")

def export_journal_to_excel(username=None):
    df = get_journal_entries(username)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Journal Entries")
    buffer.seek(0)
    return buffer


# LOGIN FUNCTIONS
def init_login_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None

def login_user(username):
    st.session_state.logged_in = True
    st.session_state.current_user = username.strip()

def logout_user():
    st.session_state.logged_in = False
    st.session_state.current_user = None

def require_login():
    init_login_state()
    if not st.session_state.logged_in:
        st.markdown("""
        <div class="lock-screen">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔒</div>
            <h2>Please Sign In</h2>
            <p>You need to sign in to access this page.</p>
            <p>Go to <b>Home</b> to sign in.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

def show_login_page():
    init_login_state()
    st.markdown("""
    <div class="login-box">
        <div class="login-icon">🧠</div>
        <div class="login-title">MindTrack</div>
        <div class="login-sub">Sign in to access your wellness dashboard</div>
    </div>
    """, unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("Your name", placeholder="Enter your name", key="login_username_input")
        submitted = st.form_submit_button("Sign In", use_container_width=True)
        if submitted:
            if username and username.strip():
                login_user(username)
                st.success(f"Welcome, {username.strip()}! 🎉")
                st.rerun()
            else:
                st.error("Please enter your name.")

def show_user_badge():
    if st.session_state.get("logged_in") and st.session_state.get("current_user"):
        st.sidebar.markdown(f"""
        <div style="margin-bottom: 10px;">
            <span class="user-pill">👤 {st.session_state.current_user}</span>
        </div>
        """, unsafe_allow_html=True)
        if st.sidebar.button("🚪 Log out", use_container_width=True, key="logout_btn"):
            logout_user()
            st.rerun()
        st.sidebar.markdown("---")

def delete_entry(entry_id):
    try:
        conn = get_connection()
        conn.execute("DELETE FROM user_history WHERE id=?", (int(entry_id),))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error deleting entry: {e}")


def delete_all_entries(username):
    try:
        conn = get_connection()
        conn.execute("DELETE FROM user_history WHERE username=?", (username,))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error clearing entries: {e}")


# ═══════════════════════════════════════════════════════════════
# WELLNESS CALCULATIONS
# ═══════════════════════════════════════════════════════════════

def calculate_wellness_score(stress, sleep, anxiety, exercise, social_connection, screen_time,
                             caffeine_intake, water_intake, sunlight_exposure, work_life_balance):
    score = 0
    score += (10 - stress) * 4
    score += min(sleep, 10) * 3
    score += (10 - anxiety) * 4
    score += min(exercise, 120) / 2
    score += social_connection * 2
    score += max(0, (8 - screen_time)) * 2
    score += min(caffeine_intake, 3) * 2
    score += min(water_intake, 10) * 1.5
    score += min(sunlight_exposure, 120) / 15
    score += work_life_balance * 2
    return min(score, 100)

def predict_risk(stress, sleep, anxiety, exercise, mood, social_connection, screen_time,
                 caffeine_intake, water_intake, sunlight_exposure, work_life_balance):
    wellness_score = calculate_wellness_score(stress, sleep, anxiety, exercise, social_connection,
                                               screen_time, caffeine_intake, water_intake,
                                               sunlight_exposure, work_life_balance)
    if wellness_score < 40:
        risk = "High"
    elif wellness_score < 70:
        risk = "Medium"
    else:
        risk = "Low"
    factors = []
    if stress > 7:
        factors.append("High stress levels")
    if sleep < 6:
        factors.append("Insufficient sleep")
    if anxiety > 7:
        factors.append("High anxiety levels")
    if exercise < 30:
        factors.append("Low physical activity")
    if social_connection < 4:
        factors.append("Low social connection")
    if screen_time > 8:
        factors.append("Excessive screen time")
    if caffeine_intake > 5:
        factors.append("High caffeine intake")
    if water_intake < 4:
        factors.append("Low hydration")
    if sunlight_exposure < 15:
        factors.append("Insufficient sunlight exposure")
    if work_life_balance < 4:
        factors.append("Poor work-life balance")
    if not factors:
        factors = ["Good overall wellness indicators"]
    return risk, factors, wellness_score

def get_recommendations(stress, sleep, anxiety, exercise, social_connection, screen_time,
                        caffeine_intake, water_intake, sunlight_exposure, work_life_balance):
    recommendations = []
    if stress > 7:
        recommendations.append("🧘 Try deep breathing exercises for 5 minutes daily")
        recommendations.append("🧘‍♂️ Practice mindfulness meditation")
        recommendations.append("☕ Take short breaks throughout your work/study")
    if sleep < 6:
        recommendations.append("🛏️ Establish a consistent sleep schedule")
        recommendations.append("📵 Avoid screens 1 hour before bedtime")
        recommendations.append("🌙 Create a relaxing bedtime routine")
    if anxiety > 7:
        recommendations.append("🧘 Try progressive muscle relaxation")
        recommendations.append("📝 Consider journaling your thoughts")
        recommendations.append("🌱 Practice grounding techniques")
    if exercise < 30:
        recommendations.append("🚶 Aim for 30 minutes of daily walking")
        recommendations.append("🧘 Try yoga or stretching exercises")
        recommendations.append("🏃 Incorporate physical activity into your routine")
    if social_connection < 4:
        recommendations.append("👥 Reach out to a friend or family member")
        recommendations.append("🤝 Join a community group or club")
        recommendations.append("📞 Schedule regular check-ins with loved ones")
    if screen_time > 8:
        recommendations.append("📵 Set screen time limits on your devices")
        recommendations.append("🌳 Take regular breaks from screens")
        recommendations.append("📖 Try reading a physical book instead of scrolling")
    if caffeine_intake > 5:
        recommendations.append("☕ Reduce caffeine intake gradually")
        recommendations.append("🍵 Try herbal tea as an alternative")
        recommendations.append("⏰ Avoid caffeine after 2 PM")
    if water_intake < 4:
        recommendations.append("💧 Drink a glass of water every hour")
        recommendations.append("🍋 Add lemon to water for flavor")
        recommendations.append("📱 Use a hydration reminder app")
    if sunlight_exposure < 15:
        recommendations.append("☀️ Get 15-30 minutes of morning sunlight")
        recommendations.append("🚶 Take walks outside during lunch")
        recommendations.append("🪟 Open curtains and let natural light in")
    if work_life_balance < 4:
        recommendations.append("⏰ Set clear work boundaries")
        recommendations.append("🛑 Learn to say no to extra commitments")
        recommendations.append("🎨 Schedule time for hobbies and relaxation")
    if len(recommendations) == 0:
        recommendations.append("🎉 Great job! Keep maintaining your healthy habits!")
        recommendations.append("✅ Continue with your current wellness routine")
        recommendations.append("🎨 Consider exploring new hobbies")
    return recommendations

def analyze_sentiment(text):
    if not text or len(text.strip()) == 0:
        return "neutral", 0.0
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        sentiment = "positive"
    elif polarity < -0.1:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return sentiment, polarity

def generate_pdf_report(username, risk_level, wellness_score, factors, recommendations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    brand_color = rl_colors.HexColor(COLOR_PRIMARY)
    ink_color = rl_colors.HexColor(COLOR_INK)
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=6,
                                  alignment=1, textColor=brand_color)
    story.append(Paragraph("MindTrack Wellness Report", title_style))
    eyebrow_style = ParagraphStyle('Eyebrow', parent=styles['Normal'], fontSize=10, alignment=1,
                                    textColor=rl_colors.HexColor(COLOR_MUTED), spaceAfter=24)
    story.append(Paragraph("MENTAL HEALTH RISK ANALYSIS", eyebrow_style))
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Heading2'], fontSize=14, spaceAfter=16,
                                     textColor=ink_color)
    story.append(Paragraph(f"For: {username}", subtitle_style))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    info_style = ParagraphStyle('CustomInfo', parent=styles['Normal'], fontSize=12, spaceAfter=12, textColor=ink_color)
    story.append(Paragraph(f"Risk Level: {risk_level}", info_style))
    story.append(Paragraph(f"Wellness Score: {wellness_score}/100", info_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Key Factors:", subtitle_style))
    for factor in factors:
        story.append(Paragraph(f"- {factor}", info_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Recommendations:", subtitle_style))
    for rec in recommendations:
        story.append(Paragraph(f"- {rec}", info_style))
    story.append(Spacer(1, 24))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8,
                                   textColor=rl_colors.HexColor(COLOR_MUTED))
    story.append(Paragraph(
        "This report is a self-reflection summary, not a clinical diagnosis. "
        "If you are struggling, please consider speaking with a licensed professional.", footer_style))
    doc.build(story)
    buffer.seek(0)
    return buffer

def export_to_excel(df, sheet_name="Data"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    buffer.seek(0)
    return buffer

def mood_to_score(series):
    mood_map = {"Very Bad": 1, "Bad": 2, "Neutral": 3, "Good": 4, "Very Good": 5}
    return series.map(mood_map)

def get_history_data():
    try:
        init_db()
        conn = get_connection()
        try:
            df = pd.read_sql_query("SELECT * FROM user_history", conn)
        except Exception:
            return pd.DataFrame()
        finally:
            conn.close()
        if df.empty:
            return df
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["mood_num"] = mood_to_score(df["mood"])
        df["wellness_score"] = df.apply(
            lambda row: calculate_wellness_score(
                row["stress_level"], row["sleep_hours"], row["anxiety_level"], row["exercise_minutes"],
                row.get("social_connection", 5), row.get("screen_time", 4),
                row.get("caffeine_intake", 2), row.get("water_intake", 6),
                row.get("sunlight_exposure", 30), row.get("work_life_balance", 5)
            ),
            axis=1,
        )
        return df.dropna(subset=["date"])
    except Exception as e:
        st.error(f"Error loading history: {e}")
        return pd.DataFrame()

def get_prediction_data():
    try:
        init_db()
        conn = get_connection()
        try:
            df = pd.read_sql_query("SELECT * FROM predictions", conn)
        except Exception:
            return pd.DataFrame()
        finally:
            conn.close()
        if df.empty:
            return df
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        # FIX: Handle empty dataframe properly
        if len(df) == 0:
            return df
        risk_map = {"Low": 1, "Medium": 2, "High": 3}
        df["risk_num"] = df["risk_level"].map(risk_map)
        return df.dropna(subset=["date"])
    except Exception as e:
        st.error(f"Error loading predictions: {e}")
        return pd.DataFrame()
# ═══════════════════════════════════════════════════════════════
# VISUALIZATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def style_plot(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(27,36,48,0.02)" if not st.session_state.dark_mode else "rgba(0,0,0,0)",
        font={"color": COLOR_INK, "family": "Inter, sans-serif"},
        title_font={"family": "Fraunces, serif", "color": COLOR_INK, "size": 17},
        margin=dict(l=20, r=20, t=50, b=20),
        legend={"font": {"color": COLOR_MUTED}},
    )
    fig.update_xaxes(gridcolor="rgba(27,36,48,0.07)" if not st.session_state.dark_mode else "rgba(255,255,255,0.06)", color=COLOR_MUTED)
    fig.update_yaxes(gridcolor="rgba(27,36,48,0.07)" if not st.session_state.dark_mode else "rgba(255,255,255,0.06)", color=COLOR_MUTED)
    return fig

def create_wellness_radar(sleep, stress, anxiety, exercise, mood, social_connection, screen_time,
                          caffeine_intake, water_intake, sunlight_exposure, work_life_balance):
    mood_scale = {"Very Bad": 2, "Bad": 4, "Neutral": 6, "Good": 8, "Very Good": 10}
    categories = ["Sleep", "Exercise", "Mood", "Stress Balance", "Anxiety Balance",
                  "Social", "Screen Balance", "Caffeine", "Hydration", "Sunlight", "Work-Life"]
    values = [
        min(float(sleep), 10), min(float(exercise) / 12, 10), mood_scale.get(mood, 6),
        10 - float(stress), 10 - float(anxiety),
        float(social_connection), max(0, 10 - float(screen_time)),
        max(0, 10 - float(caffeine_intake) * 1.5), min(float(water_intake), 10),
        min(float(sunlight_exposure) / 15, 10), float(work_life_balance)
    ]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]], theta=categories + [categories[0]], fill="toself",
        name="Wellness Profile", line_color=COLOR_PRIMARY, fillcolor="rgba(47,111,98,0.20)",
    ))
    fig.update_layout(
        title="Wellness Profile (11 Dimensions)",
        polar=dict(bgcolor="rgba(0,0,0,0)",
                   radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(color=COLOR_MUTED)),
                   angularaxis=dict(tickfont=dict(color=COLOR_INK))),
        showlegend=False,
    )
    return style_plot(fig)

def create_factor_bar(stress, sleep, anxiety, exercise, social_connection, screen_time,
                      caffeine_intake, water_intake, sunlight_exposure, work_life_balance):
    categories = ["Stress", "Sleep", "Anxiety", "Exercise", "Social", "Screen", "Caffeine", "Water", "Sunlight", "Work-Life"]
    actual_values = [stress, sleep, anxiety, exercise, social_connection, screen_time,
                     caffeine_intake, water_intake, sunlight_exposure, work_life_balance]
    healthy_targets = [3, 8, 3, 45, 7, 4, 2, 8, 30, 7]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Your Values", x=categories, y=actual_values,
                         marker_color=[COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_PRIMARY, COLOR_PRIMARY_LIGHT,
                                       COLOR_SOCIAL, COLOR_SCREEN, COLOR_CAFFEINE, COLOR_WATER,
                                       COLOR_SUNLIGHT, COLOR_WORKLIFE]))
    fig.add_trace(go.Bar(name="Healthy Target", x=categories, y=healthy_targets, marker_color=COLOR_SLATE))
    fig.update_layout(barmode="group", title="Your Wellness Factors vs Healthy Targets")
    return style_plot(fig)

def create_extended_factor_bar(stress, sleep, anxiety, exercise, social_connection, screen_time,
                               caffeine_intake, water_intake, sunlight_exposure, work_life_balance):
    categories = ["Stress\n(lower=better)", "Sleep\n(hours)", "Anxiety\n(lower=better)", "Exercise\n(min)",
                  "Social\n(0-10)", "Screen\n(hours)", "Caffeine\n(cups)", "Water\n(glasses)",
                  "Sunlight\n(min)", "Work-Life\n(0-10)"]
    actual_values = [stress, sleep, anxiety, exercise, social_connection, screen_time,
                     caffeine_intake, water_intake, sunlight_exposure, work_life_balance]
    healthy_targets = [3, 8, 3, 45, 7, 4, 2, 8, 30, 7]

    colors = []
    for i, (val, target) in enumerate(zip(actual_values, healthy_targets)):
        if i in [0, 2, 5, 6]:
            if val <= target:
                colors.append(COLOR_GOOD)
            elif val <= target * 1.5:
                colors.append(COLOR_MEDIUM)
            else:
                colors.append(COLOR_HIGH)
        else:
            if val >= target:
                colors.append(COLOR_GOOD)
            elif val >= target * 0.6:
                colors.append(COLOR_MEDIUM)
            else:
                colors.append(COLOR_HIGH)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Your Values", x=categories, y=actual_values, marker_color=colors))
    fig.add_trace(go.Bar(name="Healthy Target", x=categories, y=healthy_targets,
                         marker_color="rgba(92,122,138,0.3)", marker_line_color=COLOR_SLATE,
                         marker_line_width=2))
    fig.update_layout(barmode="group", title="Wellness Factors — Color-Coded Health Status",
                      bargap=0.25)
    return style_plot(fig)

def gauge_figure(value, title, value_range=(0, 100), steps=None):
    if steps is None:
        lo, hi = value_range
        span = hi - lo
        steps = [
            {'range': [lo, lo + span * 0.4], 'color': COLOR_HIGH},
            {'range': [lo + span * 0.4, lo + span * 0.7], 'color': COLOR_MEDIUM},
            {'range': [lo + span * 0.7, hi], 'color': COLOR_GOOD},
        ]
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value, domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20, 'color': COLOR_INK, 'family': 'Fraunces, serif'}},
        number={'font': {'color': COLOR_INK, 'family': 'IBM Plex Mono, monospace'}},
        gauge={'axis': {'range': list(value_range), 'tickwidth': 1, 'tickcolor': COLOR_MUTED},
               'bar': {'color': COLOR_PRIMARY}, 'bgcolor': "rgba(0,0,0,0)",
               'borderwidth': 1, 'bordercolor': COLOR_BORDER, 'steps': steps}
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': COLOR_INK})
    return fig

def risk_badge(risk):
    if risk == "Low":
        st.success(f"🎯 Risk Level: **{risk}**")
    elif risk == "Medium":
        st.warning(f"⚠️ Risk Level: **{risk}**")
    else:
        st.error(f"🚨 Risk Level: **{risk}**")

def calculate_streaks(entry_dates):
    if not entry_dates:
        return 0, 0
    dates = sorted(set(entry_dates))
    longest = 1
    current_run = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            current_run += 1
        else:
            current_run = 1
        longest = max(longest, current_run)

    today = datetime.now().date()
    if (today - dates[-1]).days > 1:
        current_streak = 0
    else:
        current_streak = 1
        idx = len(dates) - 1
        while idx > 0 and (dates[idx] - dates[idx - 1]).days == 1:
            current_streak += 1
            idx -= 1
    return current_streak, longest

def weekly_digest(df):
    today = datetime.now().date()
    this_week = df[df["date"].dt.date >= today - timedelta(days=6)]
    last_week = df[(df["date"].dt.date >= today - timedelta(days=13)) &
                   (df["date"].dt.date <= today - timedelta(days=7))]
    this_avg = this_week["wellness_score"].mean() if not this_week.empty else None
    last_avg = last_week["wellness_score"].mean() if not last_week.empty else None
    return this_avg, last_avg

def trend_nudge(df):
    d = df.sort_values("date")
    if len(d) < 3:
        return False
    recent = d.tail(3)["wellness_score"].tolist()
    return recent[0] > recent[1] > recent[2] and recent[2] < 40

def create_mood_calendar(df, weeks=12):
    today = datetime.now().date()
    start = today - timedelta(days=weeks * 7 - 1)
    daily = df.copy()
    daily["day"] = daily["date"].dt.date
    daily_avg = daily.groupby("day")["mood_num"].mean()

    weekday_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    matrix = np.full((7, weeks), np.nan)
    hovertext = np.empty((7, weeks), dtype=object)
    hovertext[:] = ""

    for offset in range(weeks * 7):
        day = start + timedelta(days=offset)
        if day > today:
            break
        week_idx = offset // 7
        weekday_idx = day.weekday()
        if week_idx >= weeks:
            continue
        val = daily_avg.get(day, np.nan)
        matrix[weekday_idx, week_idx] = val
        label = f"{day.strftime('%Y-%m-%d')}<br>{'Mood: %.1f' % val if not np.isnan(val) else 'No entry'}"
        hovertext[weekday_idx, week_idx] = label

    fig = go.Figure(data=go.Heatmap(
        z=matrix, x=[f"W{i + 1}" for i in range(weeks)], y=weekday_labels,
        colorscale=[[0, COLOR_HIGH], [0.5, COLOR_MEDIUM], [1, COLOR_GOOD]],
        zmin=1, zmax=5, hoverinfo="text", text=hovertext,
        xgap=3, ygap=3, showscale=False,
    ))
    fig.update_layout(title=f"Mood Calendar — Last {weeks} Weeks")
    return style_plot(fig)

def create_lifestyle_heatmap(df):
    if df.empty or len(df) < 2:
        return None
    df_sorted = df.sort_values("date").tail(30)
    lifestyle_cols = ["social_connection", "screen_time", "caffeine_intake",
                      "water_intake", "sunlight_exposure", "work_life_balance"]
    available_cols = [c for c in lifestyle_cols if c in df_sorted.columns]
    if not available_cols:
        return None

    z_data = []
    for col in available_cols:
        vals = df_sorted[col].fillna(0).values
        if col in ["screen_time", "caffeine_intake"]:
            vals = np.clip(vals, 0, 10)
            vals = 10 - vals
        elif col == "sunlight_exposure":
            vals = np.clip(vals / 12, 0, 10)
        elif col == "water_intake":
            vals = np.clip(vals, 0, 10)
        else:
            vals = np.clip(vals, 0, 10)
        z_data.append(vals)

    labels = [c.replace("_", " ").title() for c in available_cols]
    dates = df_sorted["date"].dt.strftime("%m-%d").tolist()

    fig = go.Figure(data=go.Heatmap(
        z=z_data, x=dates, y=labels,
        colorscale=[[0, COLOR_HIGH], [0.5, COLOR_MEDIUM], [1, COLOR_GOOD]],
        zmin=0, zmax=10, hoverongaps=False,
        colorbar=dict(title=dict(text="Score", side="right"))
    ))
    fig.update_layout(title="Lifestyle Factor Patterns (Last 30 Days)",
                      xaxis_title="Date", yaxis_title="Factor")
    return style_plot(fig)

def create_multi_metric_trend(df):
    if df.empty or len(df) < 2:
        return None
    df_sorted = df.sort_values("date")

    fig = go.Figure()

    metrics = {
        "Sleep": ("sleep_hours", COLOR_PRIMARY_LIGHT, lambda x: np.clip(x, 0, 10)),
        "Stress Inv": ("stress_level", COLOR_HIGH, lambda x: 10 - np.clip(x, 0, 10)),
        "Anxiety Inv": ("anxiety_level", COLOR_MEDIUM, lambda x: 10 - np.clip(x, 0, 10)),
        "Exercise": ("exercise_minutes", COLOR_PRIMARY, lambda x: np.clip(x / 12, 0, 10)),
        "Social": ("social_connection", COLOR_SOCIAL, lambda x: np.clip(x, 0, 10)),
        "Screen Inv": ("screen_time", COLOR_SCREEN, lambda x: np.clip(10 - x, 0, 10)),
        "Caffeine Inv": ("caffeine_intake", COLOR_CAFFEINE, lambda x: np.clip(10 - x * 1.5, 0, 10)),
        "Hydration": ("water_intake", COLOR_WATER, lambda x: np.clip(x, 0, 10)),
        "Sunlight": ("sunlight_exposure", COLOR_SUNLIGHT, lambda x: np.clip(x / 12, 0, 10)),
        "Work-Life": ("work_life_balance", COLOR_WORKLIFE, lambda x: np.clip(x, 0, 10)),
    }

    for label, (col, color, transform) in metrics.items():
        if col in df_sorted.columns:
            fig.add_trace(go.Scatter(
                x=df_sorted["date"], y=transform(df_sorted[col]),
                mode="lines+markers", name=label, line=dict(color=color, width=2),
                hovertemplate="%{y:.1f}<extra>" + label + "</extra>"
            ))

    fig.update_layout(
        title="All Wellness Metrics Trend (Normalized 0-10)",
        yaxis_title="Normalized Score",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    return style_plot(fig)


# ═══════════════════════════════════════════════════════════════
# 🤖 AI WELLNESS INSIGHTS ENGINE
# ═══════════════════════════════════════════════════════════════

def detect_trends(df, window=5):
    """Calculate trend slopes for key metrics using linear regression."""
    if len(df) < 3 or not SKLEARN_AVAILABLE:
        return {}
    trends = {}
    metrics = ["wellness_score", "sleep_hours", "stress_level", "anxiety_level",
               "exercise_minutes", "social_connection", "screen_time",
               "water_intake", "sunlight_exposure", "work_life_balance"]
    df = df.sort_values("date").reset_index(drop=True)
    x = np.arange(len(df)).reshape(-1, 1)
    for metric in metrics:
        if metric in df.columns:
            y = df[metric].fillna(df[metric].median()).values
            if len(y) >= 3:
                model = LinearRegression().fit(x, y)
                trends[metric] = {
                    "slope": float(model.coef_[0]),
                    "direction": "improving" if model.coef_[0] > 0.05 else "declining" if model.coef_[0] < -0.05 else "stable",
                    "r2": float(model.score(x, y)),
                }
    return trends

def find_key_correlations(df):
    """Find the strongest correlations between wellness factors."""
    if len(df) < 5:
        return []
    corr_cols = ["sleep_hours", "stress_level", "anxiety_level", "exercise_minutes",
                 "social_connection", "screen_time", "caffeine_intake", "water_intake",
                 "sunlight_exposure", "work_life_balance", "wellness_score"]
    available = [c for c in corr_cols if c in df.columns]
    if len(available) < 2:
        return []
    corr_matrix = df[available].corr()
    pairs = []
    for i in range(len(available)):
        for j in range(i + 1, len(available)):
            val = corr_matrix.iloc[i, j]
            if abs(val) > 0.4 and available[i] != available[j]:
                pairs.append({
                    "factor_a": available[i],
                    "factor_b": available[j],
                    "correlation": round(val, 3),
                    "strength": "strong" if abs(val) > 0.7 else "moderate",
                    "direction": "positive" if val > 0 else "negative",
                })
    return sorted(pairs, key=lambda x: abs(x["correlation"]), reverse=True)[:5]

def detect_anomalies(df):
    """Detect recent outliers using Z-score analysis."""
    if len(df) < 5:
        return []
    df = df.sort_values("date").tail(7)
    anomalies = []
    metrics = ["stress_level", "anxiety_level", "sleep_hours", "wellness_score"]
    for metric in metrics:
        if metric in df.columns:
            vals = df[metric].values
            mean, std = np.mean(vals), np.std(vals)
            if std > 0:
                z_scores = [(v - mean) / std for v in vals]
                latest_z = z_scores[-1]
                if abs(latest_z) > 1.5:
                    anomalies.append({
                        "metric": metric,
                        "value": vals[-1],
                        "z_score": round(latest_z, 2),
                        "severity": "high" if abs(latest_z) > 2.5 else "moderate",
                        "direction": "spike" if latest_z > 0 else "drop",
                    })
    return anomalies

def predict_next_wellness(df):
    """Predict next wellness score using simple time-series regression."""
    if len(df) < 5 or not SKLEARN_AVAILABLE:
        return None
    df = df.sort_values("date").reset_index(drop=True)
    features = ["sleep_hours", "stress_level", "anxiety_level", "exercise_minutes",
                "social_connection", "screen_time", "caffeine_intake", "water_intake",
                "sunlight_exposure", "work_life_balance"]
    available = [c for c in features if c in df.columns]
    if len(available) < 3:
        return None
    X = df[available].fillna(df[available].median()).values
    y = df["wellness_score"].values
    if len(X) < 3:
        return None
    model = LinearRegression()
    model.fit(X, y)
    last_row = df[available].iloc[-1].fillna(df[available].median()).values.reshape(1, -1)
    prediction = model.predict(last_row)[0]
    return round(np.clip(prediction, 0, 100), 1)

def generate_smart_recommendations(df, trends, correlations, anomalies):
    """Generate context-aware, data-driven recommendations."""
    recs = []
    if not df.empty:
        latest = df.iloc[-1]
        if trends.get("wellness_score", {}).get("direction") == "declining":
            recs.append("📉 **Trend Alert:** Your wellness score has been declining. Consider reviewing your recent habits and making one small adjustment today.")
        if trends.get("sleep_hours", {}).get("direction") == "declining":
            recs.append("😴 **Sleep Recovery:** Your sleep duration is trending down. Try a consistent bedtime routine — your data shows better scores on days with 7+ hours.")
        if trends.get("stress_level", {}).get("direction") == "improving":
            recs.append("🎉 **Great Progress:** Your stress levels are improving! Keep doing what's working.")
        for corr in correlations:
            if corr["factor_a"] == "sleep_hours" and corr["factor_b"] == "stress_level" and corr["direction"] == "negative":
                recs.append(f"🔗 **Insight:** Your data shows a {corr['strength']} negative correlation between sleep and stress. Prioritizing sleep could directly lower your stress.")
            if corr["factor_a"] == "exercise_minutes" and corr["factor_b"] == "wellness_score" and corr["direction"] == "positive":
                recs.append(f"🔗 **Insight:** Exercise and wellness are {corr['strength']}ly linked in your history. Even 20 minutes helps!")
        for anomaly in anomalies:
            if anomaly["metric"] == "stress_level" and anomaly["direction"] == "spike":
                recs.append(f"⚠️ **Recent Spike:** Your stress jumped significantly (Z-score: {anomaly['z_score']}). Try the 4-7-8 breathing technique on the Support page.")
            if anomaly["metric"] == "sleep_hours" and anomaly["direction"] == "drop":
                recs.append(f"⚠️ **Sleep Drop:** Your recent sleep is below your personal average. Consider avoiding screens 1 hour before bed.")
    if not recs:
        recs.append("✅ Your wellness patterns look stable. Keep maintaining your healthy habits!")
    return recs

def generate_ai_narrative(df, username):
    """Generate a natural language summary of the user's wellness state."""
    if df.empty or len(df) < 2:
        return "Not enough data yet. Complete a few more assessments to unlock AI insights!"
    trends = detect_trends(df)
    correlations = find_key_correlations(df)
    anomalies = detect_anomalies(df)
    prediction = predict_next_wellness(df)
    paragraphs = []
    latest = df.iloc[-1]
    score = latest.get("wellness_score", 0)
    if score >= 80:
        paragraphs.append(f"Hi **{username}**, your overall wellness is looking strong at **{score:.0f}/100**. ")
    elif score >= 50:
        paragraphs.append(f"Hi **{username}**, your wellness score is **{score:.0f}/100** — there's room for improvement, and your data can guide the way. ")
    else:
        paragraphs.append(f"Hi **{username}**, your wellness score is **{score:.0f}/100**. Your data reveals specific areas to focus on — let's look at them. ")
    if trends:
        trend_parts = []
        improving = [k for k, v in trends.items() if v["direction"] == "improving" and k != "wellness_score"]
        declining = [k for k, v in trends.items() if v["direction"] == "declining" and k != "wellness_score"]
        if improving:
            trend_parts.append(f"**Improving:** {', '.join([k.replace('_', ' ').title() for k in improving[:2]])}.")
        if declining:
            trend_parts.append(f"**Declining:** {', '.join([k.replace('_', ' ').title() for k in declining[:2]])}.")
        if trend_parts:
            paragraphs.append("Recent trends: " + " ".join(trend_parts))
    if correlations:
        top = correlations[0]
        a = top["factor_a"].replace("_", " ").title()
        b = top["factor_b"].replace("_", " ").title()
        direction = "increase together" if top["direction"] == "positive" else "move in opposite directions"
        paragraphs.append(f"Your strongest pattern: **{a}** and **{b}** {direction} (correlation: {top['correlation']}). This is one of the most reliable signals in your data.")
    if prediction is not None:
        diff = prediction - score
        if abs(diff) > 5:
            direction = "improve to" if diff > 0 else "drop to"
            paragraphs.append(f"Based on your current trajectory, your next wellness score may **{direction} {prediction:.0f}/100**.")
    if anomalies:
        sev = anomalies[0]
        paragraphs.append(f"⚠️ **Attention needed:** Your recent {sev['metric'].replace('_', ' ')} shows a significant {sev['direction']} compared to your usual pattern.")
    return "\n\n".join(paragraphs)

def create_trend_visualization(df):
    """Create an AI trend prediction chart. FIX: Use proper numpy function."""
    if len(df) < 5 or not SKLEARN_AVAILABLE:
        return None
    df = df.sort_values("date").reset_index(drop=True)
    features = ["sleep_hours", "stress_level", "anxiety_level", "exercise_minutes",
                "social_connection", "screen_time", "caffeine_intake", "water_intake",
                "sunlight_exposure", "work_life_balance"]
    available = [c for c in features if c in df.columns]
    if len(available) < 3:
        return None
    X = df[available].fillna(df[available].median()).values
    y = df["wellness_score"].values
    model = LinearRegression().fit(X, y)
    last = df[available].iloc[-1].values
    predictions = []
    dates = []
    for i in range(1, 4):
        # FIX: Use np.random.normal correctly
        noise = np.random.normal(0, 0.3, len(last))
        future_X = np.clip(last + noise, 0, None).reshape(1, -1)
        pred = model.predict(future_X)[0]
        predictions.append(round(np.clip(pred, 0, 100), 1))
        dates.append(df["date"].iloc[-1] + timedelta(days=i))
    hist_dates = df["date"].tolist()
    hist_scores = df["wellness_score"].tolist()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist_dates, y=hist_scores, mode="lines+markers", name="Historical",
        line=dict(color=COLOR_PRIMARY, width=2)
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=predictions, mode="lines+markers", name="AI Prediction",
        line=dict(color=COLOR_MEDIUM, width=2, dash="dash"),
        marker=dict(symbol="diamond", size=10)
    ))
    fig.add_vline(x=hist_dates[-1], line_dash="dot", line_color=COLOR_MUTED,
                  annotation_text="Today")
    fig.update_layout(
        title="Wellness Score Trajectory + 3-Day AI Forecast",
        yaxis_title="Wellness Score",
        hovermode="x unified"
    )
    return style_plot(fig)

def create_correlation_network(df):
    """Create a network-style visualization of factor correlations."""
    correlations = find_key_correlations(df)
    if not correlations:
        return None
    nodes = set()
    edges = []
    for c in correlations[:6]:
        nodes.add(c["factor_a"])
        nodes.add(c["factor_b"])
        edges.append((c["factor_a"], c["factor_b"], abs(c["correlation"]), c["direction"]))
    node_list = list(nodes)
    positions = {}
    angle_step = 2 * np.pi / len(node_list)
    for i, node in enumerate(node_list):
        positions[node] = (np.cos(i * angle_step) * 2, np.sin(i * angle_step) * 2)
    fig = go.Figure()
    for a, b, weight, direction in edges:
        x0, y0 = positions[a]
        x1, y1 = positions[b]
        color = COLOR_GOOD if direction == "positive" else COLOR_HIGH
        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1], mode="lines",
            line=dict(color=color, width=weight * 5),
            hoverinfo="skip", showlegend=False
        ))
    for node, (x, y) in positions.items():
        fig.add_trace(go.Scatter(
            x=[x], y=[y], mode="markers+text",
            marker=dict(size=30, color=COLOR_PRIMARY, line=dict(color=COLOR_INK, width=2)),
            text=node.replace("_", " ").title(), textposition="top center",
            textfont=dict(size=10, color=COLOR_INK),
            hovertemplate=f"<b>{node.replace('_', ' ').title()}</b><extra></extra>",
            showlegend=False
        ))
    fig.update_layout(
        title="Wellness Factor Correlation Network",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20),
        height=400
    )
    return fig


PAGES = [
    "🏠 Home", "📋 Assessment", "🤖 Risk Prediction", "🎯 Goals",
    "📂 Bulk Upload", "📈 Dashboard", "📝 Journal", "📓 My Journals", "🗂️ My Entries",
    "🆘 Support & Coping", "📄 Report", "🧠 AI Insights", "📊 Admin"
]

# ═══════════════════════════════════════════════════════════════
# SIDEBAR + NAVIGATION
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    if LOGO_PATH:
        try:
            if LOGO_PATH.startswith("http"):
                st.image(LOGO_PATH, width=180)
            elif os.path.exists(LOGO_PATH):
                st.image(LOGO_PATH, width=180)
        except Exception:
            pass

    toggle_icon = "🌙" if not st.session_state.dark_mode else "☀️"
    toggle_text = "Dark Mode" if not st.session_state.dark_mode else "Light Mode"
    if st.sidebar.button(f"{toggle_icon} {toggle_text}", use_container_width=True, key="dark_mode_toggle"):
        toggle_dark_mode()
        st.rerun()

    st.sidebar.markdown("""
    <div class="sidebar-brand">🧠 MindTrack</div>
    <div class="sidebar-tagline">Wellness Intelligence</div>
    """, unsafe_allow_html=True)

_nav_target = None
if 'nav_to' in st.session_state:
    _nav_map = {
        'assessment': "📋 Assessment", 'journal': "📝 Journal",
        'support': "🆘 Support & Coping", 'goals': "🎯 Goals",
    }
    if st.session_state['nav_to'] in _nav_map:
        _nav_target = _nav_map[st.session_state['nav_to']]
    del st.session_state['nav_to']

_default_index = 0
if _nav_target and _nav_target in PAGES:
    _default_index = PAGES.index(_nav_target)

page = st.sidebar.radio("Go to", PAGES, index=_default_index, label_visibility="collapsed")

show_user_badge()

st.sidebar.markdown("""
<div class="sidebar-disclaimer">
MindTrack supports self-reflection and is not a diagnostic or emergency tool.<br>
In crisis (US)? Call or text <b>988</b> — or see Support & Coping.
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE ROUTER - CONTINUE IN NEXT PART
# ═══════════════════════════════════════════════════════════════
# This file continues with all the page implementations...
# Due to size constraints, the remaining pages (Home, Assessment, Risk Prediction, etc.)
# should be split into additional files or combined at runtime.
