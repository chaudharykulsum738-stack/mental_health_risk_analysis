import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import random
import sqlite3
import hashlib
import uuid
import re
import io
from datetime import datetime, timedelta
from textblob import TextBlob
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors as rl_colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

st.set_page_config(page_title="MindTrack | Wellness Intelligence", page_icon="🧠", layout="wide")

COLOR_INK = "#1B2430"
COLOR_MUTED = "#5B6B6A"
COLOR_BG = "#F4F6F5"
COLOR_CARD = "#FFFFFF"
COLOR_BORDER = "rgba(27,36,48,0.10)"
COLOR_PRIMARY = "#2F6F62"
COLOR_PRIMARY_LIGHT = "#4C9A79"
COLOR_SLATE = "#5C7A8A"
COLOR_GOOD = "#4C9A79"
COLOR_MEDIUM = "#D9A441"
COLOR_HIGH = "#C1554A"
CHART_PALETTE = [COLOR_PRIMARY, COLOR_MEDIUM, COLOR_HIGH, COLOR_SLATE, COLOR_PRIMARY_LIGHT, "#8B5E3C"]
RISK_COLOR_MAP = {"Low": COLOR_GOOD, "Medium": COLOR_MEDIUM, "High": COLOR_HIGH}

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
.stMarkdown, .stMarkdown p, label, .stText, .stCaption {{ color: var(--muted) !important; }}
[data-testid="stSidebar"] {{ background: var(--ink); border-right: 1px solid rgba(255,255,255,0.06); }}
[data-testid="stSidebar"] * {{ color: #EDEFEE !important; }}
.sidebar-brand {{
    font-family: 'Fraunces', serif; font-size: 1.55rem; font-weight: 700; color: #fff !important;
    margin: 0.2rem 0 0.1rem 0; display: flex; align-items: center; gap: 8px;
}}
.sidebar-tagline {{
    font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--primary-light) !important; margin-bottom: 1.5rem;
}}
[data-testid="stSidebar"] div[role="radiogroup"] label {{
    background: rgba(255,255,255,0.035); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 9px 14px; margin-bottom: 6px; transition: all 0.15s ease;
}}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
    background: rgba(255,255,255,0.09); border-color: var(--primary-light);
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
    background: #fff; color: var(--primary); border: 1.5px solid var(--primary); border-radius: 8px; font-weight: 600;
}}
.stDownloadButton > button:hover {{ background: var(--primary); color: #fff; }}
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
    background: #fff; border: 1px solid rgba(27,36,48,0.10);
    border-radius: 14px; text-align: center;
}}
.login-icon {{ font-size: 3rem; margin-bottom: 0.5rem; }}
.login-title {{
    font-family: 'Fraunces', serif; font-size: 1.6rem;
    color: var(--ink); margin-bottom: 0.3rem;
}}
.login-sub {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 1.5rem; }}
.user-pill {{
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(47,111,98,0.10); border: 1px solid rgba(47,111,98,0.25);
    color: var(--primary); border-radius: 999px;
    padding: 5px 14px; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem; font-weight: 600;
}}
.lock-screen {{ text-align: center; padding: 3rem 1rem; }}
.lock-screen h2 {{ font-family: 'Fraunces', serif; color: var(--ink); }}
.mind-card {{
    background: {COLOR_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 14px;
    box-shadow: 0 3px 12px rgba(27,36,48,0.04);
}}
.trust-card {{
    background: #F8FBFA;
    border-left: 4px solid {COLOR_PRIMARY};
    padding: 16px;
    border-radius: 10px;
    margin: 10px 0;
}}
.warning-card {{
    background: #FFF9EC;
    border-left: 4px solid {COLOR_MEDIUM};
    padding: 16px;
    border-radius: 10px;
}}
.risk-card {{
    padding: 18px;
    border-radius: 14px;
    margin: 10px 0;
}}
.risk-low {{
    background: rgba(76,154,121,0.10);
    border: 1px solid rgba(76,154,121,0.25);
}}
.risk-medium {{
    background: rgba(217,164,65,0.10);
    border: 1px solid rgba(217,164,65,0.25);
}}
.risk-high {{
    background: rgba(193,85,74,0.10);
    border: 1px solid rgba(193,85,74,0.25);
}}
.small-muted {{
    color: {COLOR_MUTED};
    font-size: 0.85rem;
}}
.feature-tag {{
    display: inline-block;
    background: rgba(47,111,98,0.10);
    color: {COLOR_PRIMARY};
    padding: 5px 9px;
    border-radius: 20px;
    margin: 3px;
    font-size: 0.8rem;
}}
.chat-user {{
    background: #E8F2EF;
    padding: 12px;
    border-radius: 12px;
    margin: 8px 0;
}}
.chat-bot {{
    background: white;
    border: 1px solid {COLOR_BORDER};
    padding: 12px;
    border-radius: 12px;
    margin: 8px 0;
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

def safe_text(value):
    return str(value).replace("<", "&lt;").replace(">", "&gt;")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "mental_health.db")
JOURNAL_CSV = os.path.join(DATA_DIR, "journal_entries.csv")
AUDIT_CSV = os.path.join(DATA_DIR, "audit_log.csv")

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            user_hash TEXT,
            date TEXT,
            mood TEXT,
            sleep_hours REAL,
            stress_level REAL,
            anxiety_level REAL,
            exercise_minutes REAL,
            journal_sentiment TEXT,
            journal_polarity REAL,
            data_completeness REAL,
            confidence_score REAL,
            demographic_group TEXT,
            consent_analytics INTEGER DEFAULT 1
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            user_hash TEXT,
            date TEXT,
            risk_level TEXT,
            wellness_score REAL,
            factors TEXT,
            trajectory TEXT,
            trajectory_change REAL,
            confidence_score REAL,
            modality_count INTEGER DEFAULT 1,
            missing_fields TEXT,
            human_status TEXT DEFAULT 'Pending',
            reviewer TEXT,
            reviewer_note TEXT,
            reviewed_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            username TEXT PRIMARY KEY,
            target_sleep REAL,
            target_exercise REAL,
            target_stress_max REAL,
            updated_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS privacy_preferences (
            username TEXT PRIMARY KEY,
            consent_storage INTEGER DEFAULT 1,
            consent_analytics INTEGER DEFAULT 1,
            consent_research INTEGER DEFAULT 0,
            pseudonymous_mode INTEGER DEFAULT 1,
            updated_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS review_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id INTEGER,
            username TEXT,
            created_at TEXT,
            reason TEXT,
            status TEXT DEFAULT 'Pending',
            reviewer TEXT,
            reviewer_note TEXT,
            reviewed_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def hash_user(username):
    value = str(username).strip().lower()
    salt = os.environ.get("MINDTRACK_HASH_SALT", "development-only-change-this-salt")
    return hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()[:24]

def privacy_mode_enabled(username):
    conn = get_connection()
    row = conn.execute("SELECT pseudonymous_mode FROM privacy_preferences WHERE username=?", (username,)).fetchone()
    conn.close()
    if row is None:
        return True
    return bool(row["pseudonymous_mode"])

def audit_event(username, action, details=""):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "username_hash": hash_user(username),
        "action": action,
        "details": details,
    }
    new_df = pd.DataFrame([entry])
    if os.path.exists(AUDIT_CSV):
        old_df = pd.read_csv(AUDIT_CSV)
        df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        df = new_df
    df.to_csv(AUDIT_CSV, index=False)

def save_privacy_preferences(username, consent_storage, consent_analytics, consent_research, pseudonymous_mode):
    conn = get_connection()
    conn.execute("""
        INSERT INTO privacy_preferences (username, consent_storage, consent_analytics, consent_research, pseudonymous_mode, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            consent_storage=excluded.consent_storage,
            consent_analytics=excluded.consent_analytics,
            consent_research=excluded.consent_research,
            pseudonymous_mode=excluded.pseudonymous_mode,
            updated_at=excluded.updated_at
    """, (username, int(consent_storage), int(consent_analytics), int(consent_research), int(pseudonymous_mode), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    audit_event(username, "privacy_preferences_updated", "Consent and privacy settings changed.")

def get_privacy_preferences(username):
    conn = get_connection()
    row = conn.execute("SELECT * FROM privacy_preferences WHERE username=?", (username,)).fetchone()
    conn.close()
    if row is None:
        return {"consent_storage": 1, "consent_analytics": 1, "consent_research": 0, "pseudonymous_mode": 1}
    return dict(row)

def save_goals(username, target_sleep, target_exercise, target_stress_max):
    conn = get_connection()
    conn.execute("""
        INSERT INTO goals (username, target_sleep, target_exercise, target_stress_max, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            target_sleep=excluded.target_sleep,
            target_exercise=excluded.target_exercise,
            target_stress_max=excluded.target_stress_max,
            updated_at=excluded.updated_at
    """, (username, target_sleep, target_exercise, target_stress_max, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_goals(username):
    conn = get_connection()
    row = conn.execute("SELECT * FROM goals WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None

def init_login_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None

def login_user(username):
    st.session_state.logged_in = True
    st.session_state.current_user = username.strip()
    audit_event(username.strip(), "login", "User signed in.")

def logout_user():
    user = st.session_state.get("current_user")
    if user:
        audit_event(user, "logout", "User signed out.")
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state["page_radio"] = "🏠 Home"

def require_login():
    init_login_state()
    if not st.session_state.logged_in:
        st.markdown("""
        <div class="lock-screen">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔒</div>
            <h2>Please Sign In</h2>
            <p>You need to sign in to access this page.</p>
            <p>Go to <b>🏠 Home</b> to sign in.</p>
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
        username = st.text_input("Your name", placeholder="Enter your name")
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
            <span class="user-pill">👤 {safe_text(st.session_state.current_user)}</span>
        </div>
        """, unsafe_allow_html=True)
        if st.sidebar.button("🚪 Log out", use_container_width=True):
            logout_user()
            st.rerun()
        st.sidebar.markdown("---")

def calculate_wellness_score(stress, sleep, anxiety, exercise):
    components = []
    if stress is not None:
        components.append((10 - float(stress)) * 5)
    if sleep is not None:
        components.append(min(float(sleep), 10) * 3)
    if anxiety is not None:
        components.append((10 - float(anxiety)) * 5)
    if exercise is not None:
        components.append(min(float(exercise), 120) / 2)
    if not components:
        return None
    score = sum(components)
    return round(min(max(score, 0), 100), 1)

def calculate_completeness(sleep, stress, anxiety, exercise, mood, journal_text=None):
    fields = [sleep, stress, anxiety, exercise, mood]
    total = len(fields)
    present = sum(value is not None and str(value).strip() != "" for value in fields)
    if journal_text is not None:
        total += 1
        if str(journal_text).strip():
            present += 1
    return round(present / total * 100, 1)

def missing_data_intelligence(sleep, stress, anxiety, exercise, mood, journal_text=None):
    fields = {"sleep": sleep, "stress": stress, "anxiety": anxiety, "exercise": exercise, "mood": mood}
    missing = [name for name, value in fields.items() if value is None]
    if journal_text is not None and not str(journal_text).strip():
        missing.append("journal/text")
    completeness = calculate_completeness(sleep, stress, anxiety, exercise, mood, journal_text)
    if completeness >= 90:
        confidence = 0.95
        interpretation = "High data completeness"
    elif completeness >= 70:
        confidence = 0.80
        interpretation = "Moderate data completeness"
    elif completeness >= 50:
        confidence = 0.60
        interpretation = "Limited data completeness"
    else:
        confidence = 0.40
        interpretation = "Very limited data"
    return {"missing": missing, "completeness": completeness, "confidence": confidence, "interpretation": interpretation}

def save_user_history(username, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes, entry_date=None, journal_sentiment=None, journal_polarity=None, demographic_group=None):
    preferences = get_privacy_preferences(username)
    if not preferences["consent_storage"]:
        return False
    if entry_date is None:
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        date_str = datetime.combine(entry_date, datetime.now().time()).strftime("%Y-%m-%d %H:%M:%S")
    missing = missing_data_intelligence(sleep_hours, stress_level, anxiety_level, exercise_minutes, mood)
    conn = get_connection()
    conn.execute("""
        INSERT INTO user_history (username, user_hash, date, mood, sleep_hours, stress_level, anxiety_level,
            exercise_minutes, journal_sentiment, journal_polarity, data_completeness, confidence_score,
            demographic_group, consent_analytics)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, hash_user(username), date_str, mood, sleep_hours, stress_level, anxiety_level,
          exercise_minutes, journal_sentiment, journal_polarity, missing["completeness"],
          missing["confidence"], demographic_group, preferences["consent_analytics"]))
    conn.commit()
    conn.close()
    audit_event(username, "assessment_created", "New wellness check-in stored.")
    return True

def delete_entry(entry_id):
    conn = get_connection()
    row = conn.execute("SELECT username FROM user_history WHERE id=?", (int(entry_id),)).fetchone()
    conn.execute("DELETE FROM user_history WHERE id=?", (int(entry_id),))
    conn.commit()
    conn.close()
    if row:
        audit_event(row["username"], "assessment_deleted", f"History ID {entry_id} deleted.")

def delete_all_entries(username):
    conn = get_connection()
    conn.execute("DELETE FROM user_history WHERE username=?", (username,))
    conn.commit()
    conn.close()
    audit_event(username, "all_assessments_deleted", "All assessment history deleted.")

def save_journal_entry(username, text, sentiment, polarity):
    preferences = get_privacy_preferences(username)
    if not preferences["consent_storage"]:
        return None
    entry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "username": username,
        "username_hash": hash_user(username),
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
    audit_event(username, "journal_created", "Journal entry stored.")
    return entry

def get_journal_entries(username=None):
    if not os.path.exists(JOURNAL_CSV):
        return pd.DataFrame(columns=["id", "username", "username_hash", "date", "text", "sentiment", "polarity"])
    df = pd.read_csv(JOURNAL_CSV)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if username:
        df = df[df["username"].astype(str) == str(username)]
    return df.sort_values("date", ascending=False).reset_index(drop=True)

def delete_journal_entry(entry_id):
    if not os.path.exists(JOURNAL_CSV):
        return
    df = pd.read_csv(JOURNAL_CSV)
    username = None
    matching = df[df["id"].astype(str) == str(entry_id)]
    if not matching.empty:
        username = matching.iloc[0]["username"]
    df = df[df["id"].astype(str) != str(entry_id)]
    df.to_csv(JOURNAL_CSV, index=False)
    if username:
        audit_event(username, "journal_deleted", f"Journal ID {entry_id} deleted.")

def delete_all_journal_entries(username):
    if not os.path.exists(JOURNAL_CSV):
        return
    df = pd.read_csv(JOURNAL_CSV)
    df = df[df["username"].astype(str) != str(username)]
    df.to_csv(JOURNAL_CSV, index=False)
    audit_event(username, "all_journals_deleted", "All journal entries deleted.")

def export_journal_to_excel(username=None):
    df = get_journal_entries(username)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Journal Entries")
    buffer.seek(0)
    return buffer

def analyze_sentiment(text):
    if not text or not text.strip():
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

def analyze_text_modality(text):
    if not text:
        return {"available": False, "sentiment": "neutral", "polarity": 0.0, "safety_signal": "none"}
    sentiment, polarity = analyze_sentiment(text)
    lower = text.lower()
    crisis_patterns = [r"\bsuicide\b", r"\bkill myself\b", r"\bend my life\b", r"\bhurt myself\b", r"\bself harm\b", r"\bself-harm\b"]
    urgent = any(re.search(pattern, lower) for pattern in crisis_patterns)
    return {
        "available": True,
        "sentiment": sentiment,
        "polarity": polarity,
        "safety_signal": "urgent_language" if urgent else "none",
    }

def analyze_structured_modality(stress, anxiety, sleep, exercise, mood):
    score = calculate_wellness_score(stress, sleep, anxiety, exercise)
    return {
        "available": True,
        "wellness_score": score,
        "mood": mood,
        "stress": stress,
        "anxiety": anxiety,
        "sleep": sleep,
        "exercise": exercise,
    }

def analyze_uploaded_signal(uploaded_file):
    if uploaded_file is None:
        return {"available": False, "signals": {}}
    try:
        name = uploaded_file.name.lower()
        if name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif name.endswith(".json"):
            content = uploaded_file.read()
            data = json.loads(content)
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])
        else:
            return {"available": False, "signals": {}, "error": "Only CSV and JSON are supported."}
        signals = {}
        numeric_columns = ["heart_rate", "steps", "screen_time", "sleep_quality", "activity_level"]
        for column in numeric_columns:
            if column in df.columns:
                numeric = pd.to_numeric(df[column], errors="coerce")
                if numeric.notna().any():
                    signals[column] = round(float(numeric.mean()), 2)
        return {"available": bool(signals), "signals": signals, "rows": len(df)}
    except Exception as exc:
        return {"available": False, "signals": {}, "error": str(exc)}

def multimodal_risk_analysis(stress, sleep, anxiety, exercise, mood, journal_text=None, uploaded_signal=None):
    structured = analyze_structured_modality(stress, anxiety, sleep, exercise, mood)
    text = analyze_text_modality(journal_text)
    extra = analyze_uploaded_signal(uploaded_signal)
    modalities = [structured["available"], text["available"], extra["available"]]
    modality_count = sum(modalities)
    risk, factors, score = predict_risk(stress, sleep, anxiety, exercise, mood)
    if text["available"]:
        if text["polarity"] < -0.4:
            factors.append("Journal language shows strongly negative sentiment")
        elif text["polarity"] > 0.4:
            factors.append("Journal language shows positive sentiment")
    if extra["available"]:
        factors.append("Additional contextual data was incorporated")
    if text["safety_signal"] == "urgent_language":
        factors.append("Safety-related language detected; human review is recommended")
    return {
        "risk": risk,
        "factors": list(dict.fromkeys(factors)),
        "wellness_score": score,
        "structured": structured,
        "text": text,
        "extra": extra,
        "modality_count": modality_count,
    }

def predict_risk(stress, sleep, anxiety, exercise, mood):
    wellness_score = calculate_wellness_score(stress, sleep, anxiety, exercise)
    if wellness_score is None:
        return "Unknown", ["Insufficient information"], None
    if wellness_score < 40:
        risk = "High"
    elif wellness_score < 70:
        risk = "Medium"
    else:
        risk = "Low"
    factors = []
    if stress is not None and stress > 7:
        factors.append("High self-reported stress")
    if sleep is not None and sleep < 6:
        factors.append("Low reported sleep duration")
    if anxiety is not None and anxiety > 7:
        factors.append("High self-reported anxiety")
    if exercise is not None and exercise < 30:
        factors.append("Low physical activity")
    if mood in ["Very Bad", "Bad"]:
        factors.append("Low self-reported mood")
    if not factors:
        factors.append("No major unfavorable indicators in the submitted check-in")
    return risk, factors, wellness_score

def save_prediction(username, risk_level, wellness_score, factors, trajectory="Stable", trajectory_change=0, confidence_score=0.5, modality_count=1, missing_fields=None):
    conn = get_connection()
    conn.execute("""
        INSERT INTO predictions (username, user_hash, date, risk_level, wellness_score, factors,
            trajectory, trajectory_change, confidence_score, modality_count, missing_fields)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, hash_user(username), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), risk_level,
          wellness_score, json.dumps(factors), trajectory, trajectory_change, confidence_score,
          modality_count, json.dumps(missing_fields or [])))
    conn.commit()
    conn.close()
    audit_event(username, "prediction_created", f"Risk={risk_level}; trajectory={trajectory}")

def get_history_data():
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM user_history", conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["mood_num"] = mood_to_score(df["mood"])
    df["wellness_score"] = df.apply(
        lambda row: calculate_wellness_score(row["stress_level"], row["sleep_hours"], row["anxiety_level"], row["exercise_minutes"]),
        axis=1,
    )
    return df.dropna(subset=["date"])

def get_prediction_data():
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM predictions", conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    risk_map = {"Low": 1, "Medium": 2, "High": 3}
    df["risk_num"] = df["risk_level"].map(risk_map)
    return df.dropna(subset=["date"])

def calculate_risk_trajectory(df):
    if df is None or df.empty:
        return {"trajectory": "Insufficient data", "change": 0.0, "confidence": 0.0, "points": 0}
    d = df.sort_values("date").dropna(subset=["wellness_score"])
    if len(d) < 2:
        return {"trajectory": "Insufficient data", "change": 0.0, "confidence": 0.35, "points": len(d)}
    values = d["wellness_score"].astype(float).values
    if len(values) >= 5:
        recent = np.mean(values[-3:])
        previous = np.mean(values[-6:-3])
    else:
        recent = np.mean(values[-1:])
        previous = np.mean(values[:-1])
    change = float(recent - previous)
    if change <= -10:
        trajectory = "Worsening"
    elif change <= -3:
        trajectory = "Slightly worsening"
    elif change >= 10:
        trajectory = "Improving"
    elif change >= 3:
        trajectory = "Slightly improving"
    else:
        trajectory = "Stable"
    confidence = min(0.95, 0.35 + len(values) * 0.08)
    return {"trajectory": trajectory, "change": round(change, 2), "confidence": round(confidence, 2), "points": len(values)}

def trajectory_chart(df):
    d = df.sort_values("date").copy()
    if d.empty:
        return None
    fig = px.line(d, x="date", y="wellness_score", markers=True, title="Wellness Risk Trajectory",
                  color_discrete_sequence=[COLOR_PRIMARY])
    fig.add_hline(y=70, line_dash="dot", line_color=COLOR_GOOD, annotation_text="Higher wellness")
    fig.add_hline(y=40, line_dash="dot", line_color=COLOR_HIGH, annotation_text="Lower wellness")
    return style_plot(fig)

def missingness_explanation(missing):
    explanations = {
        "sleep": "Sleep is missing, so sleep-related wellness contribution is unavailable.",
        "stress": "Stress is missing, reducing confidence in the current wellness estimate.",
        "anxiety": "Anxiety is missing, reducing confidence in the overall assessment.",
        "exercise": "Exercise is missing, so activity-related context is unavailable.",
        "mood": "Mood is missing, reducing the ability to compare subjective well-being.",
        "journal/text": "No journal text was provided, so language-based context is unavailable.",
    }
    return [explanations[x] for x in missing if x in explanations]

def get_recommendations(stress, sleep, anxiety, exercise):
    recommendations = []
    if stress is not None and stress > 7:
        recommendations.extend([
            "🫁 Try slow breathing for 5 minutes.",
            "☕ Take short breaks from work or study.",
            "🌿 Try a brief mindfulness exercise.",
        ])
    if sleep is not None and sleep < 6:
        recommendations.extend([
            "🛏️ Consider a consistent sleep schedule.",
            "📵 Reduce stimulating screen use before bed.",
            "🌙 Create a relaxing bedtime routine.",
        ])
    if anxiety is not None and anxiety > 7:
        recommendations.extend([
            "🌱 Try a grounding exercise.",
            "📝 Write down worries and separate controllable from uncontrollable items.",
            "🤝 Consider talking with someone you trust.",
        ])
    if exercise is not None and exercise < 30:
        recommendations.extend([
            "🚶 Consider a short walk.",
            "🧘 Try gentle stretching.",
            "🏃 Add small amounts of movement throughout the day.",
        ])
    if not recommendations:
        recommendations.extend([
            "✅ Continue the routines that are working for you.",
            "🌱 Maintain regular sleep, movement, and social connection.",
        ])
    return recommendations

def create_review_item(prediction_id, username, reason):
    conn = get_connection()
    conn.execute("""
        INSERT INTO review_queue (prediction_id, username, created_at, reason, status)
        VALUES (?, ?, ?, ?, 'Pending')
    """, (prediction_id, username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), reason))
    conn.commit()
    conn.close()
    audit_event(username, "human_review_requested", reason)

def get_review_queue():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM review_queue ORDER BY created_at DESC", conn)
    conn.close()
    return df

def update_review(review_id, status, reviewer, note):
    conn = get_connection()
    row = conn.execute("SELECT username, prediction_id FROM review_queue WHERE id=?", (review_id,)).fetchone()
    if row:
        conn.execute("""
            UPDATE review_queue SET status=?, reviewer=?, reviewer_note=?, reviewed_at=?
            WHERE id=?
        """, (status, reviewer, note, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), review_id))
        conn.execute("""
            UPDATE predictions SET human_status=?, reviewer=?, reviewer_note=?, reviewed_at=?
            WHERE id=?
        """, (status, reviewer, note, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), row["prediction_id"]))
    conn.commit()
    conn.close()
    if row:
        audit_event(row["username"], "human_review_completed", f"Review {review_id}: {status}")

def fairness_audit(df):
    if df.empty:
        return pd.DataFrame()
    if "demographic_group" not in df.columns:
        return pd.DataFrame()
    d = df[df["demographic_group"].notna() & (df["demographic_group"].astype(str).str.strip() != "")].copy()
    if d.empty:
        return pd.DataFrame()
    summary = d.groupby("demographic_group").agg(
        records=("id", "count"),
        average_wellness=("wellness_score", "mean"),
        high_risk_rate=("risk_proxy", lambda x: (x == "High").mean() * 100),
        average_confidence=("confidence_score", "mean"),
    ).reset_index()
    return summary

def prepare_fairness_data(history_df):
    if history_df.empty:
        return history_df
    d = history_df.copy()
    d["risk_proxy"] = np.select(
        [d["wellness_score"] < 40, d["wellness_score"] < 70],
        ["High", "Medium"],
        default="Low",
    )
    if "confidence_score" not in d.columns:
        d["confidence_score"] = 0.5
    return d

def create_local_model_update(username):
    history = get_history_data()
    if history.empty:
        return None
    mine = history[history["username"].astype(str) == str(username)]
    if mine.empty:
        return None
    return {
        "user_hash": hash_user(username),
        "sample_count": len(mine),
        "mean_wellness": round(float(mine["wellness_score"].mean()), 2),
        "mean_stress": round(float(mine["stress_level"].mean()), 2),
        "mean_sleep": round(float(mine["sleep_hours"].mean()), 2),
        "mean_anxiety": round(float(mine["anxiety_level"].mean()), 2),
        "generated_at": datetime.now().isoformat(),
    }

def export_all_user_data(username):
    history = get_history_data()
    history_user = history[history["username"].astype(str) == str(username)] if not history.empty else pd.DataFrame()
    journals = get_journal_entries(username)
    goals = get_goals(username)
    predictions = get_prediction_data()
    predictions_user = predictions[predictions["username"].astype(str) == str(username)] if not predictions.empty else pd.DataFrame()
    privacy = get_privacy_preferences(username)
    return {
        "profile": {"username_hash": hash_user(username), "privacy": privacy},
        "history": history_user,
        "journals": journals,
        "predictions": predictions_user,
        "goals": pd.DataFrame([goals]) if goals else pd.DataFrame(),
    }

def create_user_export(username):
    data = export_all_user_data(username)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for name, value in data.items():
            if isinstance(value, pd.DataFrame):
                value.to_excel(writer, index=False, sheet_name=name[:31])
            elif isinstance(value, dict):
                pd.DataFrame([value]).to_excel(writer, index=False, sheet_name=name[:31])
    buffer.seek(0)
    audit_event(username, "data_export", "User downloaded personal data.")
    return buffer

def delete_all_user_data(username):
    conn = get_connection()
    conn.execute("DELETE FROM user_history WHERE username=?", (username,))
    conn.execute("DELETE FROM predictions WHERE username=?", (username,))
    conn.execute("DELETE FROM goals WHERE username=?", (username,))
    conn.execute("DELETE FROM privacy_preferences WHERE username=?", (username,))
    conn.execute("DELETE FROM review_queue WHERE username=?", (username,))
    conn.commit()
    conn.close()
    delete_all_journal_entries(username)
    audit_event(username, "all_user_data_deleted", "All stored user data removed.")

CRISIS_TERMS = ["suicide", "kill myself", "end my life", "want to die", "hurt myself", "self harm", "self-harm", "overdose"]
HIGH_DISTRESS_TERMS = ["can't cope", "cannot cope", "hopeless", "worthless", "panic attack", "extremely anxious"]

def chatbot_safety_gate(text):
    lower = text.lower()
    if any(term in lower for term in CRISIS_TERMS):
        return "urgent"
    if any(term in lower for term in HIGH_DISTRESS_TERMS):
        return "distress"
    return "normal"

def safe_chatbot_response(username, message):
    gate = chatbot_safety_gate(message)
    if gate == "urgent":
        return (
            "I'm really sorry you're dealing with something this intense. "
            "I can't assess or manage an emergency, but I can stay with you "
            "while you take a safety-focused next step. Please contact your "
            "local emergency service or a crisis service available in your "
            "country, and if possible move toward a trusted person rather "
            "than staying alone."
        )
    if gate == "distress":
        return (
            "That sounds really difficult. I can't diagnose what's happening, "
            "but we can focus on the next few minutes. Try putting both feet "
            "on the floor, taking five slow breaths, and identifying one "
            "person you could contact for support."
        )
    lower = message.lower()
    if "sleep" in lower or "tired" in lower:
        return (
            "If sleep has been difficult, consider keeping your wake time "
            "consistent, reducing stimulating screen use before bed, and "
            "using a short wind-down routine. You don't need to fix "
            "everything tonight."
        )
    if "anxious" in lower or "anxiety" in lower or "worried" in lower:
        return (
            "For a quick grounding exercise, name five things you can see, "
            "four things you can touch, three things you can hear, two things "
            "you can smell, and one thing you can taste."
        )
    if "stress" in lower or "stressed" in lower:
        return (
            "Let's make the next step small. Pick one task that matters, "
            "work on it for a few minutes, then take a short break. If the "
            "stress keeps feeling overwhelming, consider talking with "
            "someone you trust."
        )
    if "sad" in lower or "lonely" in lower:
        return (
            "I'm sorry you're feeling this way. A small connection can help: "
            "consider sending a simple message to someone you trust such as "
            "'I'm having a difficult day; could we talk?'"
        )
    return (
        "Thanks for sharing that. I can help you reflect on it, but I won't "
        "diagnose you or make clinical decisions. What feels like the "
        "smallest helpful step you could take right now?"
    )

def mood_to_score(series):
    mood_map = {"Very Bad": 1, "Bad": 2, "Neutral": 3, "Good": 4, "Very Good": 5}
    return series.map(mood_map)

def style_plot(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(27,36,48,0.02)",
        font={"color": COLOR_INK, "family": "Inter, sans-serif"},
        title_font={"family": "Fraunces, serif", "color": COLOR_INK, "size": 17},
        margin=dict(l=20, r=20, t=50, b=20),
        legend={"font": {"color": COLOR_MUTED}},
    )
    fig.update_xaxes(gridcolor="rgba(27,36,48,0.07)", color=COLOR_MUTED)
    fig.update_yaxes(gridcolor="rgba(27,36,48,0.07)", color=COLOR_MUTED)
    return fig

def gauge_figure(value, title, value_range=(0, 100), steps=None):
    if value is None:
        value = 0
    if steps is None:
        lo, hi = value_range
        span = hi - lo
        steps = [
            {"range": [lo, lo + span * 0.4], "color": COLOR_HIGH},
            {"range": [lo + span * 0.4, lo + span * 0.7], "color": COLOR_MEDIUM},
            {"range": [lo + span * 0.7, hi], "color": COLOR_GOOD},
        ]
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value, domain={"x": [0, 1], "y": [0, 1]},
        title={"text": title, "font": {"size": 20, "color": COLOR_INK, "family": "Fraunces, serif"}},
        number={"font": {"color": COLOR_INK, "family": "IBM Plex Mono, monospace"}},
        gauge={"axis": {"range": list(value_range), "tickwidth": 1, "tickcolor": COLOR_MUTED},
               "bar": {"color": COLOR_PRIMARY}, "bgcolor": "rgba(0,0,0,0)",
               "borderwidth": 1, "bordercolor": COLOR_BORDER, "steps": steps}
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color": COLOR_INK})
    return fig

def create_wellness_radar(sleep, stress, anxiety, exercise, mood):
    mood_scale = {"Very Bad": 2, "Bad": 4, "Neutral": 6, "Good": 8, "Very Good": 10}
    categories = ["Sleep", "Exercise", "Mood", "Stress Balance", "Anxiety Balance"]
    values = [
        min(float(sleep), 10),
        min(float(exercise) / 12, 10),
        mood_scale.get(mood, 6),
        10 - float(stress),
        10 - float(anxiety),
    ]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]], theta=categories + [categories[0]], fill="toself",
        name="Wellness Profile", line_color=COLOR_PRIMARY, fillcolor="rgba(47,111,98,0.20)",
    ))
    fig.update_layout(
        title="Wellness Profile",
        polar=dict(bgcolor="rgba(0,0,0,0)",
                   radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(color=COLOR_MUTED)),
                   angularaxis=dict(tickfont=dict(color=COLOR_INK))),
        showlegend=False,
    )
    return style_plot(fig)

def create_factor_bar(stress, sleep, anxiety, exercise):
    categories = ["Stress", "Sleep", "Anxiety", "Exercise"]
    actual_values = [stress, sleep, anxiety, exercise]
    healthy_targets = [3, 8, 3, 45]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Your Values", x=categories, y=actual_values, marker_color=COLOR_PRIMARY))
    fig.add_trace(go.Bar(name="Reference Target", x=categories, y=healthy_targets, marker_color=COLOR_SLATE))
    fig.update_layout(barmode="group", title="Current Factors vs Reference Targets")
    return style_plot(fig)

def create_mood_calendar(df, weeks=12):
    if df.empty:
        return None
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
        hovertext[weekday_idx, week_idx] = f"{day.strftime('%Y-%m-%d')}<br>{'Mood: %.1f' % val if not np.isnan(val) else 'No entry'}"
    fig = go.Figure(data=go.Heatmap(
        z=matrix, x=[f"W{i + 1}" for i in range(weeks)], y=weekday_labels,
        colorscale=[[0, COLOR_HIGH], [0.5, COLOR_MEDIUM], [1, COLOR_GOOD]],
        zmin=1, zmax=5, hoverinfo="text", text=hovertext,
        xgap=3, ygap=3, showscale=False,
    ))
    fig.update_layout(title=f"Mood Calendar — Last {weeks} Weeks")
    return style_plot(fig)

def generate_pdf_report(username, risk_level, wellness_score, factors, recommendations, trajectory=None, confidence=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    brand_color = rl_colors.HexColor(COLOR_PRIMARY)
    ink_color = rl_colors.HexColor(COLOR_INK)
    title_style = ParagraphStyle("CustomTitle", parent=styles["Heading1"], fontSize=24, spaceAfter=6,
                                  alignment=1, textColor=brand_color)
    story.append(Paragraph("MindTrack Wellness Report", title_style))
    story.append(Paragraph("MENTAL WELLNESS SELF-REFLECTION", ParagraphStyle(
        "Eyebrow", parent=styles["Normal"], fontSize=10, alignment=1,
        textColor=rl_colors.HexColor(COLOR_MUTED), spaceAfter=24)))
    story.append(Paragraph(f"For: {safe_text(username)}", styles["Heading2"]))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    story.append(Spacer(1, 20))
    info_style = ParagraphStyle("Info", parent=styles["Normal"], fontSize=12, spaceAfter=12, textColor=ink_color)
    story.append(Paragraph(f"Wellness signal: {wellness_score}/100", info_style))
    story.append(Paragraph(f"Risk band: {risk_level}", info_style))
    if trajectory:
        story.append(Paragraph(f"Trajectory: {trajectory}", info_style))
    if confidence is not None:
        story.append(Paragraph(f"Data confidence: {confidence:.0%}", info_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Key Factors", styles["Heading2"]))
    for factor in factors:
        story.append(Paragraph(f"- {safe_text(factor)}", info_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Suggestions", styles["Heading2"]))
    for recommendation in recommendations:
        story.append(Paragraph(f"- {safe_text(recommendation)}", info_style))
    story.append(Spacer(1, 24))
    footer_style = ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8,
                                   textColor=rl_colors.HexColor(COLOR_MUTED))
    story.append(Paragraph(
        "This report is a self-reflection and wellness summary. "
        "It is not a medical diagnosis, clinical risk assessment, "
        "or emergency service.", footer_style))
    doc.build(story)
    buffer.seek(0)
    return buffer

def export_to_excel(df, sheet_name="Data"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    buffer.seek(0)
    return buffer

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
    last_week = df[(df["date"].dt.date >= today - timedelta(days=13)) & (df["date"].dt.date <= today - timedelta(days=7))]
    this_avg = this_week["wellness_score"].mean() if not this_week.empty else None
    last_avg = last_week["wellness_score"].mean() if not last_week.empty else None
    return this_avg, last_avg

def trend_nudge(df):
    d = df.sort_values("date")
    if len(d) < 3:
        return False
    recent = d.tail(3)["wellness_score"].tolist()
    return recent[0] > recent[1] > recent[2] and recent[2] < 40

PAGES = [
    "🏠 Home", "📋 Assessment", "🤖 Risk Prediction", "🧭 Risk Trajectory",
    "🎯 Goals", "📂 Bulk Upload", "🧩 Multimodal Analysis", "📈 Dashboard",
    "📝 Journal", "📓 My Journals", "🗂️ My Entries", "🆘 Support & Coping",
    "💬 Safe Chatbot", "👩‍⚕️ Human Review", "⚖️ Fairness Audit",
    "🔐 Data Trust Center", "🌐 Privacy / Federated", "📄 Report", "📊 Admin"
]

st.sidebar.markdown("""
<div class="sidebar-brand">🧠 MindTrack</div>
<div class="sidebar-tagline">Wellness Intelligence</div>
""", unsafe_allow_html=True)

if 'nav_to' in st.session_state:
    _nav_map = {
        'assessment': "📋 Assessment", 'journal': "📝 Journal",
        'support': "🆘 Support & Coping", 'goals': "🎯 Goals",
    }
    if st.session_state['nav_to'] in _nav_map:
        st.session_state['page_radio'] = _nav_map[st.session_state['nav_to']]
    del st.session_state['nav_to']

page = st.sidebar.radio("Go to", PAGES, key="page_radio", label_visibility="collapsed")

show_user_badge()

st.sidebar.markdown("""
<div class="sidebar-disclaimer">
MindTrack supports self-reflection and is not a diagnostic or emergency tool.<br>
In crisis (US)? Call or text <b>988</b> — or see Support & Coping.
</div>
""", unsafe_allow_html=True)

if page == "🏠 Home":
    init_login_state()
    if not st.session_state.logged_in:
        show_login_page()
        st.stop()
    username = st.session_state.current_user
    st.markdown(f"""
    <div class="hero-wrap">
        <div class="hero-icon">🧠</div>
        <div class="hero-title">MindTrack</div>
        <div class="hero-tagline">Welcome back, {username}</div>
    </div>
    """, unsafe_allow_html=True)
    pulse_divider()
    st.markdown("""
    <div class="trust-card">
    <b>Research-gap features enabled</b><br>
    Multimodal analysis · Risk trajectory · Missing-data intelligence ·
    Human review · Fairness audit · Privacy foundation · Data Trust Center ·
    Safe chatbot
    </div>
    """, unsafe_allow_html=True)
    st.markdown("## ⚡ Quick Start")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 New Assessment", use_container_width=True):
            st.session_state['nav_to'] = 'assessment'
            st.rerun()
    with col2:
        if st.button("📝 Write Journal", use_container_width=True):
            st.session_state['nav_to'] = 'journal'
            st.rerun()
    with col3:
        if st.button("💬 Talk to Safe Chatbot", use_container_width=True):
            st.session_state["page_radio"] = "💬 Safe Chatbot"
            st.rerun()
    history = get_history_data()
    if not history.empty:
        mine = history[history["username"].astype(str) == str(username)].sort_values("date")
        if not mine.empty:
            dates = mine["date"].dt.date.tolist()
            current_streak, longest_streak = calculate_streaks(dates)
            st.markdown("## 📊 Your Snapshot")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Check-ins", len(mine))
            m2.metric("Avg Wellness", f"{mine['wellness_score'].mean():.0f}/100")
            m3.metric("Current Streak", f"{current_streak} days")
            m4.metric("Avg Sleep", f"{mine['sleep_hours'].mean():.1f}h")
            trajectory = calculate_risk_trajectory(mine)
            if trajectory["trajectory"] == "Worsening":
                st.warning(
                    "Your recent wellness indicators show a downward trend. "
                    "Consider checking in with someone you trust or using the "
                    "Support & Coping tools."
                )
            this_avg, last_avg = weekly_digest(mine)
            if this_avg is not None:
                st.markdown("#### This Week vs Last Week")
                delta_txt = f"{this_avg - last_avg:+.0f} vs last week" if last_avg is not None else "No prior week to compare"
                st.metric("This Week's Avg Wellness", f"{this_avg:.0f}/100", delta_txt)
    st.markdown("## 🌱 Daily Wellness Tip")
    tips = [
        "Take a short walk outside.", "Try two minutes of slow breathing.",
        "Drink some water.", "Send a message to someone you trust.",
        "Take a short screen break.", "Write down one thing that went well today.",
    ]
    st.info(random.choice(tips))

elif page == "📋 Assessment":
    require_login()
    page_header("📋", "DAILY CHECK-IN", "Mental Health Assessment", "A short self-reflection check-in.")
    username = st.session_state.current_user
    entry_date = st.date_input("📅 Assessment date", value=datetime.now().date())
    mood_emojis = {"Very Bad": "😢", "Bad": "😔", "Neutral": "😐", "Good": "😊", "Very Good": "😄"}
    mood = st.select_slider(
        "How is your mood today?",
        options=["Very Bad", "Bad", "Neutral", "Good", "Very Good"],
        value="Good",
        format_func=lambda x: f"{mood_emojis[x]} {x}",
    )
    col1, col2 = st.columns(2)
    with col1:
        sleep_hours = st.slider("😴 Sleep last night", 0, 12, 7)
        stress_level = st.slider("😰 Stress level", 0, 10, 3)
    with col2:
        anxiety_level = st.slider("😟 Anxiety level", 0, 10, 3)
        exercise_minutes = st.slider("🏃 Exercise today", 0, 180, 30)
    st.markdown("### Optional context")
    journal_context = st.text_area(
        "How would you describe your day?",
        height=140,
        placeholder="Optional — this is used only for text sentiment/context.",
    )
    st.markdown("### Optional demographic group")
    st.caption(
        "Only provide this if you have an appropriate research/privacy purpose. "
        "It is NOT used as an input to the wellness score."
    )
    demographic_group = st.text_input(
        "Demographic subgroup label (optional)",
        placeholder="e.g. Group A",
    )
    missing = missing_data_intelligence(
        sleep_hours, stress_level, anxiety_level, exercise_minutes, mood, journal_context,
    )
    c1, c2 = st.columns(2)
    c1.metric("Data completeness", f"{missing['completeness']:.0f}%")
    c2.metric("Estimated confidence", f"{missing['confidence']:.0%}")
    if missing["missing"]:
        st.warning("Missing context: " + ", ".join(missing["missing"]))
    preview = calculate_wellness_score(stress_level, sleep_hours, anxiety_level, exercise_minutes)
    st.metric("Preview Wellness Signal", f"{preview:.0f}/100")
    goals = get_goals(username)
    if goals:
        st.caption(
            f"🎯 Your goals: {goals['target_sleep']:.0f}h sleep · "
            f"{goals['target_exercise']:.0f} min exercise · stress under {goals['target_stress_max']:.0f}"
        )
    if st.button("✅ Submit Assessment", use_container_width=True):
        sentiment = None
        polarity = None
        if journal_context.strip():
            sentiment, polarity = analyze_sentiment(journal_context)
        saved = save_user_history(
            username, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes,
            entry_date=entry_date, journal_sentiment=sentiment, journal_polarity=polarity,
            demographic_group=(demographic_group.strip() or None),
        )
        if saved:
            st.session_state["assessment_data"] = {
                "username": username, "date": entry_date, "mood": mood,
                "sleep_hours": sleep_hours, "stress_level": stress_level,
                "anxiety_level": anxiety_level, "exercise_minutes": exercise_minutes,
                "journal_text": journal_context,
            }
            st.success("Assessment saved.")
            if sentiment:
                st.info(f"Text sentiment: {sentiment} (polarity {polarity:.2f})")
            if sentiment == "negative" and polarity < -0.5:
                st.warning(
                    "Your written reflection contains strongly negative language. "
                    "This is not a diagnosis. Consider using the Support & Coping "
                    "page or talking with someone you trust."
                )
        else:
            st.error(
                "Storage consent is disabled. "
                "Enable storage in Data Trust Center if you want to save this assessment."
            )

elif page == "🤖 Risk Prediction":
    require_login()
    page_header("🤖", "WELLNESS SIGNAL", "Risk Analysis", "A transparent self-reflection signal based on submitted information.")
    if "assessment_data" not in st.session_state:
        st.warning("Complete an assessment first.")
    else:
        data = st.session_state["assessment_data"]
        username = data["username"]
        result = multimodal_risk_analysis(
            data["stress_level"], data["sleep_hours"], data["anxiety_level"],
            data["exercise_minutes"], data["mood"], data.get("journal_text"),
        )
        risk = result["risk"]
        factors = result["factors"]
        wellness_score = result["wellness_score"]
        history = get_history_data()
        mine = history[history["username"].astype(str) == str(username)] if not history.empty else history
        trajectory = calculate_risk_trajectory(mine)
        missing = missing_data_intelligence(
            data["sleep_hours"], data["stress_level"], data["anxiety_level"],
            data["exercise_minutes"], data["mood"], data.get("journal_text"),
        )
        st.plotly_chart(gauge_figure(wellness_score, "Wellness Signal"), use_container_width=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Risk band", risk)
        c2.metric("Wellness", f"{wellness_score:.0f}/100")
        c3.metric("Trajectory", trajectory["trajectory"])
        c4.metric("Confidence", f"{missing['confidence']:.0%}")
        if risk == "Low":
            st.success("🎯 Current wellness indicators fall in the Low band.")
        elif risk == "Medium":
            st.warning("⚠️ Current wellness indicators fall in the Medium band.")
        else:
            st.error("🚨 Current wellness indicators fall in the High band. This is not a diagnosis.")
        st.markdown("## 🔍 Contributing Indicators")
        for factor in factors:
            st.info(f"• {factor}")
        st.markdown("## 🧩 Multimodal Evidence")
        modality_cols = st.columns(3)
        modality_cols[0].metric("Structured data", "✓")
        modality_cols[1].metric("Journal text", "✓" if result["text"]["available"] else "Not provided")
        modality_cols[2].metric("Extra data", "✓" if result["extra"]["available"] else "Not provided")
        st.markdown("## 🧭 Risk Trajectory")
        st.write(f"**Direction:** {trajectory['trajectory']}")
        st.write(f"**Change:** {trajectory['change']:+.1f} wellness points")
        st.write(f"**Trajectory confidence:** {trajectory['confidence']:.0%}")
        if not mine.empty:
            fig = trajectory_chart(mine)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        st.markdown("## 💡 Suggestions")
        for recommendation in get_recommendations(
            data["stress_level"], data["sleep_hours"], data["anxiety_level"], data["exercise_minutes"],
        ):
            st.success(recommendation)
        save_prediction(
            username, risk, wellness_score, factors,
            trajectory=trajectory["trajectory"], trajectory_change=trajectory["change"],
            confidence_score=missing["confidence"], modality_count=result["modality_count"],
            missing_fields=missing["missing"],
        )
        if (risk == "High" or trajectory["trajectory"] == "Worsening"
                or result["text"]["safety_signal"] == "urgent_language"
                or missing["confidence"] < 0.6):
            st.warning("This result meets the prototype's human-review criteria.")
            if st.button("👩‍⚕️ Request Human Review", use_container_width=True):
                predictions = get_prediction_data()
                if not predictions.empty:
                    latest = predictions[predictions["username"].astype(str) == str(username)].sort_values("date")
                    if not latest.empty:
                        latest_prediction = latest.iloc[-1]
                        create_review_item(int(latest_prediction["id"]), username,
                                           "Automatic review trigger: " + risk)
                        st.success("Added to the human-review queue.")

elif page == "🧭 Risk Trajectory":
    require_login()
    page_header("🧭", "LONGITUDINAL ANALYSIS", "Risk Trajectory", "Look at changes across multiple check-ins rather than a single score.")
    username = st.session_state.current_user
    history = get_history_data()
    if history.empty:
        st.info("Complete several assessments to build a trajectory.")
    else:
        mine = history[history["username"].astype(str) == str(username)].sort_values("date")
        if mine.empty:
            st.info("No")
    else:

            result = calculate_risk_trajectory(
                mine
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Trajectory",
                result[
                    "trajectory"
                ],
            )

            c2.metric(
                "Change",
                f"{result['change']:+.1f}",
            )

            c3.metric(
                "Evidence points",
                result[
                    "points"
                ],
            )

            fig = trajectory_chart(
                mine
            )

            if fig:
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

            st.markdown(
                "### Interpretation"
            )

            if result[
                "trajectory"
            ] == "Worsening":
                st.warning(
                    "Recent wellness indicators have moved downward. "
                    "This does not predict a diagnosis, but it may be useful "
                    "to discuss the change with someone you trust."
                )

            elif result[
                "trajectory"
            ] in [
                "Improving",
                "Slightly improving",
            ]:
                st.success(
                    "Recent wellness indicators are moving upward."
                )

            else:
                st.info(
                    "The current history does not show a strong directional change."
                )



elif page == "🎯 Goals":

    require_login()

    page_header(
        "🎯",
        "PERSONAL TARGETS",
        "Wellness Goals",
        "Track personal targets without turning them into clinical prescriptions.",
    )

    username = (
        st.session_state.current_user
    )

    existing = get_goals(
        username
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        target_sleep = st.slider(
            "Target sleep",
            4,
            10,
            int(
                existing[
                    "target_sleep"
                ]
            )
            if existing
            else 8,
        )

    with col2:
        target_exercise = st.slider(
            "Target exercise",
            0,
            120,
            int(
                existing[
                    "target_exercise"
                ]
            )
            if existing
            else 30,
        )

    with col3:
        target_stress_max = st.slider(
            "Maximum comfortable stress",
            0,
            10,
            int(
                existing[
                    "target_stress_max"
                ]
            )
            if existing
            else 5,
        )

    if st.button(
        "💾 Save Goals",
        use_container_width=True,
    ):

        save_goals(
            username,
            target_sleep,
            target_exercise,
            target_stress_max,
        )

        st.success(
            "Goals saved."
        )

    history = get_history_data()

    if not history.empty:

        mine = history[
            history[
                "username"
            ].astype(str)
            == str(username)
        ].sort_values(
            "date"
        )

        if not mine.empty:

            last = mine.iloc[
                -1
            ]

            g = get_goals(
                username
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Sleep",
                f"{last['sleep_hours']:.1f}h",
                f"{last['sleep_hours'] - g['target_sleep']:+.1f}h",
            )

            c2.metric(
                "Exercise",
                f"{last['exercise_minutes']:.0f} min",
                f"{last['exercise_minutes'] - g['target_exercise']:+.0f}",
            )

            c3.metric(
                "Stress",
                f"{last['stress_level']:.0f}",
                f"{last['stress_level'] - g['target_stress_max']:+.0f}",
                delta_color="inverse",
            )



elif page == "📂 Bulk Upload":

    require_login()

    page_header(
        "📂",
        "BATCH PROCESSING",
        "Bulk Upload & Analysis",
        "Analyze multiple wellness records with transparent confidence and missing-data metrics.",
    )

    required_columns = [
        "username",
        "mood",
        "sleep_hours",
        "stress_level",
        "anxiety_level",
        "exercise_minutes",
    ]

    template = pd.DataFrame(
        [
            {
                "username": "User A",
                "mood": "Good",
                "sleep_hours": 7,
                "stress_level": 3,
                "anxiety_level": 2,
                "exercise_minutes": 30,
                "demographic_group": "Group A",
            }
        ]
    )

    st.download_button(
        "📥 Download Template",
        data=export_to_excel(
            template,
            "Template",
        ),
        file_name="mindtrack_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    uploaded = st.file_uploader(
        "Upload Excel",
        type=["xlsx"],
    )

    if uploaded:

        try:
            bulk = pd.read_excel(
                uploaded
            )

            missing_cols = [
                c
                for c in required_columns
                if c not in bulk.columns
            ]

            if missing_cols:

                st.error(
                    "Missing columns: "
                    + ", ".join(
                        missing_cols
                    )
                )

            else:

                scores = []
                risks = []
                confidences = []

                for _, row in bulk.iterrows():

                    risk, _, score = predict_risk(
                        row[
                            "stress_level"
                        ],
                        row[
                            "sleep_hours"
                        ],
                        row[
                            "anxiety_level"
                        ],
                        row[
                            "exercise_minutes"
                        ],
                        row["mood"],
                    )

                    missing = missing_data_intelligence(
                        row[
                            "sleep_hours"
                        ],
                        row[
                            "stress_level"
                        ],
                        row[
                            "anxiety_level"
                        ],
                        row[
                            "exercise_minutes"
                        ],
                        row["mood"],
                    )

                    scores.append(
                        score
                    )

                    risks.append(
                        risk
                    )

                    confidences.append(
                        missing[
                            "confidence"
                        ]
                    )

                bulk[
                    "wellness_score"
                ] = scores

                bulk[
                    "risk_level"
                ] = risks

                bulk[
                    "data_confidence"
                ] = confidences

                st.success(
                    f"Analyzed {len(bulk)} records."
                )

                st.dataframe(
                    bulk,
                    use_container_width=True,
                )

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Records",
                    len(bulk),
                )

                c2.metric(
                    "Average wellness",
                    f"{bulk['wellness_score'].mean():.0f}",
                )

                c3.metric(
                    "High-risk band",
                    int(
                        (
                            bulk[
                                "risk_level"
                            ]
                            == "High"
                        ).sum()
                    ),
                )

                st.download_button(
                    "📥 Download Results",
                    data=export_to_excel(
                        bulk,
                        "Analysis",
                    ),
                    file_name="mindtrack_bulk_analysis.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

        except Exception as exc:
            st.error(
                f"Could not process file: {exc}"
            )



elif page == "🧩 Multimodal Analysis":

    require_login()

    page_header(
        "🧩",
        "RESEARCH GAP #2",
        "Multimodal Risk Analysis",
        "Combine structured check-ins, journal language, and optional contextual data.",
    )

    username = (
        st.session_state.current_user
    )

    history = get_history_data()

    mine = (
        history[
            history[
                "username"
            ].astype(str)
            == str(username)
        ]
        if not history.empty
        else history
    )

    if mine.empty:

        st.info(
            "Complete an assessment first."
        )

    else:

        latest = mine.sort_values(
            "date"
        ).iloc[-1]

        st.markdown(
            "### Current modalities"
        )

        st.write(
            "Structured check-in: "
            "sleep, stress, anxiety, exercise, mood"
        )

        journal = st.text_area(
            "Optional journal text",
            height=150,
        )

        uploaded = st.file_uploader(
            "Optional contextual CSV/JSON",
            type=[
                "csv",
                "json",
            ],
            help=(
                "Example columns: steps, heart_rate, "
                "screen_time, sleep_quality, activity_level."
            ),
        )

        if st.button(
            "🧩 Run Multimodal Analysis",
            use_container_width=True,
        ):

            result = multimodal_risk_analysis(
                latest[
                    "stress_level"
                ],
                latest[
                    "sleep_hours"
                ],
                latest[
                    "anxiety_level"
                ],
                latest[
                    "exercise_minutes"
                ],
                latest[
                    "mood"
                ],
                journal,
                uploaded,
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Risk band",
                result["risk"],
            )

            c2.metric(
                "Wellness",
                f"{result['wellness_score']:.0f}/100",
            )

            c3.metric(
                "Modalities",
                result[
                    "modality_count"
                ],
            )

            st.markdown(
                "### Modality evidence"
            )

            st.json(
                {
                    "structured": result[
                        "structured"
                    ],
                    "text": result[
                        "text"
                    ],
                    "additional_context": result[
                        "extra"
                    ],
                }
            )

            st.markdown(
                "### Key factors"
            )

            for factor in result[
                "factors"
            ]:
                st.info(
                    factor
                )

            st.caption(
                "The additional modality changes contextual understanding; "
                "it does not turn this prototype into a clinical diagnostic model."
            )



elif page == "📈 Dashboard":

    require_login()

    page_header(
        "📈",
        "ANALYTICS",
        "Wellness Dashboard",
        "Trends, distributions, correlations, and longitudinal signals.",
    )

    history = get_history_data()

    if history.empty:

        st.info(
            "Complete an assessment to populate the dashboard."
        )

    else:

        username = (
            st.session_state.current_user
        )

        filtered = history[
            history[
                "username"
            ].astype(str)
            == str(username)
        ].sort_values(
            "date"
        )

        if filtered.empty:

            st.info(
                "No data available for your account."
            )

        else:

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Entries",
                len(filtered),
            )

            c2.metric(
                "Avg wellness",
                f"{filtered['wellness_score'].mean():.0f}",
            )

            c3.metric(
                "Avg sleep",
                f"{filtered['sleep_hours'].mean():.1f}h",
            )

            c4.metric(
                "Avg stress",
                f"{filtered['stress_level'].mean():.1f}",
            )

            tab1, tab2, tab3 = st.tabs(
                [
                    "📈 Trends",
                    "🧩 Distributions",
                    "🔎 Insights",
                ]
            )

            with tab1:

                fig = px.line(
                    filtered,
                    x="date",
                    y="wellness_score",
                    markers=True,
                    title="Wellness Over Time",
                    color_discrete_sequence=[
                        COLOR_PRIMARY
                    ],
                )

                st.plotly_chart(
                    style_plot(fig),
                    use_container_width=True,
                )

                fig2 = px.line(
                    filtered,
                    x="date",
                    y=[
                        "stress_level",
                        "anxiety_level",
                    ],
                    markers=True,
                    title="Stress and Anxiety",
                )

                st.plotly_chart(
                    style_plot(fig2),
                    use_container_width=True,
                )

            with tab2:

                fig = px.histogram(
                    filtered,
                    x="wellness_score",
                    nbins=12,
                    title="Wellness Distribution",
                    color_discrete_sequence=[
                        COLOR_PRIMARY
                    ],
                )

                st.plotly_chart(
                    style_plot(fig),
                    use_container_width=True,
                )

                fig2 = px.scatter(
                    filtered,
                    x="sleep_hours",
                    y="stress_level",
                    size="exercise_minutes",
                    color="wellness_score",
                    title="Sleep vs Stress",
                    color_continuous_scale=[
                        [0, COLOR_HIGH],
                        [0.5, COLOR_MEDIUM],
                        [1, COLOR_GOOD],
                    ],
                )

                st.plotly_chart(
                    style_plot(fig2),
                    use_container_width=True,
                )

            with tab3:

                trajectory = calculate_risk_trajectory(
                    filtered
                )

                st.markdown(
                    f"""
                    <div class="mind-card">
                    <h3>🧭 Trajectory</h3>
                    <b>{trajectory['trajectory']}</b><br>
                    Change: {trajectory['change']:+.1f}<br>
                    Evidence points: {trajectory['points']}<br>
                    Confidence: {trajectory['confidence']:.0%}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                corr = filtered[
                    [
                        "sleep_hours",
                        "stress_level",
                        "anxiety_level",
                        "exercise_minutes",
                        "mood_num",
                        "wellness_score",
                    ]
                ].corr()

                heatmap = go.Figure(
                    data=go.Heatmap(
                        z=corr.values,
                        x=corr.columns,
                        y=corr.index,
                        colorscale=[
                            [0, COLOR_HIGH],
                            [0.5, "#FFFFFF"],
                            [1, COLOR_PRIMARY],
                        ],
                        zmin=-1,
                        zmax=1,
                        text=np.round(
                            corr.values,
                            2,
                        ),
                        texttemplate="%{text}",
                    )
                )

                heatmap.update_layout(
                    title="Correlation Heatmap"
                )

                st.plotly_chart(
                    style_plot(
                        heatmap
                    ),
                    use_container_width=True,
                )

                calendar = create_mood_calendar(
                    filtered
                )

                if calendar:
                    st.plotly_chart(
                        calendar,
                        use_container_width=True,
                    )



elif page == "📝 Journal":

    require_login()

    page_header(
        "📝",
        "REFLECTION",
        "Journal & Sentiment Analysis",
        "Write freely and receive a simple language-based reflection signal.",
    )

    username = (
        st.session_state.current_user
    )

    journal_text = st.text_area(
        "Your journal entry",
        height=260,
        placeholder=(
            "How was your day? "
            "What felt difficult or positive?"
        ),
    )

    if st.button(
        "🔍 Analyze & Save",
        use_container_width=True,
    ):

        if not journal_text.strip():

            st.warning(
                "Please write something first."
            )

        else:

            sentiment, polarity = analyze_sentiment(
                journal_text
            )

            entry = save_journal_entry(
                username,
                journal_text.strip(),
                sentiment,
                polarity,
            )

            if entry:

                c1, c2 = st.columns(2)

                with c1:

                    if sentiment == "positive":
                        st.success(
                            "Positive sentiment 😊"
                        )

                    elif sentiment == "negative":
                        st.warning(
                            "Negative sentiment 😔"
                        )

                    else:
                        st.info(
                            "Neutral sentiment 😐"
                        )

                with c2:

                    fig = gauge_figure(
                        polarity,
                        "Text Polarity",
                        value_range=(-1, 1),
                        steps=[
                            {
                                "range": [
                                    -1,
                                    -0.1,
                                ],
                                "color": COLOR_HIGH,
                            },
                            {
                                "range": [
                                    -0.1,
                                    0.1,
                                ],
                                "color": COLOR_MEDIUM,
                            },
                            {
                                "range": [
                                    0.1,
                                    1,
                                ],
                                "color": COLOR_GOOD,
                            },
                        ],
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                    )

                safety = chatbot_safety_gate(
                    journal_text
                )

                if safety == "urgent":

                    st.error(
                        "Safety-related language was detected. "
                        "This app cannot assess an emergency. "
                        "Please seek immediate support from a trusted person, "
                        "local emergency services, or an appropriate crisis service."
                    )

                elif (
                    sentiment == "negative"
                    and polarity < -0.4
                ):

                    st.info(
                        "The language in this entry appears strongly negative. "
                        "That is not a diagnosis. Consider talking with someone "
                        "you trust if the feeling persists."
                    )

            else:

                st.error(
                    "Journal storage is disabled in your privacy settings."
                )



elif page == "📓 My Journals":

    require_login()

    page_header(
        "📓",
        "YOUR WORDS",
        "My Journal History",
        "Review and manage your saved reflections.",
    )

    username = (
        st.session_state.current_user
    )

    df = get_journal_entries(
        username
    )

    if df.empty:

        st.info(
            "No journal entries yet."
        )

    else:

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Entries",
            len(df),
        )

        c2.metric(
            "Positive",
            int(
                (
                    df["sentiment"]
                    == "positive"
                ).sum()
            ),
        )

        c3.metric(
            "Neutral",
            int(
                (
                    df["sentiment"]
                    == "neutral"
                ).sum()
            ),
        )

        c4.metric(
            "Negative",
            int(
                (
                    df["sentiment"]
                    == "negative"
                ).sum()
            ),
        )

        if len(df) >= 2:

            chart_df = df.sort_values(
                "date"
            )

            fig = px.line(
                chart_df,
                x="date",
                y="polarity",
                markers=True,
                title="Journal Sentiment Over Time",
                color_discrete_sequence=[
                    COLOR_PRIMARY
                ],
            )

            fig.add_hline(
                y=0,
                line_dash="dot",
                line_color=COLOR_MUTED,
            )

            st.plotly_chart(
                style_plot(fig),
                use_container_width=True,
            )

        for _, row in df.iterrows():

            with st.expander(
                f"{row['date'].strftime('%Y-%m-%d %H:%M')} · "
                f"{row['sentiment'].title()}"
            ):

                st.write(
                    row["text"]
                )

                st.caption(
                    f"Polarity: {row['polarity']:.3f}"
                )

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_journal_{row['id']}",
                ):
                    delete_journal_entry(
                        row["id"]
                    )
                    st.rerun()

        st.download_button(
            "📥 Download My Journals",
            data=export_journal_to_excel(
                username
            ),
            file_name="my_journals.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )



elif page == "🗂️ My Entries":

    require_login()

    page_header(
        "🗂️",
        "YOUR DATA",
        "My Entries",
        "Review and delete your own check-in history.",
    )

    username = (
        st.session_state.current_user
    )

    history = get_history_data()

    if history.empty:

        st.info(
            "No assessments yet."
        )

    else:

        mine = history[
            history[
                "username"
            ].astype(str)
            == str(username)
        ].sort_values(
            "date",
            ascending=False,
        )

        for _, row in mine.iterrows():

            c1, c2, c3, c4, c5 = st.columns(
                [
                    2,
                    1.2,
                    1,
                    1.2,
                    0.8,
                ]
            )

            c1.write(
                row[
                    "date"
                ].strftime(
                    "%Y-%m-%d %H:%M"
                )
            )

            c2.write(
                row["mood"]
            )

            c3.write(
                f"{row['sleep_hours']:.1f}h"
            )

            c4.write(
                f"{row['wellness_score']:.0f}/100"
            )

            if c5.button(
                "🗑️",
                key=f"delete_entry_{row['id']}",
            ):

                delete_entry(
                    row["id"]
                )

                st.rerun()

        st.download_button(
            "📥 Download My Data",
            data=export_to_excel(
                mine,
                "My History",
            ),
            file_name="my_history.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )



elif page == "🆘 Support & Coping":

    require_login()

    page_header(
        "🆘",
        "TAKE A MOMENT",
        "Support & Coping Toolkit",
        "Simple techniques for the next few minutes.",
    )

    st.markdown(
        "### 🫁 Box Breathing"
    )

    st.info(
        "Breathe in for 4 seconds → hold 4 → breathe out 4 → hold 4. "
        "Repeat several times."
    )

    pulse_divider()

    st.markdown(
        "### 🌱 5–4–3–2–1 Grounding"
    )

    st.write(
        "Name 5 things you can see, "
        "4 things you can touch, "
        "3 things you can hear, "
        "2 things you can smell, "
        "and 1 thing you can taste."
    )

    pulse_divider()

    st.markdown(
        "### 🤝 Reach Out"
    )

    st.info(
        "If things feel overwhelming, consider contacting someone you trust "
        "and telling them clearly that you could use some support."
    )

    st.warning(
        "If you believe you are in immediate danger or may hurt yourself, "
        "contact your local emergency service or an appropriate crisis service "
        "in your country now."
    )



elif page == "💬 Safe Chatbot":

    require_login()

    page_header(
        "💬",
        "RESEARCH GAP #13",
        "Safe Wellness Chatbot",
        "A safety-gated conversational reflection tool.",
    )

    st.markdown(
        """
        <div class="trust-card">
        <b>Safety boundary</b><br>
        This assistant does not diagnose mental illness, prescribe medication,
        predict suicide, or replace a clinician. It focuses on reflection,
        grounding, coping, and encouraging appropriate human support.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for role, message in st.session_state.chat_history:

        if role == "user":

            st.markdown(
                f"""
                <div class="chat-user">
                <b>You</b><br>
                {safe_text(message)}
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                f"""
                <div class="chat-bot">
                <b>MindTrack</b><br>
                {safe_text(message)}
                </div>
                """,
                unsafe_allow_html=True,
            )

    message = st.chat_input(
        "Tell me what's on your mind..."
    )

    if message:

        st.session_state.chat_history.append(
            (
                "user",
                message,
            )
        )

        response = safe_chatbot_response(
            st.session_state.current_user,
            message,
        )

        st.session_state.chat_history.append(
            (
                "assistant",
                response,
            )
        )

        audit_event(
            st.session_state.current_user,
            "chatbot_interaction",
            "Safe chatbot used.",
        )

        st.rerun()

    if st.button(
        "🧹 Clear conversation"
    ):

        st.session_state.chat_history = []

        audit_event(
            st.session_state.current_user,
            "chatbot_history_cleared",
        )

        st.rerun()



elif page == "👩‍⚕️ Human Review":

    require_login()

    page_header(
        "👩‍⚕️",
        "RESEARCH GAP #9",
        "Human-in-the-Loop Review",
        "Machine-generated signals can be reviewed instead of being treated as final decisions.",
    )

    st.warning(
        "Prototype workflow only. In a real clinical deployment, reviewers "
        "must be appropriately qualified and the organization must establish "
        "governance, escalation, consent, and documentation procedures."
    )

    queue = get_review_queue()

    if queue.empty:

        st.success(
            "No pending review items."
        )

    else:

        pending = queue[
            queue["status"]
            == "Pending"
        ]

        st.metric(
            "Pending reviews",
            len(pending),
        )

        for _, row in pending.iterrows():

            with st.expander(
                f"Review #{row['id']} · "
                f"{row['reason']}"
            ):

                st.write(
                    f"User: {row['username']}"
                )

                st.write(
                    f"Created: {row['created_at']}"
                )

                reviewer = st.text_input(
                    "Reviewer name",
                    key=f"reviewer_{row['id']}",
                )

                note = st.text_area(
                    "Reviewer note",
                    key=f"review_note_{row['id']}",
                )

                c1, c2 = st.columns(2)

                with c1:

                    if st.button(
                        "✅ Reviewed",
                        key=f"approve_{row['id']}",
                        use_container_width=True,
                    ):

                        update_review(
                            row["id"],
                            "Reviewed",
                            reviewer or "Reviewer",
                            note,
                        )

                        st.success(
                            "Review recorded."
                        )

                        st.rerun()

                with c2:

                    if st.button(
                        "🚩 Escalate",
                        key=f"escalate_{row['id']}",
                        use_container_width=True,
                    ):

                        update_review(
                            row["id"],
                            "Escalated",
                            reviewer or "Reviewer",
                            note,
                        )

                        st.warning(
                            "Review marked for escalation."
                        )

                        st.rerun()



elif page == "⚖️ Fairness Audit":

    require_login()

    page_header(
        "⚖️",
        "RESEARCH GAP #10",
        "Fairness Audit",
        "Compare model outputs across consented demographic subgroups.",
    )

    st.warning(
        "This is an audit dashboard, not proof of fairness. "
        "Fairness evaluation requires sufficient sample sizes, appropriate "
        "subgroup definitions, statistical uncertainty, and domain expertise."
    )

    history = get_history_data()

    if history.empty:

        st.info(
            "No data available."
        )

    else:

        audit_df = prepare_fairness_data(
            history
        )

        if (
            "demographic_group"
            not in audit_df.columns
        ):

            st.info(
                "No demographic subgroup field exists yet."
            )

        else:

            summary = fairness_audit(
                audit_df
            )

            if summary.empty:

                st.info(
                    "No consented subgroup data available."
                )

            else:

                st.dataframe(
                    summary,
                    use_container_width=True,
                )

                fig = px.bar(
                    summary,
                    x="demographic_group",
                    y="high_risk_rate",
                    title="High-Risk-Band Rate by Group",
                    color_discrete_sequence=[
                        COLOR_HIGH
                    ],
                )

                st.plotly_chart(
                    style_plot(fig),
                    use_container_width=True,
                )

                fig2 = px.bar(
                    summary,
                    x="demographic_group",
                    y="average_wellness",
                    title="Average Wellness by Group",
                    color_discrete_sequence=[
                        COLOR_PRIMARY
                    ],
                )

                st.plotly_chart(
                    style_plot(fig2),
                    use_container_width=True,
                )

                st.markdown(
                    "### What to investigate"
                )

                st.write(
                    """
                    • Large differences in high-risk-band rates
                    • Differences in missing-data rates
                    • Differences in confidence
                    • Differences caused by data collection rather than the model
                    • Small subgroup sizes that make comparisons unstable
                    """
                )



elif page == "🔐 Data Trust Center":

    require_login()

    page_header(
        "🔐",
        "RESEARCH GAP #12",
        "Data Trust Center",
        "See what MindTrack stores, why it stores it, and control your data.",
    )

    username = (
        st.session_state.current_user
    )

    privacy = get_privacy_preferences(
        username
    )

    st.markdown(
        "## 📦 Data Inventory"
    )

    inventory = pd.DataFrame(
        [
            {
                "Data": "Wellness assessments",
                "Purpose": "Personal trend analysis",
                "Stored": bool(
                    privacy[
                        "consent_storage"
                    ]
                ),
            },
            {
                "Data": "Journal entries",
                "Purpose": "Personal reflection and sentiment analysis",
                "Stored": bool(
                    privacy[
                        "consent_storage"
                    ]
                ),
            },
            {
                "Data": "Predictions",
                "Purpose": "Display wellness signals",
                "Stored": bool(
                    privacy[
                        "consent_storage"
                    ]
                ),
            },
            {
                "Data": "Research analytics",
                "Purpose": "Aggregate/fairness analysis",
                "Stored": bool(
                    privacy[
                        "consent_research"
                    ]
                ),
            },
        ]
    )

    st.dataframe(
        inventory,
        use_container_width=True,
    )

    st.markdown(
        "## 🔑 Privacy Controls"
    )

    consent_storage = st.checkbox(
        "Allow MindTrack to store my entries",
        value=bool(
            privacy[
                "consent_storage"
            ]
        ),
    )

    consent_analytics = st.checkbox(
        "Allow analytics on my stored data",
        value=bool(
            privacy[
                "consent_analytics"
            ]
        ),
    )

    consent_research = st.checkbox(
        "Allow my data to be considered for research/fairness analysis",
        value=bool(
            privacy[
                "consent_research"
            ]
        ),
    )

    pseudonymous_mode = st.checkbox(
        "Use pseudonymous identifiers for analytics",
        value=bool(
            privacy[
                "pseudonymous_mode"
            ]
        ),
    )

    if st.button(
        "💾 Save Privacy Settings",
        use_container_width=True,
    ):

        save_privacy_preferences(
            username,
            consent_storage,
            consent_analytics,
            consent_research,
            pseudonymous_mode,
        )

        st.success(
            "Privacy preferences updated."
        )

    pulse_divider()

    st.markdown(
        "## 📥 Download My Data"
    )

    st.download_button(
        "Download complete personal data",
        data=create_user_export(
            username
        ),
        file_name="mindtrack_personal_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    pulse_divider()

    st.markdown(
        "## 🗑️ Delete My Data"
    )

    st.warning(
        "This permanently deletes your stored assessments, journals, "
        "predictions, goals, review records, and privacy preferences."
    )

    confirm_delete = st.checkbox(
        "I understand this action cannot be undone."
    )

    if confirm_delete:

        if st.button(
            "🗑️ Permanently Delete My Data",
            type="primary",
            use_container_width=True,
        ):

            delete_all_user_data(
                username
            )

            st.success(
                "Your stored data has been deleted."
            )



elif page == "🌐 Privacy / Federated":

    require_login()

    page_header(
        "🌐",
        "RESEARCH GAP #11",
        "Privacy & Federated-Learning Foundation",
        "Explore how the application can learn from local aggregates without centralizing raw personal records.",
    )

    username = (
        st.session_state.current_user
    )

    st.markdown(
        """
        <div class="trust-card">
        <b>Local-data principle</b><br>
        A federated-learning design keeps raw user records on the local
        client and sends only approved model updates to an aggregation
        service.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "### 🧬 Current Prototype Architecture"
    )

    st.code(
        """
USER DATA
   │
   ├── assessment
   ├── journal
   └── contextual signals
          │
          ▼
LOCAL FEATURE PROCESSING
          │
          ▼
LOCAL AGGREGATE
          │
          ├── sample count
          ├── mean wellness
          ├── mean sleep
          ├── mean stress
          └── mean anxiety
          │
          ▼
SECURE AGGREGATION SERVER
          │
          ▼
GLOBAL MODEL UPDATE

Raw journal/check-in records
should NOT be transmitted.
        """,
        language="text",
    )

    st.markdown(
        "### 🔐 Generate Local Model Update"
    )

    if st.button(
        "Generate Local Aggregate",
        use_container_width=True,
    ):

        update = create_local_model_update(
            username
        )

        if update:

            st.success(
                "Local aggregate generated. "
                "Nothing was transmitted by this prototype."
            )

            st.json(
                update
            )

        else:

            st.info(
                "Complete assessments first."
            )

    st.markdown(
        "### Production safeguards"
    )

    safeguards = [
        "Secure aggregation",
        "Differential privacy",
        "Encrypted transport",
        "Client authentication",
        "Model versioning",
        "Privacy-budget accounting",
        "Audit logs",
        "Data minimization",
    ]

    for item in safeguards:
        st.info(
            f"🔐 {item}"
        )

    st.caption(
        "The current implementation is a research foundation, not a complete "
        "federated-learning system."
    )



elif page == "📄 Report":

    require_login()

    page_header(
        "📄",
        "DOCUMENTATION",
        "Wellness Report",
        "Generate a shareable summary of the latest assessment.",
    )

    if "assessment_data" not in st.session_state:

        st.warning(
            "Complete an assessment first."
        )

    else:

        data = st.session_state[
            "assessment_data"
        ]

        username = data[
            "username"
        ]

        risk, factors, score = predict_risk(
            data["stress_level"],
            data["sleep_hours"],
            data["anxiety_level"],
            data["exercise_minutes"],
            data["mood"],
        )

        history = get_history_data()

        mine = history[
            history[
                "username"
            ].astype(str)
            == str(username)
        ] if not history.empty else history

        trajectory = calculate_risk_trajectory(
            mine
        )

        missing = missing_data_intelligence(
            data["sleep_hours"],
            data["stress_level"],
            data["anxiety_level"],
            data["exercise_minutes"],
            data["mood"],
            data.get("journal_text"),
        )

        st.markdown(
            "### Report Preview"
        )

        st.write(
            f"User: {username}"
        )

        st.write(
            f"Wellness signal: {score:.0f}/100"
        )

        st.write(
            f"Risk band: {risk}"
        )

        st.write(
            f"Trajectory: {trajectory['trajectory']}"
        )

        st.write(
            f"Confidence: {missing['confidence']:.0%}"
        )

        st.markdown(
            "### Key Factors"
        )

        for factor in factors:
            st.info(
                factor
            )

        recommendations = get_recommendations(
            data["stress_level"],
            data["sleep_hours"],
            data["anxiety_level"],
            data["exercise_minutes"],
        )

        pdf = generate_pdf_report(
            username,
            risk,
            score,
            factors,
            recommendations,
            trajectory[
                "trajectory"
            ],
            missing[
                "confidence"
            ],
        )

        st.download_button(
            "📥 Download PDF",
            data=pdf,
            file_name="mindtrack_wellness_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )



elif page == "📊 Admin":

    require_login()

    page_header(
        "📊",
        "BACK OFFICE",
        "Admin Dashboard",
        "Prototype governance, review, and data management.",
    )

    init_db()

    history = get_history_data()
    predictions = get_prediction_data()
    reviews = get_review_queue()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Assessment records",
        len(history),
    )

    c2.metric(
        "Predictions",
        len(predictions),
    )

    c3.metric(
        "Pending reviews",
        int(
            (
                reviews["status"]
                == "Pending"
            ).sum()
        )
        if not reviews.empty
        else 0,
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📋 History",
            "🤖 Predictions",
            "👩‍⚕️ Reviews",
            "🔐 Audit Log",
        ]
    )

    with tab1:

        st.dataframe(
            history,
            use_container_width=True,
        )

        if not history.empty:

            st.download_button(
                "📥 Download History",
                data=export_to_excel(
                    history,
                    "History",
                ),
                file_name="mindtrack_history.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    with tab2:

        st.dataframe(
            predictions,
            use_container_width=True,
        )

        if not predictions.empty:

            st.download_button(
                "📥 Download Predictions",
                data=export_to_excel(
                    predictions,
                    "Predictions",
                ),
                file_name="mindtrack_predictions.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    with tab3:

        st.dataframe(
            reviews,
            use_container_width=True,
        )

    with tab4:

        if os.path.exists(
            AUDIT_CSV
        ):

            audit_df = pd.read_csv(
                AUDIT_CSV
            )

            st.dataframe(
                audit_df,
                use_container_width=True,
            )

            st.download_button(
                "📥 Download Audit Log",
                data=export_to_excel(
                    audit_df,
                    "Audit",
                ),
                file_name="mindtrack_audit.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        else:

            st.info(
                "No audit events yet."
            )



st.sidebar.markdown("---")

st.sidebar.caption(
    "MindTrack is a wellness/self-reflection prototype. "
    "It does not provide medical diagnosis or emergency care."
)
