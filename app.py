import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
from collections import defaultdict
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

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
COLOR_RESEARCH = "#6B5B95"
COLOR_MOMENTUM_UP = "#2E8B57"
COLOR_MOMENTUM_DOWN = "#C1554A"

CHART_PALETTE = [COLOR_PRIMARY, COLOR_MEDIUM, COLOR_HIGH, COLOR_SLATE, COLOR_PRIMARY_LIGHT, "#8B5E3C"]
RISK_COLOR_MAP = {"Low": COLOR_GOOD, "Medium": COLOR_MEDIUM, "High": COLOR_HIGH}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
:root {{ --ink: {COLOR_INK}; --muted: {COLOR_MUTED}; --paper: {COLOR_BG}; --card: {COLOR_CARD};
    --border: {COLOR_BORDER}; --primary: {COLOR_PRIMARY}; --primary-light: {COLOR_PRIMARY_LIGHT};
    --good: {COLOR_GOOD}; --medium: {COLOR_MEDIUM}; --high: {COLOR_HIGH}; --research: {COLOR_RESEARCH}; }}
html, body, [class*="css"] {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}
.stApp {{ background: var(--paper); }}
.main .block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1200px; }}
h1, h2, h3 {{ font-family: 'Fraunces', Georgia, serif !important; color: var(--ink) !important;
    font-weight: 600 !important; letter-spacing: -0.01em; }}
.stMarkdown, .stMarkdown p, label, .stText, .stCaption {{ color: var(--muted) !important; }}
[data-testid="stSidebar"] {{ background: var(--ink); border-right: 1px solid rgba(255,255,255,0.06); }}
[data-testid="stSidebar"] * {{ color: #EDEFEE !important; }}
.sidebar-brand {{ font-family: 'Fraunces', serif; font-size: 1.55rem; font-weight: 700; color: #fff !important;
    margin: 0.2rem 0 0.1rem 0; display: flex; align-items: center; gap: 8px; }}
.sidebar-tagline {{ font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--primary-light) !important; margin-bottom: 1.5rem; }}
[data-testid="stSidebar"] div[role="radiogroup"] label {{
    background: rgba(255,255,255,0.035); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px; padding: 9px 14px; margin-bottom: 6px; transition: all 0.15s ease; }}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
    background: rgba(255,255,255,0.09); border-color: var(--primary-light); }}
.sidebar-disclaimer {{
    font-size: 0.68rem !important; color: rgba(237,239,238,0.55) !important;
    margin-top: 16px; line-height: 1.45; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.08); }}
.page-header {{ display: flex; align-items: flex-start; gap: 16px; margin-bottom: 0.2rem; }}
.page-header-icon {{ font-size: 2.2rem; line-height: 1; margin-top: 2px; }}
.page-eyebrow {{ font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--primary); font-weight: 600; margin-bottom: 2px; }}
.page-title {{ margin: 0 !important; font-size: 2.05rem !important; }}
.page-subtitle {{ color: var(--muted) !important; font-size: 1rem; margin-top: 4px !important; }}
.pulse-divider {{ color: var(--primary); opacity: 0.55; height: 18px; margin: 1.2rem 0 1.6rem 0; }}
.pulse-divider svg {{ width: 100%; height: 100%; display: block; }}
.hero-wrap {{ text-align: center; padding: 2.6rem 0 1.6rem 0; }}
.hero-icon {{ font-size: 3.2rem; }}
.hero-title {{ font-family: 'Fraunces', serif; font-size: 2.6rem; margin: 0.25rem 0 0.35rem 0; color: var(--ink); font-weight: 700; }}
.hero-tagline {{ font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.10em; text-transform: uppercase;
    font-size: 0.82rem; color: var(--primary); font-weight: 600; }}
[data-testid="stMetric"] {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px;
    padding: 16px 18px; box-shadow: 0 1px 3px rgba(27,36,48,0.05); }}
[data-testid="stMetricLabel"] {{ font-family: 'IBM Plex Mono', monospace !important; text-transform: uppercase;
    font-size: 0.70rem !important; letter-spacing: 0.06em; color: var(--muted) !important; }}
[data-testid="stMetricValue"] {{ font-family: 'Fraunces', serif !important; color: var(--ink) !important; }}
.feature-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px;
    padding: 22px; box-shadow: 0 1px 3px rgba(27,36,48,0.05); }}
.research-card {{
    background: linear-gradient(135deg, rgba(107,91,149,0.05) 0%, rgba(255,255,255,1) 100%);
    border: 1px solid rgba(107,91,149,0.15); border-radius: 14px;
    padding: 24px; box-shadow: 0 2px 8px rgba(107,91,149,0.08); margin-bottom: 16px; }}
.research-card h4 {{ color: {COLOR_RESEARCH} !important; font-family: 'Fraunces', serif !important;
    font-size: 1.15rem !important; margin-bottom: 8px !important; }}
.research-badge {{ display: inline-flex; align-items: center; gap: 4px;
    background: rgba(107,91,149,0.12); border: 1px solid rgba(107,91,149,0.25);
    color: {COLOR_RESEARCH}; border-radius: 999px; padding: 3px 10px;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.05em; }}
.momentum-up {{ color: {COLOR_MOMENTUM_UP} !important; font-weight: 700; }}
.momentum-down {{ color: {COLOR_MOMENTUM_DOWN} !important; font-weight: 700; }}
.stButton > button {{ background: var(--primary); color: #fff; border: none; border-radius: 8px;
    padding: 11px 22px; font-weight: 600; font-family: 'Inter', sans-serif;
    box-shadow: 0 1px 2px rgba(27,36,48,0.12); transition: all 0.15s ease; }}
.stButton > button:hover {{ background: var(--primary-light); transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(47,111,98,0.25); }}
.stDownloadButton > button {{ background: #fff; color: var(--primary); border: 1.5px solid var(--primary);
    border-radius: 8px; font-weight: 600; }}
.stDownloadButton > button:hover {{ background: var(--primary); color: #fff; }}
div[data-testid="stAlert"] {{ border-radius: 10px; border: 1px solid var(--border); }}
button[data-baseweb="tab"] {{ font-family: 'Inter', sans-serif; font-weight: 600; color: var(--muted); }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: var(--primary); }}
[data-testid="stSlider"] [role="slider"] {{ background-color: var(--primary) !important; }}
hr {{ display: none; }}
.streak-badge {{ display: inline-flex; align-items: center; gap: 6px; background: rgba(217,164,65,0.12);
    border: 1px solid rgba(217,164,65,0.35); color: var(--medium) !important; border-radius: 999px;
    padding: 4px 14px; font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem; font-weight: 600; }}
.breathing-circle-wrap {{ display: flex; justify-content: center; padding: 1.8rem 0; }}
.breathing-circle {{ width: 140px; height: 140px; border-radius: 50%;
    background: radial-gradient(circle, var(--primary-light), var(--primary));
    animation: breathe 16s ease-in-out infinite; box-shadow: 0 0 40px rgba(47,111,98,0.35); }}
@keyframes breathe {{
    0% {{ transform: scale(0.7); opacity: 0.8; }}
    25% {{ transform: scale(1.15); opacity: 1; }}
    50% {{ transform: scale(1.15); opacity: 1; }}
    75% {{ transform: scale(0.7); opacity: 0.8; }}
    100% {{ transform: scale(0.7); opacity: 0.8; }} }}
.entry-row {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    padding: 10px 16px; margin-bottom: 8px; }}
.login-box {{ max-width: 400px; margin: 2rem auto; padding: 2rem;
    background: #fff; border: 1px solid rgba(27,36,48,0.10); border-radius: 14px; text-align: center; }}
.login-icon {{ font-size: 3rem; margin-bottom: 0.5rem; }}
.login-title {{ font-family: 'Fraunces', serif; font-size: 1.6rem; color: var(--ink); margin-bottom: 0.3rem; }}
.login-sub {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 1.5rem; }}
.user-pill {{ display: inline-flex; align-items: center; gap: 6px;
    background: rgba(47,111,98,0.10); border: 1px solid rgba(47,111,98,0.25);
    color: var(--primary); border-radius: 999px; padding: 5px 14px;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; font-weight: 600; }}
.lock-screen {{ text-align: center; padding: 3rem 1rem; }}
.lock-screen h2 {{ font-family: 'Fraunces', serif; color: var(--ink); }}
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
JOURNAL_CSV = os.path.join(DATA_DIR, "journal_entries.csv")


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
            username TEXT, date TEXT, mood TEXT, sleep_hours REAL,
            stress_level REAL, anxiety_level REAL, exercise_minutes REAL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, date TEXT, risk_level TEXT, wellness_score REAL, factors TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            username TEXT PRIMARY KEY,
            target_sleep REAL, target_exercise REAL, target_stress_max REAL, updated_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mental_fingerprints (
            username TEXT PRIMARY KEY,
            baseline_sleep REAL, baseline_stress REAL, baseline_anxiety REAL,
            baseline_exercise REAL, baseline_mood REAL,
            sleep_weight REAL, stress_weight REAL, anxiety_weight REAL,
            exercise_weight REAL, mood_weight REAL,
            volatility_score REAL, pattern_stability REAL,
            updated_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trigger_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, trigger_name TEXT, trigger_type TEXT,
            confidence REAL, frequency INTEGER, avg_lead_time REAL,
            description TEXT, discovered_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS momentum_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, date TEXT, momentum_score REAL,
            momentum_direction TEXT, velocity REAL, acceleration REAL,
            trend_strength REAL, forecast_next_7 REAL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS intervention_receptivity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, intervention_type TEXT, receptivity_score REAL,
            historical_response_rate REAL, optimal_timing TEXT,
            preferred_channel TEXT, personalization_notes TEXT,
            updated_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recovery_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, episode_date TEXT, episode_type TEXT,
            episode_severity REAL, recovery_start_date TEXT,
            recovery_end_date TEXT, recovery_duration_days REAL,
            recovery_rate REAL, baseline_return_pct REAL,
            intervention_used TEXT, intervention_effectiveness REAL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS intervention_experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, experiment_name TEXT, intervention_type TEXT,
            start_date TEXT, end_date TEXT, status TEXT,
            pre_score REAL, post_score REAL, effect_size REAL,
            p_value REAL, is_significant INTEGER, sample_size INTEGER,
            notes TEXT, created_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS intervention_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, intervention_type TEXT, recommended_at TEXT,
            responded_at TEXT, response_type TEXT, engagement_score REAL,
            outcome_score REAL, feedback TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_user_history(username, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes, entry_date=None):
    init_db()
    if entry_date is None:
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        date_str = datetime.combine(entry_date, datetime.now().time()).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    conn.execute(
        """INSERT INTO user_history
           (username, date, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (username, date_str, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes),
    )
    conn.commit()
    conn.close()
    update_mental_fingerprint(username)
    update_momentum_tracking(username)
    discover_triggers(username)


def save_prediction(username, risk_level, wellness_score, factors):
    init_db()
    conn = get_connection()
    conn.execute(
        """INSERT INTO predictions (username, date, risk_level, wellness_score, factors)
           VALUES (?, ?, ?, ?, ?)""",
        (username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), risk_level, wellness_score, str(factors)),
    )
    conn.commit()
    conn.close()


def save_goals(username, target_sleep, target_exercise, target_stress_max):
    init_db()
    conn = get_connection()
    conn.execute(
        """INSERT INTO goals (username, target_sleep, target_exercise, target_stress_max, updated_at)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(username) DO UPDATE SET
             target_sleep=excluded.target_sleep,
             target_exercise=excluded.target_exercise,
             target_stress_max=excluded.target_stress_max,
             updated_at=excluded.updated_at""",
        (username, target_sleep, target_exercise, target_stress_max, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def get_goals(username):
    init_db()
    conn = get_connection()
    row = conn.execute("SELECT * FROM goals WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ============================================================================
# FEATURE 1: PERSONAL MENTAL HEALTH FINGERPRINT
# ============================================================================

def update_mental_fingerprint(username):
    df = get_user_history(username)
    if len(df) < 3:
        return
    df = df.sort_values("date")
    baseline_sleep = df["sleep_hours"].median()
    baseline_stress = df["stress_level"].median()
    baseline_anxiety = df["anxiety_level"].median()
    baseline_exercise = df["exercise_minutes"].median()
    mood_map = {"Very Bad": 1, "Bad": 2, "Neutral": 3, "Good": 4, "Very Good": 5}
    df["mood_num"] = df["mood"].map(mood_map)
    baseline_mood = df["mood_num"].median()
    df["wellness_score"] = df.apply(
        lambda row: calculate_wellness_score(
            row["stress_level"], row["sleep_hours"], row["anxiety_level"], row["exercise_minutes"]
        ), axis=1
    )
    correlations = {}
    for col in ["sleep_hours", "stress_level", "anxiety_level", "exercise_minutes"]:
        if df[col].std() > 0:
            corr = df[col].corr(df["wellness_score"])
            correlations[col] = abs(corr) if not pd.isna(corr) else 0.1
        else:
            correlations[col] = 0.1
    if df["mood_num"].std() > 0:
        mood_corr = df["mood_num"].corr(df["wellness_score"])
        correlations["mood"] = abs(mood_corr) if not pd.isna(mood_corr) else 0.1
    else:
        correlations["mood"] = 0.1
    total = sum(correlations.values())
    weights = {k: v/total for k, v in correlations.items()}
    volatility = df["wellness_score"].std() if len(df) > 1 else 0
    if len(df) >= 5:
        wellness_series = df["wellness_score"].values
        autocorr = np.corrcoef(wellness_series[:-1], wellness_series[1:])[0, 1]
        pattern_stability = autocorr if not pd.isna(autocorr) else 0
    else:
        pattern_stability = 0
    conn = get_connection()
    conn.execute(
        """INSERT INTO mental_fingerprints 
           (username, baseline_sleep, baseline_stress, baseline_anxiety, baseline_exercise, baseline_mood,
            sleep_weight, stress_weight, anxiety_weight, exercise_weight, mood_weight,
            volatility_score, pattern_stability, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(username) DO UPDATE SET
             baseline_sleep=excluded.baseline_sleep, baseline_stress=excluded.baseline_stress,
             baseline_anxiety=excluded.baseline_anxiety, baseline_exercise=excluded.baseline_exercise,
             baseline_mood=excluded.baseline_mood, sleep_weight=excluded.sleep_weight,
             stress_weight=excluded.stress_weight, anxiety_weight=excluded.anxiety_weight,
             exercise_weight=excluded.exercise_weight, mood_weight=excluded.mood_weight,
             volatility_score=excluded.volatility_score, pattern_stability=excluded.pattern_stability,
             updated_at=excluded.updated_at""",
        (username, baseline_sleep, baseline_stress, baseline_anxiety, baseline_exercise, baseline_mood,
         weights["sleep_hours"], weights["stress_level"], weights["anxiety_level"],
         weights["exercise_minutes"], weights["mood"],
         volatility, pattern_stability, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def get_fingerprint(username):
    init_db()
    conn = get_connection()
    row = conn.execute("SELECT * FROM mental_fingerprints WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def calculate_personalized_wellness_score(stress, sleep, anxiety, exercise, mood, username):
    fingerprint = get_fingerprint(username)
    mood_map = {"Very Bad": 1, "Bad": 2, "Neutral": 3, "Good": 4, "Very Good": 5}
    mood_val = mood_map.get(mood, 3)
    if fingerprint:
        score = (
            (10 - stress) * 5 * fingerprint["stress_weight"] +
            min(sleep, 10) * 3 * fingerprint["sleep_weight"] +
            (10 - anxiety) * 5 * fingerprint["anxiety_weight"] +
            min(exercise, 120) / 2 * fingerprint["exercise_weight"] +
            mood_val * 10 * fingerprint["mood_weight"]
        )
        score = score * (100 / (
            5 * fingerprint["stress_weight"] * 10 +
            3 * fingerprint["sleep_weight"] * 10 +
            5 * fingerprint["anxiety_weight"] * 10 +
            60 * fingerprint["exercise_weight"] +
            50 * fingerprint["mood_weight"]
        ))
    else:
        score = calculate_wellness_score(stress, sleep, anxiety, exercise)
    return min(max(score, 0), 100)


def get_user_history(username):
    init_db()
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM user_history WHERE username=? ORDER BY date", conn, params=(username,))
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["wellness_score"] = df.apply(
        lambda row: calculate_wellness_score(
            row["stress_level"], row["sleep_hours"], row["anxiety_level"], row["exercise_minutes"]
        ), axis=1
    )
    return df.dropna(subset=["date"])


# ============================================================================
# FEATURE 2: TRIGGER DISCOVERY ENGINE
# ============================================================================

def discover_triggers(username):
    df = get_user_history(username)
    if len(df) < 5:
        return
    df = df.sort_values("date").reset_index(drop=True)
    df["risk"] = df["wellness_score"].apply(lambda x: "High" if x < 40 else ("Medium" if x < 70 else "Low"))
    high_risk_indices = df[df["risk"] == "High"].index.tolist()
    if not high_risk_indices:
        return
    triggers_found = []
    for idx in high_risk_indices:
        window_start = max(0, idx - 3)
        window = df.iloc[window_start:idx]
        if len(window) < 2:
            continue
        if window["sleep_hours"].iloc[-1] < window["sleep_hours"].mean() - 1.5:
            triggers_found.append({
                "type": "sleep_drop", "name": "Sleep Drop",
                "description": f"Sleep decreased to {window['sleep_hours'].iloc[-1]:.1f}h before high-risk period",
                "lead_time": (df.iloc[idx]["date"] - window["date"].iloc[-1]).total_seconds() / 86400
            })
        if window["stress_level"].iloc[-1] > window["stress_level"].mean() + 2:
            triggers_found.append({
                "type": "stress_spike", "name": "Stress Spike",
                "description": f"Stress spiked to {window['stress_level'].iloc[-1]:.0f}/10 before high-risk period",
                "lead_time": (df.iloc[idx]["date"] - window["date"].iloc[-1]).total_seconds() / 86400
            })
        if window["exercise_minutes"].iloc[-1] < window["exercise_minutes"].mean() * 0.5:
            triggers_found.append({
                "type": "exercise_drop", "name": "Exercise Drop",
                "description": f"Exercise dropped to {window['exercise_minutes'].iloc[-1]:.0f}min before high-risk period",
                "lead_time": (df.iloc[idx]["date"] - window["date"].iloc[-1]).total_seconds() / 86400
            })
        if window["anxiety_level"].iloc[-1] > window["anxiety_level"].mean() + 2:
            triggers_found.append({
                "type": "anxiety_spike", "name": "Anxiety Spike",
                "description": f"Anxiety spiked to {window['anxiety_level'].iloc[-1]:.0f}/10 before high-risk period",
                "lead_time": (df.iloc[idx]["date"] - window["date"].iloc[-1]).total_seconds() / 86400
            })
    trigger_counts = defaultdict(lambda: {"count": 0, "lead_times": [], "descriptions": []})
    for t in triggers_found:
        trigger_counts[t["type"]]["count"] += 1
        trigger_counts[t["type"]]["lead_times"].append(t["lead_time"])
        trigger_counts[t["type"]]["descriptions"].append(t["description"])
    init_db()
    conn = get_connection()
    for trigger_type, data in trigger_counts.items():
        confidence = min(data["count"] / len(high_risk_indices), 1.0)
        avg_lead = np.mean(data["lead_times"]) if data["lead_times"] else 1.0
        conn.execute(
            """INSERT INTO trigger_patterns 
               (username, trigger_name, trigger_type, confidence, frequency, avg_lead_time, description, discovered_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT DO NOTHING""",
            (username, trigger_type.replace("_", " ").title(), trigger_type, confidence, 
             data["count"], avg_lead, data["descriptions"][0] if data["descriptions"] else "",
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
    conn.commit()
    conn.close()


def get_triggers(username):
    init_db()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM trigger_patterns WHERE username=? ORDER BY confidence DESC, frequency DESC",
        (username,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================================
# FEATURE 3: MENTAL HEALTH MOMENTUM
# ============================================================================

def update_momentum_tracking(username):
    df = get_user_history(username)
    if len(df) < 3:
        return
    df = df.sort_values("date").reset_index(drop=True)
    wellness = df["wellness_score"].values
    if len(wellness) >= 2:
        velocity = wellness[-1] - wellness[-2]
    else:
        velocity = 0
    if len(wellness) >= 3:
        prev_velocity = wellness[-2] - wellness[-3]
        acceleration = velocity - prev_velocity
    else:
        acceleration = 0
    n = min(7, len(wellness))
    x = np.arange(n)
    y = wellness[-n:]
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    trend_strength = r_value ** 2
    momentum_score = velocity + 0.5 * acceleration + slope * 3
    if momentum_score > 2:
        direction = "Improving"
    elif momentum_score < -2:
        direction = "Deteriorating"
    else:
        direction = "Stable"
    forecast = intercept + slope * (n + 6)
    forecast = min(max(forecast, 0), 100)
    init_db()
    conn = get_connection()
    conn.execute(
        """INSERT INTO momentum_tracking 
           (username, date, momentum_score, momentum_direction, velocity, acceleration, trend_strength, forecast_next_7)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), momentum_score, direction,
         velocity, acceleration, trend_strength, forecast)
    )
    conn.commit()
    conn.close()


def get_latest_momentum(username):
    init_db()
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM momentum_tracking WHERE username=? ORDER BY date DESC LIMIT 1",
        (username,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_momentum_history(username):
    init_db()
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM momentum_tracking WHERE username=? ORDER BY date",
        conn, params=(username,)
    )
    conn.close()
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df


# ============================================================================
# FEATURE 4: INTERVENTION RECEPTIVITY
# ============================================================================

def calculate_intervention_receptivity(username, intervention_type):
    init_db()
    conn = get_connection()
    responses = conn.execute(
        "SELECT * FROM intervention_responses WHERE username=? AND intervention_type=?",
        (username, intervention_type)
    ).fetchall()
    if not responses:
        conn.close()
        return {
            "receptivity_score": 0.5,
            "historical_response_rate": 0.0,
            "optimal_timing": "morning",
            "preferred_channel": "in-app",
            "personalization_notes": "No prior interaction history. Default moderate receptivity."
        }
    responses = [dict(r) for r in responses]
    total_recommended = len(responses)
    total_responded = len([r for r in responses if r["responded_at"] is not None])
    response_rate = total_responded / total_recommended if total_recommended > 0 else 0
    engagement_scores = [r["engagement_score"] for r in responses if r["engagement_score"] is not None]
    avg_engagement = np.mean(engagement_scores) if engagement_scores else 0.5
    successful = [r for r in responses if r["engagement_score"] is not None and r["engagement_score"] > 0.6]
    if successful:
        hours = [datetime.strptime(r["recommended_at"], "%Y-%m-%d %H:%M:%S").hour for r in successful]
        avg_hour = np.mean(hours)
        if 5 <= avg_hour < 12:
            optimal = "morning"
        elif 12 <= avg_hour < 17:
            optimal = "afternoon"
        elif 17 <= avg_hour < 22:
            optimal = "evening"
        else:
            optimal = "night"
    else:
        optimal = "morning"
    receptivity = (response_rate * 0.4 + avg_engagement * 0.6)
    df = get_user_history(username)
    if not df.empty:
        latest = df.iloc[-1]
        current_wellness = calculate_wellness_score(
            latest["stress_level"], latest["sleep_hours"],
            latest["anxiety_level"], latest["exercise_minutes"]
        )
        if current_wellness < 30:
            receptivity *= 0.7
        if latest["stress_level"] > 7:
            preferred_channel = "quick-action"
        else:
            preferred_channel = "guided"
    else:
        preferred_channel = "in-app"
    conn.close()
    return {
        "receptivity_score": min(receptivity, 1.0),
        "historical_response_rate": response_rate,
        "optimal_timing": optimal,
        "preferred_channel": preferred_channel,
        "personalization_notes": f"Based on {total_recommended} past recommendations."
    }


def save_intervention_response(username, intervention_type, recommended_at, responded_at=None,
                                response_type=None, engagement_score=None, outcome_score=None, feedback=None):
    init_db()
    conn = get_connection()
    conn.execute(
        """INSERT INTO intervention_responses 
           (username, intervention_type, recommended_at, responded_at, response_type, 
            engagement_score, outcome_score, feedback)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (username, intervention_type, recommended_at, responded_at, response_type,
         engagement_score, outcome_score, feedback)
    )
    conn.commit()
    conn.close()


def get_all_receptivity_scores(username):
    intervention_types = ["breathing", "journaling", "exercise", "sleep_hygiene", 
                          "social_connection", "mindfulness", "professional_help"]
    return {it: calculate_intervention_receptivity(username, it) for it in intervention_types}


# ============================================================================
# FEATURE 5: RECOVERY PATTERN ANALYSIS
# ============================================================================

def analyze_recovery_patterns(username):
    df = get_user_history(username)
    if len(df) < 5:
        return []
    df = df.sort_values("date").reset_index(drop=True)
    wellness = df["wellness_score"].values
    fingerprint = get_fingerprint(username)
    baseline = fingerprint["baseline_sleep"] * 3 + 30 if fingerprint else 60
    episodes = []
    in_episode = False
    episode_start = None
    episode_min = 100
    for i, score in enumerate(wellness):
        if score < 40 and not in_episode:
            in_episode = True
            episode_start = i
            episode_min = score
        elif score < 40 and in_episode:
            episode_min = min(episode_min, score)
        elif score >= 40 and in_episode:
            in_episode = False
            episodes.append({
                "start_idx": episode_start, "end_idx": i - 1, "min_score": episode_min,
                "start_date": df.iloc[episode_start]["date"], "end_date": df.iloc[i - 1]["date"]
            })
    if in_episode:
        episodes.append({
            "start_idx": episode_start, "end_idx": len(wellness) - 1, "min_score": episode_min,
            "start_date": df.iloc[episode_start]["date"], "end_date": df.iloc[-1]["date"]
        })
    recoveries = []
    init_db()
    conn = get_connection()
    for ep in episodes:
        recovery_start = ep["end_idx"] + 1
        if recovery_start >= len(wellness):
            continue
        recovery_scores = wellness[recovery_start:]
        baseline_target = baseline * 0.8
        recovery_idx = None
        for j, score in enumerate(recovery_scores):
            if score >= baseline_target:
                recovery_idx = recovery_start + j
                break
        if recovery_idx is not None:
            recovery_duration = (df.iloc[recovery_idx]["date"] - ep["start_date"]).days
            recovery_rate = (wellness[recovery_idx] - ep["min_score"]) / max(recovery_duration, 1)
            baseline_return = (wellness[recovery_idx] / baseline) * 100 if baseline > 0 else 0
            conn.execute(
                """INSERT INTO recovery_patterns 
                   (username, episode_date, episode_type, episode_severity, recovery_start_date,
                    recovery_end_date, recovery_duration_days, recovery_rate, baseline_return_pct,
                    intervention_used, intervention_effectiveness)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT DO NOTHING""",
                (username, ep["start_date"].strftime("%Y-%m-%d %H:%M:%S"), "wellness_dip",
                 ep["min_score"], ep["end_date"].strftime("%Y-%m-%d %H:%M:%S"),
                 df.iloc[recovery_idx]["date"].strftime("%Y-%m-%d %H:%M:%S"),
                 recovery_duration, recovery_rate, baseline_return, "unknown", 0.0)
            )
            recoveries.append({
                "episode_date": ep["start_date"], "severity": ep["min_score"],
                "recovery_duration": recovery_duration, "recovery_rate": recovery_rate,
                "baseline_return": baseline_return
            })
    conn.commit()
    conn.close()
    return recoveries


def get_recovery_patterns(username):
    init_db()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM recovery_patterns WHERE username=? ORDER BY episode_date DESC",
        (username,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================================
# FEATURE 6: INTERVENTION EXPERIMENT
# ============================================================================

def create_intervention_experiment(username, experiment_name, intervention_type, start_date, notes=""):
    init_db()
    conn = get_connection()
    df = get_user_history(username)
    if not df.empty:
        pre_df = df[df["date"] < pd.Timestamp(start_date)]
        if len(pre_df) >= 3:
            pre_score = pre_df["wellness_score"].mean()
        else:
            pre_score = None
    else:
        pre_score = None
    conn.execute(
        """INSERT INTO intervention_experiments 
           (username, experiment_name, intervention_type, start_date, status, pre_score, notes, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (username, experiment_name, intervention_type, start_date, "active",
         pre_score, notes, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def complete_intervention_experiment(experiment_id, end_date):
    init_db()
    conn = get_connection()
    exp = conn.execute(
        "SELECT * FROM intervention_experiments WHERE id=?", (experiment_id,)
    ).fetchone()
    if not exp:
        conn.close()
        return None
    exp = dict(exp)
    username = exp["username"]
    start_date = exp["start_date"]
    df = get_user_history(username)
    if not df.empty:
        post_df = df[(df["date"] >= pd.Timestamp(start_date)) & (df["date"] <= pd.Timestamp(end_date))]
        pre_df = df[df["date"] < pd.Timestamp(start_date)]
        if len(post_df) >= 3 and len(pre_df) >= 3:
            post_scores = post_df["wellness_score"].values
            pre_scores = pre_df["wellness_score"].values[-7:]
            post_mean = np.mean(post_scores)
            pre_mean = np.mean(pre_scores)
            pooled_std = np.sqrt((np.std(pre_scores)**2 + np.std(post_scores)**2) / 2)
            effect_size = (post_mean - pre_mean) / pooled_std if pooled_std > 0 else 0
            t_stat, p_value = stats.ttest_ind(pre_scores, post_scores)
            is_significant = 1 if p_value < 0.05 else 0
            conn.execute(
                """UPDATE intervention_experiments SET
                   end_date=?, status=?, post_score=?, effect_size=?, p_value=?,
                   is_significant=?, sample_size=?
                   WHERE id=?""",
                (end_date, "completed", post_mean, effect_size, p_value,
                 is_significant, len(post_scores), experiment_id)
            )
            conn.commit()
            conn.close()
            return {
                "pre_score": pre_mean, "post_score": post_mean,
                "effect_size": effect_size, "p_value": p_value,
                "is_significant": bool(is_significant), "improvement": post_mean - pre_mean
            }
    conn.execute(
        "UPDATE intervention_experiments SET end_date=?, status=? WHERE id=?",
        (end_date, "insufficient_data", experiment_id)
    )
    conn.commit()
    conn.close()
    return None


def get_experiments(username):
    init_db()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM intervention_experiments WHERE username=? ORDER BY created_at DESC",
        (username,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_active_experiments(username):
    init_db()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM intervention_experiments WHERE username=? AND status='active' ORDER BY start_date DESC",
        (username,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================================
# ORIGINAL HELPER FUNCTIONS
# ============================================================================

def save_journal_entry(username, text, sentiment, polarity):
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

def get_journal_entries(username=None):
    if not os.path.exists(JOURNAL_CSV):
        return pd.DataFrame(columns=["id", "username", "date", "text", "sentiment", "polarity"])
    df = pd.read_csv(JOURNAL_CSV)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if username:
        df = df[df["username"].astype(str) == str(username)]
    return df.sort_values("date", ascending=False).reset_index(drop=True)

def delete_journal_entry(entry_id):
    if not os.path.exists(JOURNAL_CSV):
        return
    df = pd.read_csv(JOURNAL_CSV)
    df = df[df["id"].astype(str) != str(entry_id)]
    df.to_csv(JOURNAL_CSV, index=False)

def delete_all_journal_entries(username):
    if not os.path.exists(JOURNAL_CSV):
        return
    df = pd.read_csv(JOURNAL_CSV)
    df = df[df["username"].astype(str) != str(username)]
    df.to_csv(JOURNAL_CSV, index=False)

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
            <span class="user-pill">👤 {st.session_state.current_user}</span>
        </div>
        """, unsafe_allow_html=True)
        if st.sidebar.button("🚪 Log out", use_container_width=True):
            logout_user()
            st.rerun()
        st.sidebar.markdown("---")

def delete_entry(entry_id):
    conn = get_connection()
    conn.execute("DELETE FROM user_history WHERE id=?", (int(entry_id),))
    conn.commit()
    conn.close()


def delete_all_entries(username):
    conn = get_connection()
    conn.execute("DELETE FROM user_history WHERE username=?", (username,))
    conn.commit()
    conn.close()


def calculate_wellness_score(stress, sleep, anxiety, exercise):
    score = 0
    score += (10 - stress) * 5
    score += min(sleep, 10) * 3
    score += (10 - anxiety) * 5
    score += min(exercise, 120) / 2
    return min(score, 100)

def predict_risk(stress, sleep, anxiety, exercise, mood):
    wellness_score = calculate_wellness_score(stress, sleep, anxiety, exercise)
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
    if not factors:
        factors = ["Good overall wellness indicators"]
    return risk, factors, wellness_score

def get_recommendations(stress, sleep, anxiety, exercise):
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
            row["stress_level"], row["sleep_hours"], row["anxiety_level"], row["exercise_minutes"]
        ),
        axis=1,
    )
    return df.dropna(subset=["date"])

def get_prediction_data():
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

def style_plot(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(27,36,48,0.02)",
        font={"color": COLOR_INK, "family": "Inter, sans-serif"},
        title_font={"family": "Fraunces, serif", "color": COLOR_INK, "size": 17},
        margin=dict(l=20, r=20, t=50, b=20),
        legend={"font": {"color": COLOR_MUTED}},
    )
    fig.update_xaxes(gridcolor="rgba(27,36,48,0.07)", color=COLOR_MUTED)
    fig.update_yaxes(gridcolor="rgba(27,36,48,0.07)", color=COLOR_MUTED)
    return fig

def create_wellness_radar(sleep, stress, anxiety, exercise, mood):
    mood_scale = {"Very Bad": 2, "Bad": 4, "Neutral": 6, "Good": 8, "Very Good": 10}
    categories = ["Sleep", "Exercise", "Mood", "Stress Balance", "Anxiety Balance"]
    values = [
        min(float(sleep), 10), min(float(exercise) / 12, 10), mood_scale.get(mood, 6),
        10 - float(stress), 10 - float(anxiety),
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
    fig.add_trace(go.Bar(name="Healthy Target", x=categories, y=healthy_targets, marker_color=COLOR_SLATE))
    fig.update_layout(barmode="group", title="Your Wellness Factors vs Healthy Targets")
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


# ============================================================================
# NEW VISUALIZATION FUNCTIONS FOR RESEARCH FEATURES
# ============================================================================

def create_fingerprint_radar(fingerprint):
    categories = ["Sleep\nImpact", "Stress\nImpact", "Anxiety\nImpact", "Exercise\nImpact", "Mood\nImpact"]
    values = [
        fingerprint["sleep_weight"] * 100,
        fingerprint["stress_weight"] * 100,
        fingerprint["anxiety_weight"] * 100,
        fingerprint["exercise_weight"] * 100,
        fingerprint["mood_weight"] * 100,
    ]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]], theta=categories + [categories[0]], fill="toself",
        name="Your Fingerprint", line_color=COLOR_RESEARCH, fillcolor="rgba(107,91,149,0.20)",
        line=dict(width=3)
    ))
    fig.update_layout(
        title="Your Mental Health Fingerprint — What Affects You Most",
        polar=dict(bgcolor="rgba(0,0,0,0)",
                   radialaxis=dict(visible=True, range=[0, 50], tickfont=dict(color=COLOR_MUTED)),
                   angularaxis=dict(tickfont=dict(color=COLOR_INK, size=11))),
        showlegend=False,
    )
    return style_plot(fig)


def create_momentum_chart(momentum_df):
    if momentum_df.empty or len(momentum_df) < 2:
        return None
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Wellness Velocity & Acceleration", "Momentum Direction Over Time"),
        row_heights=[0.6, 0.4],
        vertical_spacing=0.12
    )
    fig.add_trace(
        go.Scatter(x=momentum_df["date"], y=momentum_df["velocity"], 
                   mode="lines+markers", name="Velocity", line=dict(color=COLOR_PRIMARY, width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=momentum_df["date"], y=momentum_df["acceleration"],
                   mode="lines+markers", name="Acceleration", line=dict(color=COLOR_MEDIUM, width=2)),
        row=1, col=1
    )
    fig.add_hline(y=0, line_dash="dot", line_color=COLOR_MUTED, row=1, col=1)
    colors = [COLOR_MOMENTUM_UP if d == "Improving" else (COLOR_MOMENTUM_DOWN if d == "Deteriorating" else COLOR_SLATE) 
              for d in momentum_df["momentum_direction"]]
    fig.add_trace(
        go.Bar(x=momentum_df["date"], y=momentum_df["momentum_score"],
               marker_color=colors, name="Momentum Score"),
        row=2, col=1
    )
    fig.update_layout(height=500, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02))
    return style_plot(fig)


def create_trigger_timeline(df, triggers):
    if df.empty or not triggers:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["wellness_score"],
        mode="lines+markers", name="Wellness Score",
        line=dict(color=COLOR_PRIMARY, width=2)
    ))
    fig.add_hline(y=40, line_dash="dash", line_color=COLOR_HIGH, 
                  annotation_text="High Risk Threshold")
    for trigger in triggers[:5]:
        fig.add_annotation(
            x=pd.Timestamp(trigger["discovered_at"]),
            y=50,
            text=f"⚡ {trigger['trigger_name']}",
            showarrow=True,
            arrowhead=2,
            arrowcolor=COLOR_RESEARCH,
            ax=0, ay=-40
        )
    fig.update_layout(title="Trigger Discovery Timeline", height=400)
    return style_plot(fig)


def create_recovery_chart(recoveries):
    if not recoveries:
        return None
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Recovery Duration", "Recovery Rate"),
        specs=[[{"type": "bar"}, {"type": "scatter"}]]
    )
    episodes = [f"Ep {i+1}" for i in range(len(recoveries))]
    durations = [r["recovery_duration"] for r in recoveries]
    rates = [r["recovery_rate"] for r in recoveries]
    severities = [r["severity"] for r in recoveries]
    fig.add_trace(go.Bar(x=episodes, y=durations, marker_color=COLOR_PRIMARY, name="Days to Recover"), row=1, col=1)
    fig.add_trace(go.Scatter(x=episodes, y=rates, mode="lines+markers", 
                               marker=dict(size=severities, color=COLOR_RESEARCH), name="Recovery Rate"), row=1, col=2)
    fig.update_layout(height=350, showlegend=False)
    return style_plot(fig)


def create_experiment_results_chart(experiments):
    if not experiments:
        return None
    completed = [e for e in experiments if e["status"] == "completed" and e["pre_score"] is not None]
    if not completed:
        return None
    fig = go.Figure()
    names = [e["experiment_name"] for e in completed]
    pre_scores = [e["pre_score"] for e in completed]
    post_scores = [e["post_score"] for e in completed]
    fig.add_trace(go.Bar(name="Pre-Intervention", x=names, y=pre_scores, marker_color=COLOR_SLATE))
    fig.add_trace(go.Bar(name="Post-Intervention", x=names, y=post_scores, marker_color=COLOR_PRIMARY))
    fig.update_layout(title="Intervention Experiment Results", barmode="group", height=400)
    return style_plot(fig)


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
PAGES = [
    "🏠 Home", "📋 Assessment", "🤖 Risk Prediction", "🎯 Goals",
    "📂 Bulk Upload", "📈 Dashboard", "📝 Journal", "📓 My Journals", "🗂️ My Entries",
    "🆘 Support & Coping", "📄 Report", "📊 Admin",
    "🔬 Research Lab"
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


# ============================================================================
# HOME PAGE
# ============================================================================
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
        if st.button("📋 Start New Assessment", use_container_width=True):
            st.session_state['nav_to'] = 'assessment'
            st.rerun()
    with col2:
        if st.button("📝 Write in Journal", use_container_width=True):
            st.session_state['nav_to'] = 'journal'
            st.rerun()
    with col3:
        if st.button("🆘 I Need Support Now", use_container_width=True):
            st.session_state['nav_to'] = 'support'
            st.rerun()

    st.markdown("## 🔬 Research Features")
    st.caption("Advanced analytics that learn your unique patterns")
    rcol1, rcol2, rcol3 = st.columns(3)
    with rcol1:
        if st.button("🔍 View My Fingerprint", use_container_width=True):
            st.session_state['page_radio'] = "🔬 Research Lab"
            st.session_state['research_tab'] = 'fingerprint'
            st.rerun()
    with rcol2:
        if st.button("📊 Check Momentum", use_container_width=True):
            st.session_state['page_radio'] = "🔬 Research Lab"
            st.session_state['research_tab'] = 'momentum'
            st.rerun()
    with rcol3:
        if st.button("🧪 Run Experiment", use_container_width=True):
            st.session_state['page_radio'] = "🔬 Research Lab"
            st.session_state['research_tab'] = 'experiments'
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

            momentum = get_latest_momentum(st.session_state.current_user)
            if momentum:
                pulse_divider()
                st.markdown("## 🌊 Mental Health Momentum")
                mcol1, mcol2, mcol3 = st.columns(3)
                mcol1.metric("Direction", momentum["momentum_direction"])
                mcol2.metric("Velocity", f"{momentum['velocity']:+.1f}")
                mcol3.metric("7-Day Forecast", f"{momentum['forecast_next_7']:.0f}/100")

                if momentum["momentum_direction"] == "Deteriorating":
                    st.warning("Your wellness trend is declining. Consider visiting **Support & Coping** or **Research Lab** for insights.")
                elif momentum["momentum_direction"] == "Improving":
                    st.success("Your wellness trend is improving! Keep up the good work.")
    except Exception:
        pass

    pulse_divider()
    wellness_tips = [
        "Take a 5-minute walk outside 🌳", "Practice deep breathing for 2 minutes 🧘",
        "Drink a glass of water 💧", "Call a friend or family member 📞",
        "Write down 3 things you're grateful for ✍️", "Stretch your body for 10 minutes 🤸",
        "Listen to your favorite song 🎵", "Take a short break from screens 📵"
    ]
    st.markdown("## 🌟 Daily Wellness Tip")
    st.info(random.choice(wellness_tips))

    pulse_divider()
    quotes = [
        "The greatest glory in living lies not in never falling, but in rising every time we fall. – Nelson Mandela",
        "The way to get started is to quit talking and begin doing. – Walt Disney",
        "Your time is limited, don't waste it living someone else's life. – Steve Jobs",
        "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt",
        "It does not matter how slowly you go as long as you do not stop. – Confucius"
    ]
    st.markdown("## 💬 Motivation")
    st.success(random.choice(quotes))

# ============================================================================
# ASSESSMENT PAGE
# ============================================================================
elif page == "📋 Assessment":
    require_login()
    page_header("📋", "Daily Check-in", "Mental Health Assessment",
                "A few quick questions to understand how you're doing today.")

    username = st.text_input("👤 Your name", st.session_state.get("current_user", "Guest User"))
    entry_date = st.date_input("📅 Date of this assessment", value=datetime.now().date())

    st.markdown("## Answer the following questions:")
    mood_emojis = {"Very Bad": "😢", "Bad": "😔", "Neutral": "😐", "Good": "😊", "Very Good": "😄"}
    mood = st.select_slider(
        "How is your mood today?", options=["Very Bad", "Bad", "Neutral", "Good", "Very Good"],
        value="Good", format_func=lambda x: f"{mood_emojis[x]} {x}"
    )

    col1, col2 = st.columns(2)
    with col1:
        sleep_hours = st.slider("😴 How many hours did you sleep last night?", 0, 12, 7)
        stress_level = st.slider("😰 How stressed are you? (0-10)", 0, 10, 3)
    with col2:
        anxiety_level = st.slider("😟 How anxious are you? (0-10)", 0, 10, 3)
        exercise_minutes = st.slider("🏃 How many minutes did you exercise today?", 0, 180, 30)

    personalized_score = calculate_personalized_wellness_score(
        stress_level, sleep_hours, anxiety_level, exercise_minutes, mood, username
    )
    preview_score = calculate_wellness_score(stress_level, sleep_hours, anxiety_level, exercise_minutes)

    score_col1, score_col2 = st.columns(2)
    with score_col1:
        st.metric("Standard Wellness Score", f"{preview_score}/100")
    with score_col2:
        fingerprint = get_fingerprint(username)
        if fingerprint:
            st.metric("Your Personalized Score", f"{personalized_score:.0f}/100", 
                     help="Based on your unique mental health fingerprint")
        else:
            st.caption("Complete more assessments to unlock your personalized score")

    goals = get_goals(username)
    if goals:
        st.caption(
            f"🎯 Your goals: {goals['target_sleep']:.0f}h sleep · "
            f"{goals['target_exercise']:.0f} min exercise · stress under {goals['target_stress_max']:.0f}"
        )

    if st.button("✅ Submit Assessment"):
        save_user_history(username, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes, entry_date=entry_date)
        st.session_state['assessment_data'] = {
            "username": username, "date": entry_date, "mood": mood, "sleep_hours": sleep_hours,
            "stress_level": stress_level, "anxiety_level": anxiety_level, "exercise_minutes": exercise_minutes
        }
        st.success(f"🎉 Assessment saved for {entry_date.strftime('%Y-%m-%d')}!")

        active_exps = get_active_experiments(username)
        if active_exps:
            st.info(f"📊 This entry will contribute to {len(active_exps)} active intervention experiment(s).")

# ============================================================================
# RISK PREDICTION PAGE
# ============================================================================
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

        risk, factors, wellness_score = predict_risk(stress, sleep, anxiety, exercise, mood)
        recommendations = get_recommendations(stress, sleep, anxiety, exercise)

        st.markdown("## 📊 Prediction Results")
        st.plotly_chart(gauge_figure(wellness_score, "Wellness Score"), use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            risk_badge(risk)
        with col2:
            st.metric("Wellness Score", f"{wellness_score}/100")

        compare_col, radar_col = st.columns(2)
        with compare_col:
            st.plotly_chart(create_factor_bar(stress, sleep, anxiety, exercise), use_container_width=True)
        with radar_col:
            st.plotly_chart(create_wellness_radar(sleep, stress, anxiety, exercise, mood), use_container_width=True)

        st.markdown("## 🔍 Key Factors")
        for factor in factors:
            st.info(f"• {factor}")

        st.markdown("## 💡 Personalized Recommendations")
        for rec in recommendations:
            st.success(rec)

        pulse_divider()
        st.markdown("## 🎯 Intervention Receptivity")
        st.caption("Based on your past engagement patterns")

        receptivity = get_all_receptivity_scores(username)
        rec_cols = st.columns(3)
        interventions = ["breathing", "journaling", "exercise", "sleep_hygiene", "mindfulness", "social_connection"]
        for i, intervention in enumerate(interventions):
            with rec_cols[i % 3]:
                score = receptivity[intervention]["receptivity_score"]
                color = COLOR_GOOD if score > 0.6 else (COLOR_MEDIUM if score > 0.3 else COLOR_HIGH)
                st.markdown(f"""
                <div style="background: var(--card); border: 1px solid {color}40; border-radius: 8px; padding: 10px; margin-bottom: 8px;">
                    <div style="font-size: 0.75rem; color: {COLOR_MUTED}; text-transform: uppercase;">{intervention.replace('_', ' ')}</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: {color};">{score*100:.0f}%</div>
                    <div style="font-size: 0.7rem; color: {COLOR_MUTED};">{receptivity[intervention]['optimal_timing']}</div>
                </div>
                """, unsafe_allow_html=True)

        save_prediction(username, risk, wellness_score, factors)

        hist = get_history_data()
        mine = hist[hist["username"].astype(str) == str(username)] if not hist.empty else hist
        if not mine.empty and trend_nudge(mine):
            pulse_divider()
            st.warning(
                "Your recent check-ins suggest things have felt harder lately. "
                "That's worth paying attention to — consider reaching out to a professional "
                "or someone you trust. The **Support & Coping** page has resources if you'd like them."
            )

# ============================================================================
# GOALS PAGE
# ============================================================================
elif page == "🎯 Goals":
    require_login()
    page_header("🎯", "Personal Targets", "Your Wellness Goals",
                "Set targets that matter to you — we'll track your progress against them.")

    username = st.text_input("👤 Your name", st.session_state.get("current_user", "Guest User"), key="goals_username")
    existing = get_goals(username)

    col1, col2, col3 = st.columns(3)
    with col1:
        target_sleep = st.slider("🎯 Target sleep (hours)", 4, 10,
                                  int(existing["target_sleep"]) if existing else 8)
    with col2:
        target_exercise = st.slider("🎯 Target exercise (min/day)", 0, 120,
                                     int(existing["target_exercise"]) if existing else 30)
    with col3:
        target_stress_max = st.slider("🎯 Max comfortable stress", 0, 10,
                                       int(existing["target_stress_max"]) if existing else 5)

    if st.button("💾 Save Goals"):
        save_goals(username, target_sleep, target_exercise, target_stress_max)
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
            "target_stress_max": target_stress_max,
        }
        gcol1, gcol2, gcol3 = st.columns(3)
        gcol1.metric("Sleep (latest)", f"{last['sleep_hours']:.1f}h",
                     f"{last['sleep_hours'] - g['target_sleep']:+.1f}h vs goal")
        gcol2.metric("Exercise (latest)", f"{last['exercise_minutes']:.0f} min",
                     f"{last['exercise_minutes'] - g['target_exercise']:+.0f} min vs goal")
        gcol3.metric("Stress (latest)", f"{last['stress_level']:.0f}",
                     f"{last['stress_level'] - g['target_stress_max']:+.0f} vs max", delta_color="inverse")


# ============================================================================
# BULK UPLOAD PAGE
# ============================================================================
elif page == "📂 Bulk Upload":
    require_login()
    page_header("📂", "Batch Processing", "Bulk Upload & Analyze", "Upload an Excel file to analyze many records at once.")
    st.write(
        "Upload an Excel file (.xlsx) with multiple records to analyze them all at once, "
        "instead of entering them one by one in the Assessment page."
    )

    REQUIRED_COLUMNS = ["username", "mood", "sleep_hours", "stress_level", "anxiety_level", "exercise_minutes"]

    with st.expander("📋 Expected file format / download a template"):
        st.write(f"Your Excel file must contain these columns: `{'`, `'.join(REQUIRED_COLUMNS)}`")
        st.caption("`mood` must be one of: Very Bad, Bad, Neutral, Good, Very Good. A `date` column is optional.")
        template_df = pd.DataFrame([{
            "username": "John Doe", "mood": "Good", "sleep_hours": 7,
            "stress_level": 3, "anxiety_level": 2, "exercise_minutes": 30,
        }])
        st.download_button(
            label="📥 Download Template (Excel)", data=export_to_excel(template_df, sheet_name="Template"),
            file_name="bulk_upload_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

    if uploaded_file is not None:
        try:
            bulk_df = pd.read_excel(uploaded_file)
        except Exception as e:
            bulk_df = None
            st.error(f"❌ Couldn't read that file: {e}")

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

                risk_levels, wellness_scores, factor_lists = [], [], []
                for _, row in bulk_df.iterrows():
                    risk, factors, wellness = predict_risk(
                        row["stress_level"], row["sleep_hours"], row["anxiety_level"],
                        row["exercise_minutes"], row["mood"],
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
                    )
                with save_col:
                    if st.button("➕ Add these records to the backend data", use_container_width=True):
                        init_db()
                        conn = get_connection()
                        history_rows = bulk_df[["username", "date", "mood", "sleep_hours", "stress_level", "anxiety_level", "exercise_minutes"]].values.tolist()
                        conn.executemany(
                            """INSERT INTO user_history
                               (username, date, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes)
                               VALUES (?, ?, ?, ?, ?, ?, ?)""", history_rows,
                        )
                        prediction_rows = bulk_df[["username", "date", "risk_level", "wellness_score", "factors"]].values.tolist()
                        conn.executemany(
                            """INSERT INTO predictions (username, date, risk_level, wellness_score, factors)
                               VALUES (?, ?, ?, ?, ?)""", prediction_rows,
                        )
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Added {len(bulk_df)} records to the backend. They'll now show up in Dashboard and Admin.")

# ============================================================================
# DASHBOARD PAGE
# ============================================================================
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
            selected_user = st.selectbox("Filter by user", users)
        with filter_col2:
            min_date = history_df["date"].min().date()
            max_date = history_df["date"].max().date()
            selected_dates = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        with filter_col3:
            chart_style = st.selectbox("Chart mode", ["Smooth", "Detailed"])

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
            )

            trends_tab, dist_tab, insights_tab = st.tabs(["📈 Trends", "🧩 Distributions", "🔎 Insights"])

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
                corr_df = filtered_df[["sleep_hours", "stress_level", "anxiety_level", "exercise_minutes", "mood_num", "wellness_score"]].corr()
                heatmap = go.Figure(data=go.Heatmap(
                    z=corr_df.values, x=corr_df.columns, y=corr_df.index,
                    colorscale=[[0, COLOR_HIGH], [0.5, "#FFFFFF"], [1, COLOR_PRIMARY]],
                    zmin=-1, zmax=1, text=np.round(corr_df.values, 2), texttemplate="%{text}",
                ))
                heatmap.update_layout(title="Correlation Heatmap")
                st.plotly_chart(style_plot(heatmap), use_container_width=True)

                st.plotly_chart(create_mood_calendar(filtered_df), use_container_width=True)

                last_row = filtered_df.sort_values("date").iloc[-1]
                radar_col, info_col = st.columns([1.2, 1])
                with radar_col:
                    st.plotly_chart(create_wellness_radar(
                        last_row["sleep_hours"], last_row["stress_level"],
                        last_row["anxiety_level"], last_row["exercise_minutes"], last_row["mood"],
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


# ============================================================================
# JOURNAL PAGE
# ============================================================================
elif page == "📝 Journal":
    require_login()
    page_header("📝", "Reflection", "Journal & Sentiment Analysis", "Write about your day and we'll analyze your mood.")

    username = st.text_input("👤 Your name", st.session_state.get("current_user", "Guest User"), key="journal_username")
    journal_text = st.text_area("Your Journal Entry:", height=250, placeholder="How was your day? What made you happy or worried?")

    if st.button("🔍 Analyze & Save"):
        if journal_text.strip():
            sentiment, polarity = analyze_sentiment(journal_text)

            entry = save_journal_entry(username, journal_text.strip(), sentiment, polarity)

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

# ============================================================================
# MY JOURNALS PAGE
# ============================================================================
elif page == "📓 My Journals":
    require_login()
    page_header("📓", "Your Words", "My Journal History", "Review, reflect on, and manage your saved journal entries.")

    username = st.text_input("👤 Enter your name to view your journals", st.session_state.get("current_user", "Guest User"), key="my_journals_username")
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
            fig.add_hline(y=0, line_dash="dot", line_color=COLOR_MUTED, annotation_text="Neutral")
            st.plotly_chart(style_plot(fig), use_container_width=True)

        pulse_divider()
        st.markdown("### 📖 Your Entries")
        for _, row in df.iterrows():
            sentiment_emoji = {"positive": "😊", "negative": "😔", "neutral": "😐"}.get(row["sentiment"], "😐")
            with st.container():
                c1, c2, c3 = st.columns([2, 1, 0.8])
                c1.markdown(f"**{row['date'].strftime('%Y-%m-%d %H:%M')}** · {sentiment_emoji} {row['sentiment'].title()}")
                c2.write(f"Polarity: {row['polarity']:.3f}")
                if c3.button("🗑️", key=f"del_journal_{row['id']}", help="Delete this entry"):
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
            )
        with clear_col:
            if st.button("🧹 Clear all my journals", use_container_width=True):
                delete_all_journal_entries(username)
                st.success("All journal entries cleared.")
                st.rerun()

# ============================================================================
# MY ENTRIES PAGE
# ============================================================================
elif page == "🗂️ My Entries":
    require_login()
    page_header("🗂️", "Your Data", "My Entries", "Review, correct, or remove your own check-in history.")

    username = st.text_input("👤 Enter your name to view your entries", st.session_state.get("current_user", "Guest User"), key="my_entries_username")
    df = get_history_data()
    mine = df[df["username"].astype(str) == username].sort_values("date", ascending=False) if not df.empty else df

    if mine.empty:
        st.info("No entries found for this name yet.")
    else:
        st.caption(f"{len(mine)} entries found for **{username}**.")
        for _, row in mine.iterrows():
            c1, c2, c3, c4, c5 = st.columns([2, 1.2, 1, 1.2, 0.8])
            c1.markdown(f"**{row['date'].strftime('%Y-%m-%d %H:%M')}**")
            c2.write(f"Mood: {row['mood']}")
            c3.write(f"😴 {row['sleep_hours']:.0f}h")
            c4.write(f"Wellness: {row['wellness_score']:.0f}/100")
            if c5.button("🗑️", key=f"del_{row['id']}", help="Delete this entry"):
                delete_entry(row["id"])
                st.rerun()

        pulse_divider()
        st.download_button(
            "📥 Download My Data (Excel)",
            data=export_to_excel(mine.drop(columns=["mood_num"], errors="ignore"), sheet_name="My History"),
            file_name=f"{username}_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        if st.button("🧹 Clear all my entries", use_container_width=True):
            delete_all_entries(username)
            st.success("All entries cleared.")
            st.rerun()

# ============================================================================
# SUPPORT & COPING PAGE
# ============================================================================
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
        "What's one thing that felt hard today, and one thing that helped?",
        "What would I tell a friend who felt the way I feel right now?",
        "What's one small thing I can do in the next hour to take care of myself?",
    ]
    for p in prompts:
        st.info(p)

    pulse_divider()
    st.markdown("### 📞 If You Need to Talk to Someone")
    st.error("**US: 988 Suicide & Crisis Lifeline** — call or text **988**, available 24/7.")
    st.warning("**Crisis Text Line** — text **HOME** to **741741** (US & Canada).")
    st.info('**Outside the US** — search "[your country] crisis helpline" or contact local emergency services.')
    st.caption(
        "MindTrack is a self-reflection tool, not a diagnostic service or emergency line. "
        "If you are in immediate danger, please contact local emergency services right away."
    )

# ============================================================================
# REPORT PAGE
# ============================================================================
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

        risk, factors, wellness_score = predict_risk(stress, sleep, anxiety, exercise, mood)
        recommendations = get_recommendations(stress, sleep, anxiety, exercise)

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
                            file_name=f"mental_health_report_{username}.pdf", mime="application/pdf")


# ============================================================================
# ADMIN PAGE
# ============================================================================
elif page == "📊 Admin":
    require_login()
    page_header("📊", "Back Office", "Admin Dashboard", "Manage and export the underlying data.")

    st.markdown("## 📁 Data Management")
    st.caption(f"Backed by a SQL database (SQLite) at `{DB_PATH}`.")
    init_db()

    admin_tabs = st.tabs(["User History", "Predictions", "Goals", "Fingerprints", "Triggers", "Momentum", "Experiments"])

    with admin_tabs[0]:
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
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    with admin_tabs[1]:
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
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    with admin_tabs[2]:
        try:
            conn = get_connection()
            df_goals = pd.read_sql_query("SELECT * FROM goals", conn)
            conn.close()
            st.markdown("### 🎯 Saved Goals")
            st.dataframe(df_goals, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error: {e}")

    with admin_tabs[3]:
        try:
            conn = get_connection()
            df_fp = pd.read_sql_query("SELECT * FROM mental_fingerprints", conn)
            conn.close()
            st.markdown("### 🔬 Mental Health Fingerprints")
            st.dataframe(df_fp, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error: {e}")

    with admin_tabs[4]:
        try:
            conn = get_connection()
            df_trig = pd.read_sql_query("SELECT * FROM trigger_patterns", conn)
            conn.close()
            st.markdown("### ⚡ Discovered Triggers")
            st.dataframe(df_trig, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error: {e}")

    with admin_tabs[5]:
        try:
            conn = get_connection()
            df_mom = pd.read_sql_query("SELECT * FROM momentum_tracking", conn)
            conn.close()
            st.markdown("### 🌊 Momentum Tracking")
            st.dataframe(df_mom, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error: {e}")

    with admin_tabs[6]:
        try:
            conn = get_connection()
            df_exp = pd.read_sql_query("SELECT * FROM intervention_experiments", conn)
            conn.close()
            st.markdown("### 🧪 Intervention Experiments")
            st.dataframe(df_exp, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ============================================================================
# RESEARCH LAB PAGE — THE 6 NOVEL FEATURES
# ============================================================================
elif page == "🔬 Research Lab":
    require_login()
    page_header("🔬", "Advanced Analytics", "Research Lab", 
                "Cutting-edge features that learn your unique mental health patterns and fill research gaps.")

    username = st.text_input("👤 Your name", st.session_state.get("current_user", "Guest User"), key="research_username")

    default_tab = 0
    if 'research_tab' in st.session_state:
        tab_map = {'fingerprint': 0, 'triggers': 1, 'momentum': 2, 'receptivity': 3, 'recovery': 4, 'experiments': 5}
        default_tab = tab_map.get(st.session_state['research_tab'], 0)
        del st.session_state['research_tab']

    research_tabs = st.tabs([
        "🔍 Fingerprint", "⚡ Triggers", "🌊 Momentum", "🎯 Receptivity", 
        "🏥 Recovery", "🧪 Experiments"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: PERSONAL MENTAL HEALTH FINGERPRINT
    # -------------------------------------------------------------------------
    with research_tabs[0]:
        st.markdown("""
        <div class="research-card">
            <span class="research-badge">🔬 Research Feature 1</span>
            <h4>Personal Mental Health Fingerprint</h4>
            <p>Learns what factors affect <em>you</em> uniquely. Unlike generic wellness apps that treat everyone the same, 
            MindTrack analyzes your historical data to discover your personal sensitivity to sleep, stress, anxiety, 
            exercise, and mood — creating a unique "fingerprint" that personalizes your wellness score.</p>
        </div>
        """, unsafe_allow_html=True)

        fingerprint = get_fingerprint(username)
        df = get_user_history(username)

        if fingerprint and not df.empty and len(df) >= 3:
            col1, col2 = st.columns([1.2, 1])
            with col1:
                st.plotly_chart(create_fingerprint_radar(fingerprint), use_container_width=True)
            with col2:
                st.markdown("### Your Baseline Profile")
                st.markdown(f"**Sleep Baseline:** {fingerprint['baseline_sleep']:.1f}h")
                st.markdown(f"**Stress Baseline:** {fingerprint['baseline_stress']:.1f}/10")
                st.markdown(f"**Anxiety Baseline:** {fingerprint['baseline_anxiety']:.1f}/10")
                st.markdown(f"**Exercise Baseline:** {fingerprint['baseline_exercise']:.0f}min")

                st.markdown("### Your Stability Metrics")
                st.metric("Volatility Score", f"{fingerprint['volatility_score']:.1f}", 
                         help="How much your wellness scores vary. Lower = more stable.")
                st.metric("Pattern Stability", f"{fingerprint['pattern_stability']:.2f}",
                         help="How predictable your patterns are. Higher = more predictable.")

                weights = {
                    "Sleep": fingerprint["sleep_weight"],
                    "Stress": fingerprint["stress_weight"],
                    "Anxiety": fingerprint["anxiety_weight"],
                    "Exercise": fingerprint["exercise_weight"],
                    "Mood": fingerprint["mood_weight"]
                }
                dominant = max(weights, key=weights.get)
                st.info(f"🎯 **Your dominant factor:** {dominant} ({weights[dominant]*100:.0f}% influence on your wellness)")

            st.markdown("### How It Works")
            st.caption("""
            Your fingerprint is computed by correlating each wellness factor with your overall wellness score over time. 
            Factors with stronger correlations get higher weights in your personalized scoring. This addresses the research 
            gap of "one-size-fits-all" wellness models that assume all users are affected equally by the same factors.
            """)
        else:
            st.info("📊 Complete at least 3 assessments to generate your Mental Health Fingerprint. The more data you provide, the more accurate your personalized profile becomes.")

    # -------------------------------------------------------------------------
    # TAB 2: TRIGGER DISCOVERY ENGINE
    # -------------------------------------------------------------------------
    with research_tabs[1]:
        st.markdown("""
        <div class="research-card">
            <span class="research-badge">🔬 Research Feature 2</span>
            <h4>Trigger Discovery Engine</h4>
            <p>Automatically discovers patterns that precede your high-risk periods. Most mental health apps only 
            show current state — this engine looks backward through your history to find the specific triggers 
            (sleep drops, stress spikes, exercise gaps) that reliably predict your downturns.</p>
        </div>
        """, unsafe_allow_html=True)

        triggers = get_triggers(username)
        df = get_user_history(username)

        if triggers:
            st.markdown(f"### ⚡ Discovered {len(triggers)} Trigger Pattern(s)")

            for i, trigger in enumerate(triggers):
                confidence_color = COLOR_GOOD if trigger["confidence"] > 0.7 else (COLOR_MEDIUM if trigger["confidence"] > 0.4 else COLOR_HIGH)
                with st.container():
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.markdown(f"**{i+1}. {trigger['trigger_name']}**")
                    c1.caption(trigger["description"])
                    c2.markdown(f"<span style='color:{confidence_color};font-weight:700;'>{trigger['confidence']*100:.0f}% confidence</span>", unsafe_allow_html=True)
                    c2.caption(f"Observed {trigger['frequency']} time(s)")
                    c3.metric("Avg Lead Time", f"{trigger['avg_lead_time']:.1f} days")
                st.markdown("---")

            if not df.empty:
                st.markdown("### Trigger Timeline")
                fig = create_trigger_timeline(df, triggers)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Research Significance")
            st.caption("""
            Traditional mental health tracking is reactive — it tells you how you feel *now*. The Trigger Discovery Engine 
            is proactive — it identifies the early warning signals specific to *your* mental health patterns. This fills 
            a critical research gap in personalized early warning systems for mental health deterioration.
            """)
        else:
            st.info("🔍 No triggers discovered yet. Triggers are identified after you experience high-risk periods (wellness score < 40). Continue tracking to enable trigger discovery.")

    # -------------------------------------------------------------------------
    # TAB 3: MENTAL HEALTH MOMENTUM
    # -------------------------------------------------------------------------
    with research_tabs[2]:
        st.markdown("""
        <div class="research-card">
            <span class="research-badge">🔬 Research Feature 3</span>
            <h4>Mental Health Momentum</h4>
            <p>Detects whether your condition is improving or deteriorating using physics-inspired metrics: 
            <strong>velocity</strong> (rate of change), <strong>acceleration</strong> (change in velocity), and 
            <strong>trend strength</strong> (statistical confidence). Includes a 7-day forecast based on your trajectory.</p>
        </div>
        """, unsafe_allow_html=True)

        momentum = get_latest_momentum(username)
        momentum_df = get_momentum_history(username)

        if momentum:
            col1, col2, col3, col4 = st.columns(4)
            direction_emoji = "📈" if momentum["momentum_direction"] == "Improving" else ("📉" if momentum["momentum_direction"] == "Deteriorating" else "➡️")
            col1.metric(f"{direction_emoji} Direction", momentum["momentum_direction"])
            col2.metric("⚡ Velocity", f"{momentum['velocity']:+.1f}", help="Rate of wellness change per entry")
            col3.metric("🚀 Acceleration", f"{momentum['acceleration']:+.1f}", help="Whether change is speeding up or slowing")
            col4.metric("📊 Trend Strength", f"{momentum['trend_strength']:.2f}", help="R² of linear fit (0-1)")

            st.markdown("### 🔮 7-Day Forecast")
            forecast = momentum["forecast_next_7"]
            forecast_color = COLOR_GOOD if forecast > 70 else (COLOR_MEDIUM if forecast > 40 else COLOR_HIGH)
            st.markdown(f"""
            <div style="background: linear-gradient(90deg, {forecast_color}20, {forecast_color}05); 
                        border-left: 4px solid {forecast_color}; padding: 16px; border-radius: 8px;">
                <div style="font-size: 1.3rem; font-weight: 700; color: {forecast_color};">
                    Predicted Wellness: {forecast:.0f}/100
                </div>
                <div style="color: {COLOR_MUTED}; font-size: 0.9rem; margin-top: 4px;">
                    Based on your current trajectory. This is a statistical projection, not a guarantee.
                </div>
            </div>
            """, unsafe_allow_html=True)

            if not momentum_df.empty and len(momentum_df) >= 2:
                st.markdown("### Momentum History")
                fig = create_momentum_chart(momentum_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Research Significance")
            st.caption("""
            Most apps show static snapshots. Momentum analysis treats mental health as a dynamic system with inertia — 
            just like physical objects. This approach, inspired by dynamical systems theory in psychology research, 
            captures whether you're gaining or losing "mental health momentum" and predicts where you'll be in a week 
            if current trends continue.
            """)
        else:
            st.info("🌊 Complete at least 3 assessments to calculate your Mental Health Momentum. Each new entry refines the velocity, acceleration, and forecast.")

    # -------------------------------------------------------------------------
    # TAB 4: INTERVENTION RECEPTIVITY
    # -------------------------------------------------------------------------
    with research_tabs[3]:
        st.markdown("""
        <div class="research-card">
            <span class="research-badge">🔬 Research Feature 4</span>
            <h4>Intervention Receptivity</h4>
            <p>Predicts whether you are likely to engage with a recommended intervention based on your historical 
            response patterns, optimal timing, and current mental state. Addresses the research gap where apps 
            recommend interventions without considering whether the user will actually follow through.</p>
        </div>
        """, unsafe_allow_html=True)

        receptivity = get_all_receptivity_scores(username)

        st.markdown("### 🎯 Your Intervention Receptivity Profile")

        intervention_names = [k.replace("_", " ").title() for k in receptivity.keys()]
        scores = [v["receptivity_score"] * 100 for v in receptivity.values()]
        timings = [v["optimal_timing"] for v in receptivity.values()]

        fig = go.Figure()
        colors = [COLOR_GOOD if s > 60 else (COLOR_MEDIUM if s > 30 else COLOR_HIGH) for s in scores]
        fig.add_trace(go.Bar(
            x=intervention_names, y=scores,
            marker_color=colors,
            text=[f"{s:.0f}%" for s in scores],
            textposition="outside"
        ))
        fig.update_layout(
            title="Likelihood of Engaging with Each Intervention",
            yaxis_title="Receptivity Score (%)",
            height=400,
            yaxis=dict(range=[0, 110])
        )
        st.plotly_chart(style_plot(fig), use_container_width=True)

        st.markdown("### 📋 Detailed Breakdown")
        for intervention, data in receptivity.items():
            with st.expander(f"{intervention.replace('_', ' ').title()} — {data['receptivity_score']*100:.0f}% receptivity"):
                c1, c2 = st.columns(2)
                c1.metric("Historical Response Rate", f"{data['historical_response_rate']*100:.0f}%")
                c1.metric("Optimal Timing", data["optimal_timing"].title())
                c2.metric("Preferred Channel", data["preferred_channel"].replace("_", " ").title())
                c2.caption(data["personalization_notes"])

        st.markdown("### Research Significance")
        st.caption("""
        Digital mental health interventions have high dropout rates because recommendations are often generic. 
        Intervention Receptivity uses your engagement history to predict which interventions you're most likely 
        to follow through on, and when. This personalization addresses a major research gap in digital therapeutics: 
        the "engagement cliff" where users receive recommendations but don't act on them.
        """)

    # -------------------------------------------------------------------------
    # TAB 5: RECOVERY PATTERN ANALYSIS
    # -------------------------------------------------------------------------
    with research_tabs[4]:
        st.markdown("""
        <div class="research-card">
            <span class="research-badge">🔬 Research Feature 5</span>
            <h4>Recovery Pattern Analysis</h4>
            <p>Measures how quickly you return toward your baseline after a mental health dip. Tracks recovery 
            rate, baseline return percentage, and whether interventions speed up your recovery. Most apps only 
            track decline — this tracks your resilience and bounce-back ability.</p>
        </div>
        """, unsafe_allow_html=True)

        recoveries = analyze_recovery_patterns(username)
        stored_recoveries = get_recovery_patterns(username)

        if stored_recoveries:
            st.markdown(f"### 🏥 {len(stored_recoveries)} Recovery Episode(s) Analyzed")

            col1, col2, col3 = st.columns(3)
            avg_duration = np.mean([r["recovery_duration_days"] for r in stored_recoveries if r["recovery_duration_days"]])
            avg_rate = np.mean([r["recovery_rate"] for r in stored_recoveries if r["recovery_rate"]])
            avg_return = np.mean([r["baseline_return_pct"] for r in stored_recoveries if r["baseline_return_pct"]])

            col1.metric("Avg Recovery Time", f"{avg_duration:.1f} days" if avg_duration else "N/A")
            col2.metric("Avg Recovery Rate", f"{avg_rate:.1f} pts/day" if avg_rate else "N/A")
            col3.metric("Baseline Return", f"{avg_return:.0f}%" if avg_return else "N/A")

            fig = create_recovery_chart(stored_recoveries)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Episode Details")
            for i, rec in enumerate(stored_recoveries[:5]):
                with st.expander(f"Episode {i+1}: {rec['episode_date'][:10]} — Severity: {rec['episode_severity']:.0f}/100"):
                    c1, c2 = st.columns(2)
                    c1.metric("Recovery Duration", f"{rec['recovery_duration_days']:.0f} days")
                    c1.metric("Recovery Rate", f"{rec['recovery_rate']:.1f} pts/day")
                    c2.metric("Baseline Return", f"{rec['baseline_return_pct']:.0f}%")
                    c2.metric("Intervention Used", rec["intervention_used"] or "None recorded")

            st.markdown("### Research Significance")
            st.caption("""
            Resilience research shows that recovery speed is a better predictor of long-term mental health than 
            baseline wellness alone. By measuring your personal recovery patterns — how fast you bounce back, 
            what helps, and what doesn't — MindTrack fills a critical gap in self-monitoring tools that focus 
            exclusively on symptoms rather than resilience.
            """)
        else:
            st.info("🏥 No recovery episodes detected yet. Recovery patterns are identified when your wellness score drops below 40 and then returns to baseline. Continue tracking to build your recovery profile.")

    # -------------------------------------------------------------------------
    # TAB 6: INTERVENTION EXPERIMENT
    # -------------------------------------------------------------------------
    with research_tabs[5]:
        st.markdown("""
        <div class="research-card">
            <span class="research-badge">🔬 Research Feature 6</span>
            <h4>Intervention Experiment</h4>
            <p>Measures whether recommendations actually produce improvement using pre/post analysis with 
            effect sizes and statistical significance testing. Unlike apps that assume interventions work, 
            this feature runs controlled "experiments" on your own data to find what actually helps <em>you</em>.</p>
        </div>
        """, unsafe_allow_html=True)

        experiments = get_experiments(username)

        st.markdown("### 🧪 Start a New Experiment")
        with st.form("new_experiment"):
            exp_name = st.text_input("Experiment Name", placeholder="e.g., 'Daily Breathing for 2 Weeks'")
            exp_type = st.selectbox("Intervention Type", [
                "breathing", "journaling", "exercise", "sleep_hygiene", 
                "mindfulness", "social_connection", "professional_help", "other"
            ])
            exp_notes = st.text_area("Notes / Hypothesis", placeholder="What do you expect to happen?")
            submitted = st.form_submit_button("🚀 Start Experiment")
            if submitted and exp_name:
                create_intervention_experiment(
                    username, exp_name, exp_type, 
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), exp_notes
                )
                st.success(f"Experiment '{exp_name}' started! Continue your assessments — the system will track your progress.")
                st.rerun()

        pulse_divider()

        active_exps = get_active_experiments(username)
        if active_exps:
            st.markdown(f"### 🔥 {len(active_exps)} Active Experiment(s)")
            for exp in active_exps:
                with st.container():
                    c1, c2, c3 = st.columns([2, 1.5, 1])
                    c1.markdown(f"**{exp['experiment_name']}**")
                    c1.caption(f"Started: {exp['start_date'][:10]} | Type: {exp['intervention_type']}")
                    c2.caption(f"Pre-score: {exp['pre_score']:.1f}" if exp['pre_score'] else "Collecting baseline...")
                    if c3.button("✅ Complete", key=f"complete_exp_{exp['id']}"):
                        result = complete_intervention_experiment(
                            exp['id'], 
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )
                        if result:
                            st.success(f"""
                            Experiment completed!
                            - Pre-score: {result['pre_score']:.1f}
                            - Post-score: {result['post_score']:.1f}
                            - Improvement: {result['improvement']:+.1f}
                            - Effect size (Cohen's d): {result['effect_size']:.2f}
                            - Statistical significance: {'Yes' if result['is_significant'] else 'No'} (p={result['p_value']:.3f})
                            """)
                        else:
                            st.warning("Not enough data to complete the experiment. Need at least 3 entries before and after the start date.")
                        st.rerun()
                st.markdown("---")

        completed_exps = [e for e in experiments if e["status"] == "completed"]
        if completed_exps:
            st.markdown(f"### 📊 {len(completed_exps)} Completed Experiment(s)")

            fig = create_experiment_results_chart(experiments)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            for exp in completed_exps:
                with st.expander(f"{exp['experiment_name']} — {exp['intervention_type']}"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Pre-Score", f"{exp['pre_score']:.1f}")
                    c1.metric("Post-Score", f"{exp['post_score']:.1f}")
                    c2.metric("Effect Size", f"{exp['effect_size']:.2f}",
                             help="Cohen's d: 0.2=small, 0.5=medium, 0.8=large")
                    sig_color = COLOR_GOOD if exp["is_significant"] else COLOR_HIGH
                    c2.markdown(f"<span style='color:{sig_color};font-weight:700;'>Significant: {'Yes ✅' if exp['is_significant'] else 'No ❌'}</span>", unsafe_allow_html=True)
                    c3.metric("p-value", f"{exp['p_value']:.3f}")
                    c3.metric("Sample Size", exp["sample_size"])
                    if exp["notes"]:
                        st.caption(f"Notes: {exp['notes']}")

        st.markdown("### Research Significance")
        st.caption("""
        Most mental health apps recommend interventions based on population studies — what works "on average." 
        But what works for the average person may not work for you. The Intervention Experiment feature treats 
        your own life as a natural experiment: it compares your wellness scores before and after you try an 
        intervention, calculates effect sizes, and tests for statistical significance. This is the gold standard 
        for evidence-based self-improvement, adapted for personal use.
        """)

# End of app
