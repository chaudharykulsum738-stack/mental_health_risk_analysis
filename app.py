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
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════
# 🎨 LOGO CONFIGURATION — PUT YOUR LOGO HERE
# ═══════════════════════════════════════════════════════════════
LOGO_PATH = "logo.png"  # <-- CHANGE THIS to your image file name
# LOGO_PATH = "https://your-domain.com/logo.png"  # Or use a URL
# LOGO_PATH = None  # Or disable logo

st.set_page_config(page_title="MindTrack | Wellness Intelligence", page_icon="🧠", layout="wide")

# ═══════════════════════════════════════════════════════════════
# 🌗 DARK MODE: STATE & COLOR SYSTEM
# ═══════════════════════════════════════════════════════════════
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

# Light mode colors
L_COLORS = {
    "ink": "#1B2430",
    "muted": "#5B6B6A",
    "bg": "#F4F6F5",
    "card": "#FFFFFF",
    "border": "rgba(27,36,48,0.10)",
    "sidebar_bg": "#1B2430",
    "sidebar_text": "#EDEFEE",
    "sidebar_border": "rgba(255,255,255,0.06)",
    "radio_bg": "rgba(255,255,255,0.035)",
    "radio_hover": "rgba(255,255,255,0.09)",
    "grid": "rgba(27,36,48,0.07)",
}

# Dark mode colors
D_COLORS = {
    "ink": "#E8ECF1",
    "muted": "#8B95A5",
    "bg": "#0D1117",
    "card": "#161B22",
    "border": "rgba(255,255,255,0.08)",
    "sidebar_bg": "#0D1117",
    "sidebar_text": "#C9D1D9",
    "sidebar_border": "rgba(255,255,255,0.08)",
    "radio_bg": "rgba(255,255,255,0.05)",
    "radio_hover": "rgba(255,255,255,0.12)",
    "grid": "rgba(255,255,255,0.06)",
}

# Pick active palette
C = D_COLORS if st.session_state.dark_mode else L_COLORS

# Static accent colors (same in both modes)
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
# 🌗 DYNAMIC CSS INJECTION
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
</style>
""", unsafe_allow_html=True)

css = f"""
<style>
:root {{
    --ink: {C['ink']}; --muted: {C['muted']}; --paper: {C['bg']}; --card: {C['card']};
    --border: {C['border']}; --primary: {COLOR_PRIMARY}; --primary-light: {COLOR_PRIMARY_LIGHT};
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
    background: {C['sidebar_bg']}; 
    border-right: 1px solid {C['sidebar_border']}; 
}}
[data-testid="stSidebar"] * {{ color: {C['sidebar_text']} !important; }}
.sidebar-brand {{
    font-family: 'Fraunces', serif; font-size: 1.55rem; font-weight: 700; color: #fff !important;
    margin: 0.2rem 0 0.1rem 0; display: flex; align-items: center; gap: 8px;
}}
.sidebar-tagline {{
    font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--primary-light) !important; margin-bottom: 1.5rem;
}}
[data-testid="stSidebar"] div[role="radiogroup"] label {{
    background: {C['radio_bg']}; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 9px 14px; margin-bottom: 6px; transition: all 0.15s ease;
}}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
    background: {C['radio_hover']}; border-color: var(--primary-light);
}}
.sidebar-disclaimer {{
    font-size: 0.68rem !important; color: rgba(237,239,238,0.55) !important;
    margin-top: 16px; line-height: 1.45; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.08);
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

/* Dark mode: dataframe/table styling */
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

/* Dark mode: input fields */
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

/* Dark mode: select slider */
.stSlider > div > div > div {{
    color: var(--ink) !important;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)



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


# ═══════════════════════════════════════════════════════════════
# DATABASE SETUP
# ═══════════════════════════════════════════════════════════════
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
        return dict(row) if row else None
    except Exception as e:
        st.error(f"Error loading goals: {e}")
        return None


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

def calculate_wellness_score(stress, sleep, anxiety, exercise, social_connection, screen_time,
                             caffeine_intake, water_intake, sunlight_exposure, work_life_balance):
    """Balanced 0-100 wellness score. Perfect health = 100. Average health ≈ 60-75."""
    # Force everything to float to handle strings from Excel/CSV
    try:
        stress = float(stress)
        sleep = float(sleep)
        anxiety = float(anxiety)
        exercise = float(exercise)
        social_connection = float(social_connection)
        screen_time = float(screen_time)
        caffeine_intake = float(caffeine_intake)
        water_intake = float(water_intake)
        sunlight_exposure = float(sunlight_exposure)
        work_life_balance = float(work_life_balance)
    except (ValueError, TypeError):
        return 0.0

    score = 0
    score += min(sleep / 8, 1.0) * 15
    score += max(0, (10 - stress) / 10) * 15
    score += max(0, (10 - anxiety) / 10) * 15
    score += min(exercise / 60, 1.0) * 10
    score += min(social_connection / 8, 1.0) * 10
    score += max(0, (8 - screen_time) / 8) * 10
    score += max(0, (5 - caffeine_intake) / 5) * 5
    score += min(water_intake / 8, 1.0) * 10
    score += min(sunlight_exposure / 30, 1.0) * 5
    score += min(work_life_balance / 7, 1.0) * 5
    return round(score, 1)


def predict_risk(stress, sleep, anxiety, exercise, mood, social_connection, screen_time,
                 caffeine_intake, water_intake, sunlight_exposure, work_life_balance):
    wellness_score = calculate_wellness_score(stress, sleep, anxiety, exercise, social_connection,
                                               screen_time, caffeine_intake, water_intake,
                                               sunlight_exposure, work_life_balance)
    if wellness_score < 35:
        risk = "High"
    elif wellness_score < 65:
        risk = "Medium"
    else:
        risk = "Low"
    factors = []
    if float(stress) > 7:
        factors.append("High stress levels")
    if float(sleep) < 6:
        factors.append("Insufficient sleep")
    if float(anxiety) > 7:
        factors.append("High anxiety levels")
    if float(exercise) < 30:
        factors.append("Low physical activity")
    if float(social_connection) < 4:
        factors.append("Low social connection")
    if float(screen_time) > 8:
        factors.append("Excessive screen time")
    if float(caffeine_intake) > 5:
        factors.append("High caffeine intake")
    if float(water_intake) < 4:
        factors.append("Low hydration")
    if float(sunlight_exposure) < 15:
        factors.append("Insufficient sunlight exposure")
    if float(work_life_balance) < 4:
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
    ink_color = rl_colors.HexColor("#2D3436" if not st.session_state.dark_mode else "#E8ECF1")
    muted_color = rl_colors.HexColor(C["muted"])
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=6,
                                  alignment=1, textColor=brand_color)
    story.append(Paragraph("MindTrack Wellness Report", title_style))
    eyebrow_style = ParagraphStyle('Eyebrow', parent=styles['Normal'], fontSize=10, alignment=1,
                                    textColor=muted_color, spaceAfter=24)
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
                                   textColor=muted_color)
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
        risk_map = {"Low": 1, "Medium": 2, "High": 3}
        df["risk_num"] = df["risk_level"].map(risk_map)
        return df.dropna(subset=["date"])
    except Exception as e:
        st.error(f"Error loading predictions: {e}")
        return pd.DataFrame()



def style_plot(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(27,36,48,0.02)" if not st.session_state.dark_mode else "rgba(0,0,0,0)",
        font={"color": C['ink'], "family": "Inter, sans-serif"},
        title_font={"family": "Fraunces, serif", "color": C['ink'], "size": 17},
        margin=dict(l=20, r=20, t=50, b=20),
        legend={"font": {"color": C['muted']}},
    )
    fig.update_xaxes(
        gridcolor=C['grid'], 
        color=C['muted']
    )
    fig.update_yaxes(
        gridcolor=C['grid'], 
        color=C['muted']
    )
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
                   radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(color=C['muted'])),
                   angularaxis=dict(tickfont=dict(color=C['ink']))),
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
        title={'text': title, 'font': {'size': 20, 'color': C['ink'], 'family': 'Fraunces, serif'}},
        number={'font': {'color': C['ink'], 'family': 'IBM Plex Mono, monospace'}},
        gauge={'axis': {'range': list(value_range), 'tickwidth': 1, 'tickcolor': C['muted']},
               'bar': {'color': COLOR_PRIMARY}, 'bgcolor': "rgba(0,0,0,0)",
               'borderwidth': 1, 'bordercolor': C['border'], 'steps': steps}
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': C['ink']})
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
    """Create an AI trend prediction chart."""
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
    fig.add_vline(x=hist_dates[-1], line_dash="dot", line_color=C['muted'],
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
            marker=dict(size=30, color=COLOR_PRIMARY, line=dict(color=C['ink'], width=2)),
            text=node.replace("_", " ").title(), textposition="top center",
            textfont=dict(size=10, color=C['ink']),
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


# ═══════════════════════════════════════════════════════════════
# PAGE LIST & SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════════
PAGES = [
    "🏠 Home", "📋 Assessment", "🤖 Risk Prediction", "🎯 Goals",
    "📂 Bulk Upload", "📈 Dashboard", "📝 Journal", "📓 My Journals", "🗂️ My Entries",
    "🆘 Support & Coping", "📄 Report", "🧠 AI Insights", "📊 Admin"
]

# Build sidebar — FIXED: no nested st.sidebar calls inside with st.sidebar
with st.sidebar:
    # Logo display
    if LOGO_PATH:
        try:
            if LOGO_PATH.startswith("http"):
                st.image(LOGO_PATH, width=180)
            elif os.path.exists(LOGO_PATH):
                st.image(LOGO_PATH, width=180)
        except Exception:
            pass

    # Dark mode toggle — FIXED: uses st.button (not st.sidebar.button) inside with st.sidebar
    toggle_icon = "🌙" if not st.session_state.dark_mode else "☀️"
    toggle_text = "Dark Mode" if not st.session_state.dark_mode else "Light Mode"
    if st.button(f"{toggle_icon} {toggle_text}", use_container_width=True, key="dark_mode_toggle"):
        toggle_dark_mode()

    st.markdown("""
    <div class="sidebar-brand">🧠 MindTrack</div>
    <div class="sidebar-tagline">Wellness Intelligence</div>
    """, unsafe_allow_html=True)

# Initialize page selector in session state
if "page_selector" not in st.session_state:
    st.session_state.page_selector = PAGES[0]

page = st.sidebar.radio("Go to", PAGES, 
                         index=PAGES.index(st.session_state.page_selector), 
                         label_visibility="collapsed",
                         key="page_selector")

# Logout button in sidebar
if st.session_state.get("logged_in"):
    if st.sidebar.button("🚪 Log out", use_container_width=True, key="logout_btn"):
        logout_user()
        st.session_state.page_selector = PAGES[0]
        st.rerun()
    st.sidebar.markdown("---")

show_user_badge()

st.sidebar.markdown("""
<div class="sidebar-disclaimer">
MindTrack supports self-reflection and is not a diagnostic or emergency tool.<br>
In crisis (US)? Call or text <b>988</b> — or see Support & Coping.
</div>
""", unsafe_allow_html=True)
# ═══════════════════════════════════════════════════════════════
# HOME PAGE
# ═══════════════════════════════════════════════════════════════
if page == "🏠 Home":
    init_login_state()
    if not st.session_state.logged_in:
        show_login_page()
        st.stop()
    st.markdown(f"""
    <div class="hero-wrap">
        <div class="hero-icon">🧠</div>
        <div class="hero-title">MindTrack</div>
        <div class="hero-tagline">Welcome back, {st.session_state.current_user}</div>
    </div>
    """, unsafe_allow_html=True)
    pulse_divider()

    st.markdown("## ⚡ Quick Start")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 Start New Assessment", use_container_width=True, key="home_btn_assessment"):
            st.session_state.page_selector = "📋 Assessment"
            st.rerun()
    with col2:
        if st.button("📝 Write in Journal", use_container_width=True, key="home_btn_journal"):
            st.session_state.page_selector = "📝 Journal"
            st.rerun()
    with col3:
        if st.button("🆘 I Need Support Now", use_container_width=True, key="home_btn_support"):
            st.session_state.page_selector = "🆘 Support & Coping"
            st.rerun()

    try:
        df = get_history_data()
        if len(df) > 0:
            pulse_divider()
            df_sorted = df.sort_values("date")
            dates_only = df_sorted["date"].dt.date.tolist()
            current_streak, longest_streak = calculate_streaks(dates_only)

            st.markdown("## 📊 Your Stats")
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Total Check-ins", len(df_sorted))
            m2.metric("Avg Sleep", f"{df_sorted['sleep_hours'].mean():.1f}h")
            m3.metric("Avg Stress", f"{df_sorted['stress_level'].mean():.1f}")
            m4.metric("🔥 Current Streak", f"{current_streak} day{'s' if current_streak != 1 else ''}")
            m5.metric("🏆 Longest Streak", f"{longest_streak} day{'s' if longest_streak != 1 else ''}")

            this_avg, last_avg = weekly_digest(df_sorted)
            if this_avg is not None:
                st.markdown("#### This Week vs Last Week")
                delta_txt = f"{this_avg - last_avg:+.0f} vs last week" if last_avg is not None else "No prior week to compare"
                st.metric("This Week's Avg Wellness", f"{this_avg:.0f}/100", delta_txt)
    except Exception:
        pass

    pulse_divider()
    wellness_tips = [
        "Take a 5-minute walk outside 🌳", "Practice deep breathing for 2 minutes 🧘",
        "Drink a glass of water 💧", "Call a friend or family member 📞",
        "Write down 3 things you are grateful for ✍️", "Stretch your body for 10 minutes 🤸",
        "Listen to your favorite song 🎵", "Take a short break from screens 📵",
        "Get 15 minutes of sunlight ☀️", "Set a work boundary today ⏰",
        "Drink herbal tea instead of coffee 🍵", "Connect with someone you care about 👥"
    ]
    st.markdown("## 🌟 Daily Wellness Tip")
    st.info(random.choice(wellness_tips))

    pulse_divider()
    quotes = [
        "The greatest glory in living lies not in never falling, but in rising every time we fall. – Nelson Mandela",
        "The way to get started is to quit talking and begin doing. – Walt Disney",
        "Your time is limited, do not waste it living someone else's life. – Steve Jobs",
        "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt",
        "It does not matter how slowly you go as long as you do not stop. – Confucius",
        "Connection is why we are here; it gives purpose and meaning to our lives. – Brené Brown",
        "Balance is not something you find, it is something you create. – Jana Kingsford"
    ]
    st.markdown("## 💬 Motivation")
    st.success(random.choice(quotes))

# ═══════════════════════════════════════════════════════════════
# ASSESSMENT PAGE — FIXED WITH st.form
# ═══════════════════════════════════════════════════════════════
elif page == "📋 Assessment":
    require_login()
    page_header("📋", "Daily Check-in", "Mental Health Assessment",
                "A comprehensive 11-factor wellness check to understand how you are doing today.")

    # REMOVED st.form wrapper so sliders update live
    username = st.text_input("👤 Your name", value=st.session_state.get("current_user", "Guest User"), key="assessment_username")
    entry_date = st.date_input("📅 Date of this assessment", value=datetime.now().date(), key="assessment_date")

    st.markdown("## Answer the following questions:")
    mood_emojis = {"Very Bad": "😢", "Bad": "😔", "Neutral": "😐", "Good": "😊", "Very Good": "😄"}
    mood = st.select_slider(
        "How is your mood today?", options=["Very Bad", "Bad", "Neutral", "Good", "Very Good"],
        value="Good", format_func=lambda x: f"{mood_emojis[x]} {x}", key="assessment_mood"
    )

    col1, col2 = st.columns(2)
    with col1:
        sleep_hours = st.slider("😴 How many hours did you sleep last night?", 0, 12, 7, key="assessment_sleep")
        stress_level = st.slider("😰 How stressed are you? (0-10)", 0, 10, 3, key="assessment_stress")
        anxiety_level = st.slider("😟 How anxious are you? (0-10)", 0, 10, 3, key="assessment_anxiety")
        exercise_minutes = st.slider("🏃 How many minutes did you exercise today?", 0, 180, 30, key="assessment_exercise")
    with col2:
        social_connection = st.slider("👥 Social connection quality (0-10)", 0, 10, 6,
                                       help="How connected do you feel to friends, family, or community?", key="assessment_social")
        screen_time = st.slider("📱 Screen time today (hours)", 0, 16, 4,
                                 help="Total hours spent on phones, computers, TV", key="assessment_screen")
        caffeine_intake = st.slider("☕ Caffeine intake (cups today)", 0, 10, 2,
                                     help="Coffee, tea, energy drinks, etc.", key="assessment_caffeine")
        water_intake = st.slider("💧 Water intake (glasses today)", 0, 20, 6,
                                  help="Approximate number of 8oz glasses", key="assessment_water")

    col3, col4 = st.columns(2)
    with col3:
        sunlight_exposure = st.slider("☀️ Sunlight exposure (minutes today)", 0, 300, 30,
                                       help="Time spent outdoors in natural light", key="assessment_sun")
    with col4:
        work_life_balance = st.slider("⚖️ Work-life balance (0-10)", 0, 10, 6,
                                       help="How well are you balancing work/study with personal life?", key="assessment_worklife")

    # Preview now updates LIVE as you drag sliders
    preview_score = calculate_wellness_score(stress_level, sleep_hours, anxiety_level, exercise_minutes,
                                              social_connection, screen_time, caffeine_intake,
                                              water_intake, sunlight_exposure, work_life_balance)
    st.metric("Preview Wellness Score", f"{preview_score}/100")

    goals = get_goals(username)
    if goals:
        st.caption(
            f"🎯 Your goals: {goals['target_sleep']:.0f}h sleep · "
            f"{goals['target_exercise']:.0f} min exercise · stress under {goals['target_stress_max']:.0f} · "
            f"social >= {goals.get('target_social', 5):.0f} · screen <= {goals.get('target_screen_max', 4):.0f}h · "
            f"water >= {goals.get('target_water', 6):.0f} · sunlight >= {goals.get('target_sunlight', 15):.0f}min · "
            f"work-life >= {goals.get('target_worklife', 5):.0f}"
        )

    if st.button("✅ Submit Assessment", use_container_width=True, key="assessment_submit"):
        success = save_user_history(username, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes,
                              social_connection, screen_time, caffeine_intake, water_intake,
                              sunlight_exposure, work_life_balance, entry_date=entry_date)
        if success:
            st.session_state['assessment_data'] = {
                "username": username, "date": entry_date, "mood": mood, "sleep_hours": sleep_hours,
                "stress_level": stress_level, "anxiety_level": anxiety_level, "exercise_minutes": exercise_minutes,
                "social_connection": social_connection, "screen_time": screen_time,
                "caffeine_intake": caffeine_intake, "water_intake": water_intake,
                "sunlight_exposure": sunlight_exposure, "work_life_balance": work_life_balance
            }
            st.success(f"🎉 Assessment saved for {entry_date.strftime('%Y-%m-%d')}!")
            st.balloons()



# ═══════════════════════════════════════════════════════════════
# RISK PREDICTION PAGE
# ═══════════════════════════════════════════════════════════════
elif page == "🤖 Risk Prediction":
    require_login()
    page_header("🤖", "AI Analysis", "Mental Health Risk Prediction", "Based on your most recent assessment.")

    if 'assessment_data' not in st.session_state:
        st.warning("⚠️ Please complete the Assessment first!")
    else:
        data = st.session_state['assessment_data']
        stress, sleep = data["stress_level"], data["sleep_hours"]
        anxiety, exercise = data["anxiety_level"], data["exercise_minutes"]
        mood, username = data["mood"], data["username"]
        social_connection = data.get("social_connection", 5)
        screen_time = data.get("screen_time", 4)
        caffeine_intake = data.get("caffeine_intake", 2)
        water_intake = data.get("water_intake", 6)
        sunlight_exposure = data.get("sunlight_exposure", 30)
        work_life_balance = data.get("work_life_balance", 5)

        risk, factors, wellness_score = predict_risk(stress, sleep, anxiety, exercise, mood,
                                                      social_connection, screen_time, caffeine_intake,
                                                      water_intake, sunlight_exposure, work_life_balance)
        recommendations = get_recommendations(stress, sleep, anxiety, exercise, social_connection,
                                               screen_time, caffeine_intake, water_intake,
                                               sunlight_exposure, work_life_balance)

        st.markdown("## 📊 Prediction Results")
        st.plotly_chart(gauge_figure(wellness_score, "Wellness Score"), use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            risk_badge(risk)
        with col2:
            st.metric("Wellness Score", f"{wellness_score}/100")

        compare_col, radar_col = st.columns(2)
        with compare_col:
            st.plotly_chart(create_extended_factor_bar(stress, sleep, anxiety, exercise, social_connection,
                                                        screen_time, caffeine_intake, water_intake,
                                                        sunlight_exposure, work_life_balance), use_container_width=True)
        with radar_col:
            st.plotly_chart(create_wellness_radar(sleep, stress, anxiety, exercise, mood, social_connection,
                                                   screen_time, caffeine_intake, water_intake,
                                                   sunlight_exposure, work_life_balance), use_container_width=True)

        st.markdown("## 🔍 Key Factors")
        for factor in factors:
            st.info(f"• {factor}")

        st.markdown("## 💡 Personalized Recommendations")
        for rec in recommendations:
            st.success(rec)

        save_prediction(username, risk, wellness_score, factors)

        hist = get_history_data()
        mine = hist[hist["username"].astype(str) == str(username)] if not hist.empty else hist
        if not mine.empty and trend_nudge(mine):
            pulse_divider()
            st.warning(
                "Your recent check-ins suggest things have felt harder lately. "
                "That is worth paying attention to — consider reaching out to a professional "
                "or someone you trust. The **Support & Coping** page has resources if you would like them."
            )

# ═══════════════════════════════════════════════════════════════
# GOALS PAGE
# ═══════════════════════════════════════════════════════════════
elif page == "🎯 Goals":
    require_login()
    page_header("🎯", "Personal Targets", "Your Wellness Goals",
                "Set targets that matter to you — we will track your progress against them.")

    with st.form("goals_form"):
        username = st.text_input("👤 Your name", value=st.session_state.get("current_user", "Guest User"), key="goals_username")
        existing = get_goals(username)

        st.markdown("### Core Wellness Goals")
        col1, col2, col3 = st.columns(3)
        with col1:
            target_sleep = st.slider("🎯 Target sleep (hours)", 4, 10,
                                      int(existing["target_sleep"]) if existing else 8, key="goal_sleep")
        with col2:
            target_exercise = st.slider("🎯 Target exercise (min/day)", 0, 120,
                                         int(existing["target_exercise"]) if existing else 30, key="goal_exercise")
        with col3:
            target_stress_max = st.slider("🎯 Max comfortable stress", 0, 10,
                                           int(existing["target_stress_max"]) if existing else 5, key="goal_stress")

        st.markdown("### Lifestyle Goals")
        col4, col5, col6 = st.columns(3)
        with col4:
            target_social = st.slider("🎯 Min social connection", 0, 10,
                                       int(existing["target_social"]) if existing and "target_social" in existing else 5, key="goal_social")
        with col5:
            target_screen_max = st.slider("🎯 Max screen time (hours)", 0, 12,
                                           int(existing["target_screen_max"]) if existing and "target_screen_max" in existing else 4, key="goal_screen")
        with col6:
            target_water = st.slider("🎯 Min water intake (glasses)", 0, 15,
                                      int(existing["target_water"]) if existing and "target_water" in existing else 6, key="goal_water")

        col7, col8 = st.columns(2)
        with col7:
            target_sunlight = st.slider("🎯 Min sunlight (minutes)", 0, 120,
                                         int(existing["target_sunlight"]) if existing and "target_sunlight" in existing else 15, key="goal_sun")
        with col8:
            target_worklife = st.slider("🎯 Min work-life balance", 0, 10,
                                         int(existing["target_worklife"]) if existing and "target_worklife" in existing else 5, key="goal_worklife")

        submitted = st.form_submit_button("💾 Save Goals", use_container_width=True)

    if submitted:
        save_goals(username, target_sleep, target_exercise, target_stress_max,
                   target_social, target_screen_max, target_water, target_sunlight, target_worklife)
        st.success("Goals saved!")

    pulse_divider()
    st.markdown("## 📈 Progress vs Goals")
    hist = get_history_data()
    mine = hist[hist["username"].astype(str) == username].sort_values("date") if not hist.empty else hist

    if mine.empty:
        st.info("Complete an assessment to see your progress against these goals.")
    else:
        last = mine.iloc[-1]
        g = get_goals(username) or {
            "target_sleep": target_sleep, "target_exercise": target_exercise,
            "target_stress_max": target_stress_max, "target_social": target_social,
            "target_screen_max": target_screen_max, "target_water": target_water,
            "target_sunlight": target_sunlight, "target_worklife": target_worklife,
        }

        gcol1, gcol2, gcol3 = st.columns(3)
        gcol1.metric("Sleep (latest)", f"{last['sleep_hours']:.1f}h",
                     f"{last['sleep_hours'] - g['target_sleep']:+.1f}h vs goal")
        gcol2.metric("Exercise (latest)", f"{last['exercise_minutes']:.0f} min",
                     f"{last['exercise_minutes'] - g['target_exercise']:+.0f} min vs goal")
        gcol3.metric("Stress (latest)", f"{last['stress_level']:.0f}",
                     f"{last['stress_level'] - g['target_stress_max']:+.0f} vs max", delta_color="inverse")

        gcol4, gcol5, gcol6 = st.columns(3)
        gcol4.metric("Social (latest)", f"{last.get('social_connection', 0):.0f}",
                     f"{last.get('social_connection', 0) - g['target_social']:+.0f} vs goal")
        gcol5.metric("Screen (latest)", f"{last.get('screen_time', 0):.0f}h",
                     f"{last.get('screen_time', 0) - g['target_screen_max']:+.0f}h vs max", delta_color="inverse")
        gcol6.metric("Water (latest)", f"{last.get('water_intake', 0):.0f}",
                     f"{last.get('water_intake', 0) - g['target_water']:+.0f} vs goal")

        gcol7, gcol8 = st.columns(2)
        gcol7.metric("Sunlight (latest)", f"{last.get('sunlight_exposure', 0):.0f}min",
                     f"{last.get('sunlight_exposure', 0) - g['target_sunlight']:+.0f}min vs goal")
        gcol8.metric("Work-Life (latest)", f"{last.get('work_life_balance', 0):.0f}",
                     f"{last.get('work_life_balance', 0) - g['target_worklife']:+.0f} vs goal")



# ═══════════════════════════════════════════════════════════════
# BULK UPLOAD PAGE
# ═══════════════════════════════════════════════════════════════
elif page == "📂 Bulk Upload":
    require_login()
    page_header("📂", "Batch Processing", "Bulk Upload & Analyze", "Upload an Excel file to analyze many records at once.")
    st.write(
        "Upload an Excel file (.xlsx) with multiple records to analyze them all at once, "
        "instead of entering them one by one in the Assessment page."
    )

    REQUIRED_COLUMNS = ["username", "mood", "sleep_hours", "stress_level", "anxiety_level", "exercise_minutes",
                        "social_connection", "screen_time", "caffeine_intake", "water_intake",
                        "sunlight_exposure", "work_life_balance"]

    with st.expander("📋 Expected file format / download a template"):
        st.write(f"Your Excel file must contain these columns: `{'`, `'.join(REQUIRED_COLUMNS)}`")
        st.caption("`mood` must be one of: Very Bad, Bad, Neutral, Good, Very Good. A `date` column is optional.")
        template_df = pd.DataFrame([{
            "username": "John Doe", "mood": "Good", "sleep_hours": 7,
            "stress_level": 3, "anxiety_level": 2, "exercise_minutes": 30,
            "social_connection": 6, "screen_time": 4, "caffeine_intake": 2,
            "water_intake": 6, "sunlight_exposure": 30, "work_life_balance": 6,
        }])
        st.download_button(
            label="📥 Download Template (Excel)", data=export_to_excel(template_df, sheet_name="Template"),
            file_name="bulk_upload_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="bulk_dl_template"
        )

    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"], key="bulk_uploader")

    if uploaded_file is not None:
        try:
            bulk_df = pd.read_excel(uploaded_file)
        except Exception as e:
            bulk_df = None
            st.error(f"❌ Could not read that file: {e}")

        if bulk_df is not None:
            missing_cols = [c for c in REQUIRED_COLUMNS if c not in bulk_df.columns]
            if missing_cols:
                st.error(f"❌ Missing required column(s): {', '.join(missing_cols)}. "
                         f"Check the template above for the expected format.")
            elif bulk_df.empty:
                st.warning("⚠️ The uploaded file has no rows.")
            else:
                bulk_df = bulk_df.copy()
                if "date" not in bulk_df.columns:
                    bulk_df["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                numeric_cols = ["sleep_hours", "stress_level", "anxiety_level", "exercise_minutes",
                            "social_connection", "screen_time", "caffeine_intake",
                            "water_intake", "sunlight_exposure", "work_life_balance"]
                for col in numeric_cols:
                    if col in bulk_df.columns:
                        bulk_df[col] = pd.to_numeric(bulk_df[col], errors="coerce").fillna(0)
                risk_levels, wellness_scores, factor_lists = [], [], []
                for _, row in bulk_df.iterrows():
                    risk, factors, wellness = predict_risk(
                        row["stress_level"], row["sleep_hours"], row["anxiety_level"],
                        row["exercise_minutes"], row["mood"],
                        row.get("social_connection", 5), row.get("screen_time", 4),
                        row.get("caffeine_intake", 2), row.get("water_intake", 6),
                        row.get("sunlight_exposure", 30), row.get("work_life_balance", 5),
                    )
                    risk_levels.append(risk)
                    wellness_scores.append(wellness)
                    factor_lists.append(", ".join(factors))

                bulk_df["wellness_score"] = wellness_scores
                bulk_df["risk_level"] = risk_levels
                bulk_df["factors"] = factor_lists

                st.success(f"✅ Analyzed {len(bulk_df)} records.")

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Records", len(bulk_df))
                m2.metric("Avg Wellness", f"{bulk_df['wellness_score'].mean():.0f}/100")
                m3.metric("High Risk", int((bulk_df["risk_level"] == "High").sum()))
                m4.metric("Low Risk", int((bulk_df["risk_level"] == "Low").sum()))

                st.markdown("### 📊 Results")
                st.dataframe(bulk_df, use_container_width=True)

                c1, c2 = st.columns(2)
                with c1:
                    risk_counts = bulk_df["risk_level"].value_counts().reset_index()
                    risk_counts.columns = ["Risk", "Count"]
                    fig_risk = px.bar(risk_counts, x="Risk", y="Count", color="Risk",
                                       title="Risk Level Distribution", color_discrete_map=RISK_COLOR_MAP)
                    st.plotly_chart(style_plot(fig_risk), use_container_width=True)
                with c2:
                    fig_hist = px.histogram(bulk_df, x="wellness_score", nbins=15, title="Wellness Score Distribution",
                                             color_discrete_sequence=[COLOR_PRIMARY])
                    st.plotly_chart(style_plot(fig_hist), use_container_width=True)

                st.markdown("### 📥 Export or Save")
                dl_col, save_col = st.columns(2)
                with dl_col:
                    st.download_button(
                        label="📥 Download Analyzed Results (Excel)", data=export_to_excel(bulk_df, sheet_name="Bulk Analysis"),
                        file_name=f"bulk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="bulk_dl_results"
                    )
                with save_col:
                    if st.button("➕ Add these records to the backend data", use_container_width=True, key="bulk_save_btn"):
                        init_db()
                        conn = get_connection()
                        history_rows = bulk_df[["username", "date", "mood", "sleep_hours", "stress_level",
                                                "anxiety_level", "exercise_minutes", "social_connection",
                                                "screen_time", "caffeine_intake", "water_intake",
                                                "sunlight_exposure", "work_life_balance"]].values.tolist()
                        conn.executemany(
                            """INSERT INTO user_history
                               (username, date, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes,
                                social_connection, screen_time, caffeine_intake, water_intake,
                                sunlight_exposure, work_life_balance)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", history_rows,
                        )
                        prediction_rows = bulk_df[["username", "date", "risk_level", "wellness_score", "factors"]].values.tolist()
                        conn.executemany(
                            """INSERT INTO predictions (username, date, risk_level, wellness_score, factors)
                               VALUES (?, ?, ?, ?, ?)""", prediction_rows,
                        )
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Added {len(bulk_df)} records to the backend. They will now show up in Dashboard and Admin.")



# ═══════════════════════════════════════════════════════════════
# DASHBOARD PAGE
# ═══════════════════════════════════════════════════════════════
elif page == "📈 Dashboard":
    require_login()
    page_header("📈", "Analytics", "Wellness Dashboard", "Trends, distributions, and correlations over time.")

    history_df = get_history_data()
    prediction_df = get_prediction_data()

    if history_df.empty:
        st.info("📭 No data available yet! Complete an assessment first.")
    else:
        filter_col1, filter_col2, filter_col3 = st.columns([1.3, 1.2, 1])
        with filter_col1:
            users = ["All Users"] + sorted(history_df["username"].dropna().astype(str).unique().tolist())
            selected_user = st.selectbox("Filter by user", users, key="dash_user_filter")
        with filter_col2:
            min_date = history_df["date"].min().date()
            max_date = history_df["date"].max().date()
            selected_dates = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date, key="dash_date_filter")
        with filter_col3:
            chart_style = st.selectbox("Chart mode", ["Smooth", "Detailed"], key="dash_chart_style")

        filtered_df = history_df.copy()
        if selected_user != "All Users":
            filtered_df = filtered_df[filtered_df["username"].astype(str) == selected_user]

        if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
            start_date, end_date = selected_dates
            filtered_df = filtered_df[
                (filtered_df["date"].dt.date >= start_date) & (filtered_df["date"].dt.date <= end_date)
            ]

        if filtered_df.empty:
            st.warning("No records match the selected filters.")
        else:
            st.markdown("## 📊 Quick Stats")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Visible Entries", len(filtered_df))
            m2.metric("Avg Wellness", f"{filtered_df['wellness_score'].mean():.0f}/100")
            m3.metric("Avg Mood", f"{filtered_df['mood_num'].mean():.1f}/5")
            m4.metric("Avg Sleep", f"{filtered_df['sleep_hours'].mean():.1f}h")

            st.download_button(
                label="📥 Download History (Excel)",
                data=export_to_excel(filtered_df.drop(columns=["mood_num"], errors="ignore"), sheet_name="History"),
                file_name=f"patient_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dash_dl_history"
            )

            trends_tab, dist_tab, insights_tab, lifestyle_tab = st.tabs(["📈 Trends", "🧩 Distributions", "🔎 Insights", "🌿 Lifestyle"])

            with trends_tab:
                col1, col2 = st.columns(2)
                line_shape = "spline" if chart_style == "Smooth" else "linear"
                with col1:
                    fig_mood = px.line(filtered_df.sort_values("date"), x="date", y="mood_num", markers=True,
                                        title="Mood Over Time", color_discrete_sequence=[COLOR_PRIMARY_LIGHT])
                    fig_mood.update_traces(line_shape=line_shape)
                    st.plotly_chart(style_plot(fig_mood), use_container_width=True)
                with col2:
                    fig_sleep = px.area(filtered_df.sort_values("date"), x="date", y="sleep_hours",
                                         title="Sleep Pattern", color_discrete_sequence=[COLOR_SLATE])
                    st.plotly_chart(style_plot(fig_sleep), use_container_width=True)

                col3, col4 = st.columns(2)
                with col3:
                    fig_stress = px.line(filtered_df.sort_values("date"), x="date", y="stress_level", markers=True,
                                          title="Stress Trend", color_discrete_sequence=[COLOR_MEDIUM])
                    fig_stress.update_traces(line_shape=line_shape)
                    st.plotly_chart(style_plot(fig_stress), use_container_width=True)
                with col4:
                    fig_exercise = px.bar(filtered_df.sort_values("date"), x="date", y="exercise_minutes",
                                           title="Exercise Activity", color="exercise_minutes",
                                           color_continuous_scale=[[0, "#E7EFEC"], [1, COLOR_PRIMARY]])
                    st.plotly_chart(style_plot(fig_exercise), use_container_width=True)

                fig_wellness = px.line(filtered_df.sort_values("date"), x="date", y="wellness_score", markers=True,
                                        title="Overall Wellness Score Trend", color_discrete_sequence=[COLOR_PRIMARY])
                fig_wellness.update_traces(line_shape=line_shape)
                st.plotly_chart(style_plot(fig_wellness), use_container_width=True)

                multi_fig = create_multi_metric_trend(filtered_df)
                if multi_fig:
                    st.plotly_chart(multi_fig, use_container_width=True)

            with dist_tab:
                col1, col2 = st.columns(2)
                with col1:
                    mood_counts = filtered_df["mood"].value_counts().reset_index()
                    mood_counts.columns = ["Mood", "Count"]
                    fig_mood_dist = px.pie(mood_counts, names="Mood", values="Count", hole=0.55,
                                            title="Mood Distribution", color_discrete_sequence=CHART_PALETTE)
                    st.plotly_chart(style_plot(fig_mood_dist), use_container_width=True)
                with col2:
                    fig_sleep_box = px.box(filtered_df, y="sleep_hours", points="all",
                                            title="Sleep Variability", color_discrete_sequence=[COLOR_SLATE])
                    st.plotly_chart(style_plot(fig_sleep_box), use_container_width=True)

                col3, col4 = st.columns(2)
                with col3:
                    fig_scatter = px.scatter(filtered_df, x="sleep_hours", y="stress_level", size="exercise_minutes",
                                              color="wellness_score", hover_data=["username", "mood"],
                                              title="Sleep vs Stress vs Exercise",
                                              color_continuous_scale=[[0, COLOR_HIGH], [0.5, COLOR_MEDIUM], [1, COLOR_GOOD]])
                    st.plotly_chart(style_plot(fig_scatter), use_container_width=True)
                with col4:
                    if not prediction_df.empty:
                        pred_filtered = prediction_df.copy()
                        if selected_user != "All Users":
                            pred_filtered = pred_filtered[pred_filtered["username"].astype(str) == selected_user]
                        if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                            pred_filtered = pred_filtered[
                                (pred_filtered["date"].dt.date >= start_date) & (pred_filtered["date"].dt.date <= end_date)
                            ]
                        if not pred_filtered.empty:
                            risk_counts = pred_filtered["risk_level"].value_counts().reset_index()
                            risk_counts.columns = ["Risk", "Count"]
                            fig_risk = px.bar(risk_counts, x="Risk", y="Count", color="Risk",
                                               title="Risk Level Distribution", color_discrete_map=RISK_COLOR_MAP)
                            st.plotly_chart(style_plot(fig_risk), use_container_width=True)
                        else:
                            st.info("No prediction records available for the selected filters.")
                    else:
                        st.info("No prediction records available yet.")

            with insights_tab:
                corr_cols = ["sleep_hours", "stress_level", "anxiety_level", "exercise_minutes",
                             "social_connection", "screen_time", "caffeine_intake",
                             "water_intake", "sunlight_exposure", "work_life_balance", "mood_num", "wellness_score"]
                available_corr_cols = [c for c in corr_cols if c in filtered_df.columns]
                if len(available_corr_cols) >= 2:
                    corr_df = filtered_df[available_corr_cols].corr()
                    heatmap = go.Figure(data=go.Heatmap(
                        z=corr_df.values, x=corr_df.columns, y=corr_df.index,
                        colorscale=[[0, COLOR_HIGH], [0.5, "#FFFFFF"], [1, COLOR_PRIMARY]],
                        zmin=-1, zmax=1, text=np.round(corr_df.values, 2), texttemplate="%{text}",
                    ))
                    heatmap.update_layout(title="Correlation Heatmap (All 11 Factors)")
                    st.plotly_chart(style_plot(heatmap), use_container_width=True)

                st.plotly_chart(create_mood_calendar(filtered_df), use_container_width=True)

                last_row = filtered_df.sort_values("date").iloc[-1]
                radar_col, info_col = st.columns([1.2, 1])
                with radar_col:
                    st.plotly_chart(create_wellness_radar(
                        last_row["sleep_hours"], last_row["stress_level"],
                        last_row["anxiety_level"], last_row["exercise_minutes"], last_row["mood"],
                        last_row.get("social_connection", 5), last_row.get("screen_time", 4),
                        last_row.get("caffeine_intake", 2), last_row.get("water_intake", 6),
                        last_row.get("sunlight_exposure", 30), last_row.get("work_life_balance", 5),
                    ), use_container_width=True)
                with info_col:
                    st.markdown("### Latest Snapshot")
                    st.metric("Latest Wellness", f"{last_row['wellness_score']:.0f}/100")
                    st.metric("Latest Mood", last_row["mood"])
                    st.metric("Latest Stress", f"{last_row['stress_level']}/10")
                    st.metric("Latest Anxiety", f"{last_row['anxiety_level']}/10")

                if trend_nudge(filtered_df):
                    st.warning(
                        "Wellness scores have been trending down over the last few check-ins. "
                        "Consider visiting **Support & Coping** or reaching out to someone you trust."
                    )

            with lifestyle_tab:
                st.markdown("### 🌿 Lifestyle Factor Analysis")
                lifestyle_fig = create_lifestyle_heatmap(filtered_df)
                if lifestyle_fig:
                    st.plotly_chart(lifestyle_fig, use_container_width=True)
                else:
                    st.info("Need at least 2 entries with lifestyle data to generate heatmap.")

                lifestyle_metrics = [
                    ("social_connection", "Social Connection", COLOR_SOCIAL),
                    ("screen_time", "Screen Time (hours)", COLOR_SCREEN),
                    ("caffeine_intake", "Caffeine Intake (cups)", COLOR_CAFFEINE),
                    ("water_intake", "Water Intake (glasses)", COLOR_WATER),
                    ("sunlight_exposure", "Sunlight Exposure (min)", COLOR_SUNLIGHT),
                    ("work_life_balance", "Work-Life Balance", COLOR_WORKLIFE),
                ]

                for i in range(0, len(lifestyle_metrics), 2):
                    c1, c2 = st.columns(2)
                    for j, (col, title, color) in enumerate(lifestyle_metrics[i:i+2]):
                        if col in filtered_df.columns:
                            fig = px.line(filtered_df.sort_values("date"), x="date", y=col, markers=True,
                                          title=title, color_discrete_sequence=[color])
                            fig.update_traces(line_shape=line_shape)
                            if j == 0:
                                c1.plotly_chart(style_plot(fig), use_container_width=True)
                            else:
                                c2.plotly_chart(style_plot(fig), use_container_width=True)



# ═══════════════════════════════════════════════════════════════
# JOURNAL PAGE — FIXED WITH st.form
# ═══════════════════════════════════════════════════════════════
elif page == "📝 Journal":
    require_login()
    page_header("📝", "Reflection", "Journal & Sentiment Analysis", "Write about your day and we will analyze your mood.")

    with st.form("journal_form"):
        username = st.text_input("👤 Your name", value=st.session_state.get("current_user", "Guest User"), key="journal_username")
        journal_text = st.text_area("Your Journal Entry:", height=250, placeholder="How was your day? What made you happy or worried?", key="journal_text")

        submitted = st.form_submit_button("🔍 Analyze & Save", use_container_width=True)

    if submitted:
        if journal_text.strip():
            sentiment, polarity = analyze_sentiment(journal_text.strip())
            entry = save_journal_entry(username, journal_text.strip(), sentiment, polarity)

            if entry:
                st.markdown("## 📊 Sentiment Analysis Results")
                col1, col2 = st.columns(2)
                with col1:
                    if sentiment == "positive":
                        st.success("Sentiment: **Positive** 😊")
                    elif sentiment == "negative":
                        st.error("Sentiment: **Negative** 😔")
                    else:
                        st.info("Sentiment: **Neutral** 😐")
                with col2:
                    fig_polarity = gauge_figure(
                        polarity, "Polarity", value_range=(-1, 1),
                        steps=[{'range': [-1, -0.1], 'color': COLOR_HIGH},
                               {'range': [-0.1, 0.1], 'color': COLOR_MEDIUM},
                               {'range': [0.1, 1], 'color': COLOR_GOOD}]
                    )
                    st.plotly_chart(fig_polarity, use_container_width=True)

                st.markdown("### 📝 Your Entry:")
                st.write(journal_text)

                st.success(f"✅ Entry saved for {username} at {entry['date']}!")

                if sentiment == "negative" and polarity < -0.4:
                    pulse_divider()
                    st.info(
                        "That sounds like a heavy day. Writing it down is a good step — "
                        "if it would help, the **Support & Coping** page has grounding techniques and resources."
                    )
        else:
            st.warning("⚠️ Please write something in your journal first!")

# ═══════════════════════════════════════════════════════════════
# MY JOURNALS PAGE
# ═══════════════════════════════════════════════════════════════
elif page == "📓 My Journals":
    require_login()
    page_header("📓", "Your Words", "My Journal History", "Review, reflect on, and manage your saved journal entries.")

    username = st.text_input("👤 Enter your name to view your journals", value=st.session_state.get("current_user", "Guest User"), key="myjournals_username")
    df = get_journal_entries(username)

    if df.empty:
        st.info("No journal entries found for this name yet. Go to **Journal** to write your first entry!")
    else:
        st.caption(f"{len(df)} journal entries found for **{username}**.")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Entries", len(df))
        col2.metric("Positive", len(df[df["sentiment"] == "positive"]))
        col3.metric("Neutral", len(df[df["sentiment"] == "neutral"]))
        col4.metric("Negative", len(df[df["sentiment"] == "negative"]))

        if len(df) >= 2:
            pulse_divider()
            st.markdown("### 📈 Sentiment Trend")
            df_chart = df.sort_values("date").copy()
            df_chart["polarity_smooth"] = df_chart["polarity"].rolling(window=min(3, len(df_chart)), min_periods=1).mean()
            fig = px.line(df_chart, x="date", y="polarity", markers=True,
                          title="Polarity Over Time", color_discrete_sequence=[COLOR_PRIMARY])
            fig.add_scatter(x=df_chart["date"], y=df_chart["polarity_smooth"],
                            mode="lines", name="Trend", line=dict(color=COLOR_MEDIUM, width=2))
            fig.add_hline(y=0, line_dash="dot", line_color=C['muted'], annotation_text="Neutral")
            st.plotly_chart(style_plot(fig), use_container_width=True)

        pulse_divider()
        st.markdown("### 📖 Your Entries")
        for idx, row in df.iterrows():
            sentiment_emoji = {"positive": "😊", "negative": "😔", "neutral": "😐"}.get(row["sentiment"], "😐")
            with st.container():
                c1, c2, c3 = st.columns([2, 1, 0.8])
                c1.markdown(f"**{row['date'].strftime('%Y-%m-%d %H:%M')}** · {sentiment_emoji} {row['sentiment'].title()}")
                c2.write(f"Polarity: {row['polarity']:.3f}")
                if c3.button("🗑️", key=f"del_journal_{row['id']}_{idx}", help="Delete this entry"):
                    delete_journal_entry(row["id"])
                    st.rerun()
            with st.expander("Read entry"):
                st.write(row["text"])
            st.markdown("---")

        pulse_divider()
        dl_col, clear_col = st.columns(2)
        with dl_col:
            st.download_button(
                "📥 Download My Journals (Excel)",
                data=export_journal_to_excel(username),
                file_name=f"{username}_journals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="myjournals_dl"
            )
        with clear_col:
            if st.button("🧹 Clear all my journals", use_container_width=True, key="myjournals_clear"):
                delete_all_journal_entries(username)
                st.success("All journal entries cleared.")
                st.rerun()

# ═══════════════════════════════════════════════════════════════
# MY ENTRIES PAGE
# ═══════════════════════════════════════════════════════════════
elif page == "🗂️ My Entries":
    require_login()
    page_header("🗂️", "Your Data", "My Entries", "Review, correct, or remove your own check-in history.")

    username = st.text_input("👤 Enter your name to view your entries", value=st.session_state.get("current_user", "Guest User"), key="myentries_username")
    df = get_history_data()
    mine = df[df["username"].astype(str) == username].sort_values("date", ascending=False) if not df.empty else df

    if mine.empty:
        st.info("No entries found for this name yet.")
    else:
        st.caption(f"{len(mine)} entries found for **{username}**.")
        for idx, row in mine.iterrows():
            c1, c2, c3, c4, c5 = st.columns([2, 1.2, 1, 1.2, 0.8])
            c1.markdown(f"**{row['date'].strftime('%Y-%m-%d %H:%M')}**")
            c2.write(f"Mood: {row['mood']}")
            c3.write(f"😴 {row['sleep_hours']:.0f}h")
            c4.write(f"Wellness: {row['wellness_score']:.0f}/100")
            if c5.button("🗑️", key=f"del_entry_{row['id']}_{idx}", help="Delete this entry"):
                delete_entry(row["id"])
                st.rerun()

        pulse_divider()
        st.download_button(
            "📥 Download My Data (Excel)",
            data=export_to_excel(mine.drop(columns=["mood_num"], errors="ignore"), sheet_name="My History"),
            file_name=f"{username}_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="myentries_dl"
        )
        if st.button("🧹 Clear all my entries", use_container_width=True, key="myentries_clear"):
            delete_all_entries(username)
            st.success("All entries cleared.")
            st.rerun()

# ═══════════════════════════════════════════════════════════════
# SUPPORT & COPING PAGE
# ═══════════════════════════════════════════════════════════════
elif page == "🆘 Support & Coping":
    require_login()
    page_header("🆘", "Take a Moment", "Support & Coping Toolkit", "Tools for right now, and where to go for more support.")

    st.markdown("### 🫁 Guided Breathing")
    st.caption("Box breathing: in for 4s, hold 4s, out for 4s, hold 4s. Follow the circle.")
    st.markdown('<div class="breathing-circle-wrap"><div class="breathing-circle"></div></div>', unsafe_allow_html=True)

    pulse_divider()
    st.markdown("### 🌱 Grounding: 5-4-3-2-1")
    st.write("Name to yourself: 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste.")

    pulse_divider()
    st.markdown("### 📝 Journaling Prompts")
    prompts = [
        "What is one thing that felt hard today, and one thing that helped?",
        "What would I tell a friend who felt the way I feel right now?",
        "What is one small thing I can do in the next hour to take care of myself?",
    ]
    for p in prompts:
        st.info(p)

    pulse_divider()
    st.markdown("### 📞 If You Need to Talk to Someone")
    st.error("**India: 14416 Suicide & Crisis Lifeline** — call or text **14416**, available 24/7.")
    st.warning("**Crisis Text Line** — text **HOME** to **tel:78930-78930** (India).")
    st.info("**Outside the India** — search \"[your country] crisis helpline\" or contact local emergency services.")
    st.caption(
        "MindTrack is a self-reflection tool, not a diagnostic service or emergency line. "
        "If you are in immediate danger, please contact local emergency services right away."
    )

# ═══════════════════════════════════════════════════════════════
# REPORT PAGE
# ═══════════════════════════════════════════════════════════════
elif page == "📄 Report":
    require_login()
    page_header("📄", "Documentation", "Health Report", "A shareable summary of your latest assessment.")

    if 'assessment_data' not in st.session_state:
        st.warning("⚠️ Please complete the Assessment first!")
    else:
        data = st.session_state['assessment_data']
        username = data["username"]
        stress, sleep = data["stress_level"], data["sleep_hours"]
        anxiety, exercise = data["anxiety_level"], data["exercise_minutes"]
        mood = data["mood"]
        social_connection = data.get("social_connection", 5)
        screen_time = data.get("screen_time", 4)
        caffeine_intake = data.get("caffeine_intake", 2)
        water_intake = data.get("water_intake", 6)
        sunlight_exposure = data.get("sunlight_exposure", 30)
        work_life_balance = data.get("work_life_balance", 5)

        risk, factors, wellness_score = predict_risk(stress, sleep, anxiety, exercise, mood,
                                                      social_connection, screen_time, caffeine_intake,
                                                      water_intake, sunlight_exposure, work_life_balance)
        recommendations = get_recommendations(stress, sleep, anxiety, exercise, social_connection,
                                               screen_time, caffeine_intake, water_intake,
                                               sunlight_exposure, work_life_balance)

        st.markdown("## 📋 Report Preview")
        st.markdown(f"**👤 Username:** {username}")
        risk_badge(risk)
        st.metric("🏆 Wellness Score", f"{wellness_score}/100")

        st.markdown("## 🔍 Key Factors")
        for factor in factors:
            st.info(f"• {factor}")

        st.markdown("## 💡 Recommendations")
        for rec in recommendations:
            st.success(rec)

        pdf_buffer = generate_pdf_report(username, risk, wellness_score, factors, recommendations)
        st.download_button("📥 Download PDF Report", data=pdf_buffer,
                            file_name=f"mental_health_report_{username}.pdf", mime="application/pdf",
                            key="report_dl_pdf")

# ═══════════════════════════════════════════════════════════════
# AI INSIGHTS PAGE
# ═══════════════════════════════════════════════════════════════
elif page == "🧠 AI Insights":
    require_login()
    page_header("🧠", "Intelligence", "AI Wellness Insights",
                "Pattern recognition, predictive analysis, and personalized intelligence for your wellness journey.")

    username = st.text_input("👤 Analyze data for", value=st.session_state.get("current_user", "Guest User"), key="ai_username")

    hist = get_history_data()
    mine = hist[hist["username"].astype(str) == username].sort_values("date") if not hist.empty else hist

    if mine.empty or len(mine) < 2:
        st.info("📭 Not enough data for AI analysis yet. Complete at least 2 assessments to unlock insights.")
        if not SKLEARN_AVAILABLE:
            st.warning("⚠️ scikit-learn is not installed. Run `pip install scikit-learn` to enable full AI features.")
        st.stop()

    # AI Narrative
    st.markdown("## 📝 Your Wellness Story")
    narrative = generate_ai_narrative(mine, username)
    card_bg = C["card"]
    border_color = C["border"]
    text_color = C["ink"]
    st.markdown(
        f'<div style="background:{card_bg};border:1px solid {border_color};'
        f'border-radius:12px;padding:20px;line-height:1.7;font-size:1rem;'
        f'color:{text_color};">{narrative}</div>',
        unsafe_allow_html=True
    )
    pulse_divider()

    # Trend Analysis
    trends = detect_trends(mine)
    if trends:
        st.markdown("## 📈 Trend Analysis")
        trend_df_data = []
        for metric, data in trends.items():
            trend_df_data.append({
                "Metric": metric.replace("_", " ").title(),
                "Direction": data["direction"].capitalize(),
                "Slope": round(data["slope"], 3),
                "Reliability (R²)": round(data["r2"], 2),
            })
        trend_df = pd.DataFrame(trend_df_data)

        def color_direction(val):
            if val == "Improving":
                return f"color: {COLOR_GOOD}; font-weight: 600;"
            elif val == "Declining":
                return f"color: {COLOR_HIGH}; font-weight: 600;"
            return f"color: {COLOR_MEDIUM};"

        try:
            styled = trend_df.style.map(color_direction, subset=["Direction"])
        except AttributeError:
            styled = trend_df.style.applymap(color_direction, subset=["Direction"])
        st.dataframe(styled, use_container_width=True)
        pulse_divider()

    # Correlation Insights
    correlations = find_key_correlations(mine)
    if correlations:
        st.markdown("## 🔗 Hidden Patterns in Your Data")
        st.caption("Factors that move together in your personal history")

        col1, col2 = st.columns([1.2, 1])
        with col1:
            corr_net = create_correlation_network(mine)
            if corr_net:
                st.plotly_chart(corr_net, use_container_width=True)

        with col2:
            st.markdown("### Top Correlations")
            for i, corr in enumerate(correlations[:4], 1):
                emoji = "🟢" if corr["direction"] == "positive" else "🔴"
                st.markdown(
                    f"{emoji} **{corr['factor_a'].replace('_', ' ').title()}** ↔ "
                    f"**{corr['factor_b'].replace('_', ' ').title()}**  <br>"
                    f"<span style='font-family: IBM Plex Mono; font-size: 0.8rem; color: {C['muted']};'>"
                    f"r = {corr['correlation']} ({corr['strength']} {corr['direction']})</span>",
                    unsafe_allow_html=True
                )
        pulse_divider()

    # Anomaly Detection
    anomalies = detect_anomalies(mine)
    if anomalies:
        st.markdown("## ⚠️ Recent Anomalies Detected")
        for anom in anomalies:
            severity_color = COLOR_HIGH if anom["severity"] == "high" else COLOR_MEDIUM
            st.markdown(
                f'<div style="border-left: 4px solid {severity_color}; padding-left: 12px; margin-bottom: 8px;">'
                f'<strong>{anom["metric"].replace("_", " ").title()}</strong> — '
                f'{anom["direction"].title()} to <strong>{anom["value"]:.1f}</strong> '
                f'(Z-score: {anom["z_score"]})</div>',
                unsafe_allow_html=True
            )
        pulse_divider()

    # Predictive Forecast
    st.markdown("## 🔮 Predictive Wellness Forecast")
    pred_chart = create_trend_visualization(mine)
    if pred_chart:
        st.plotly_chart(pred_chart, use_container_width=True)
        prediction = predict_next_wellness(mine)
        if prediction is not None:
            latest_score = mine.iloc[-1]["wellness_score"]
            diff = prediction - latest_score
            delta_color = "normal" if diff > 0 else "inverse"
            st.metric("Predicted Next Wellness Score", f"{prediction}/100",
                     f"{diff:+.0f} from current", delta_color=delta_color)
    else:
        st.info("Need more data to generate predictions. Keep logging your assessments!")
    pulse_divider()

    # Smart Recommendations
    st.markdown("## 💡 AI-Generated Recommendations")
    smart_recs = generate_smart_recommendations(mine, trends, correlations, anomalies)
    for rec in smart_recs:
        st.success(rec)

    # Factor Importance (Feature Weights)
    if len(mine) >= 5 and SKLEARN_AVAILABLE:
        st.markdown("## 🎯 What Drives Your Wellness Score?")
        features = ["sleep_hours", "stress_level", "anxiety_level", "exercise_minutes",
                    "social_connection", "screen_time", "caffeine_intake", "water_intake",
                    "sunlight_exposure", "work_life_balance"]
        available = [c for c in features if c in mine.columns]
        if len(available) >= 3:
            X = mine[available].fillna(mine[available].median()).values
            y = mine["wellness_score"].values
            model = LinearRegression()
            model.fit(X, y)

            importance_df = pd.DataFrame({
                "Factor": [c.replace("_", " ").title() for c in available],
                "Impact on Wellness": model.coef_,
                "Abs Impact": np.abs(model.coef_)
            }).sort_values("Abs Impact", ascending=True)

            fig_imp = px.bar(importance_df, x="Impact on Wellness", y="Factor", orientation="h",
                            title="Factor Importance (How Much Each Affects Your Score)",
                            color="Impact on Wellness", color_continuous_scale=[COLOR_HIGH, COLOR_MEDIUM, COLOR_GOOD])
            fig_imp.update_layout(showlegend=False, yaxis_title="")
            st.plotly_chart(style_plot(fig_imp), use_container_width=True)

            top_driver = importance_df.iloc[-1]["Factor"]
            st.info(f"🎯 **Key Insight:** **{top_driver}** has the strongest influence on your personal wellness score. Small improvements here may have the biggest impact.")

# ═══════════════════════════════════════════════════════════════
# ADMIN PAGE
# ═══════════════════════════════════════════════════════════════
elif page == "📊 Admin":
    require_login()
    page_header("📊", "Back Office", "Admin Dashboard", "Manage and export the underlying data.")

    st.markdown("## 📁 Data Management")
    st.caption(f"Backed by a SQL database (SQLite) at `{DB_PATH}`.")
    init_db()

    col1, col2 = st.columns(2)
    with col1:
        try:
            conn = get_connection()
            df_history = pd.read_sql_query("SELECT * FROM user_history", conn)
            conn.close()
            st.markdown("### 👥 User History Data")
            st.dataframe(df_history, use_container_width=True)
            st.metric("Total Entries", len(df_history))
            if not df_history.empty:
                st.download_button("📥 Download Patient History (Excel)",
                                    data=export_to_excel(df_history, sheet_name="Patient History"),
                                    file_name=f"patient_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key="admin_dl_history")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    with col2:
        try:
            conn = get_connection()
            df_predictions = pd.read_sql_query("SELECT * FROM predictions", conn)
            conn.close()
            st.markdown("### 🤖 Predictions Data")
            st.dataframe(df_predictions, use_container_width=True)
            st.metric("Total Predictions", len(df_predictions))
            if not df_predictions.empty:
                st.download_button("📥 Download Predictions (Excel)",
                                    data=export_to_excel(df_predictions, sheet_name="Predictions"),
                                    file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key="admin_dl_predictions")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    pulse_divider()
    st.markdown("### 🎯 Saved Goals")
    try:
        conn = get_connection()
        df_goals = pd.read_sql_query("SELECT * FROM goals", conn)
        conn.close()
        st.dataframe(df_goals, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Error: {e}")
