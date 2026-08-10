import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import random
import sqlite3
import json
from datetime import datetime, timedelta
from textblob import TextBlob
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors as rl_colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import io

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
:root {{ --ink: {COLOR_INK}; --muted: {COLOR_MUTED}; --paper: {COLOR_BG}; --card: {COLOR_CARD}; --border: {COLOR_BORDER}; --primary: {COLOR_PRIMARY}; --primary-light: {COLOR_PRIMARY_LIGHT}; --good: {COLOR_GOOD}; --medium: {COLOR_MEDIUM}; --high: {COLOR_HIGH}; }}
html, body, [class*="css"] {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}
.stApp {{ background: var(--paper); }}
.main .block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1200px; }}
h1, h2, h3 {{ font-family: 'Fraunces', Georgia, serif !important; color: var(--ink) !important; font-weight: 600 !important; letter-spacing: -0.01em; }}
.stMarkdown, .stMarkdown p, label, .stText, .stCaption {{ color: var(--muted) !important; }}
[data-testid="stSidebar"] {{ background: var(--ink); border-right: 1px solid rgba(255,255,255,0.06); }}
[data-testid="stSidebar"] * {{ color: #EDEFEE !important; }}
.sidebar-brand {{ font-family: 'Fraunces', serif; font-size: 1.55rem; font-weight: 700; color: #fff !important; margin: 0.2rem 0 0.1rem 0; display: flex; align-items: center; gap: 8px; }}
.sidebar-tagline {{ font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--primary-light) !important; margin-bottom: 1.5rem; }}
[data-testid="stSidebar"] div[role="radiogroup"] label {{ background: rgba(255,255,255,0.035); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 9px 14px; margin-bottom: 6px; transition: all 0.15s ease; }}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{ background: rgba(255,255,255,0.09); border-color: var(--primary-light); }}
.sidebar-disclaimer {{ font-size: 0.68rem !important; color: rgba(237,239,238,0.55) !important; margin-top: 16px; line-height: 1.45; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.08); }}
.page-header {{ display: flex; align-items: flex-start; gap: 16px; margin-bottom: 0.2rem; }}
.page-header-icon {{ font-size: 2.2rem; line-height: 1; margin-top: 2px; }}
.page-eyebrow {{ font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--primary); font-weight: 600; margin-bottom: 2px; }}
.page-title {{ margin: 0 !important; font-size: 2.05rem !important; }}
.page-subtitle {{ color: var(--muted) !important; font-size: 1rem; margin-top: 4px !important; }}
.pulse-divider {{ color: var(--primary); opacity: 0.55; height: 18px; margin: 1.2rem 0 1.6rem 0; }}
.pulse-divider svg {{ width: 100%; height: 100%; display: block; }}
.hero-wrap {{ text-align: center; padding: 2.6rem 0 1.6rem 0; }}
.hero-icon {{ font-size: 3.2rem; }}
.hero-title {{ font-family: 'Fraunces', serif; font-size: 2.6rem; margin: 0.25rem 0 0.35rem 0; color: var(--ink); font-weight: 700; }}
.hero-tagline {{ font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.10em; text-transform: uppercase; font-size: 0.82rem; color: var(--primary); font-weight: 600; }}
[data-testid="stMetric"] {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; box-shadow: 0 1px 3px rgba(27,36,48,0.05); }}
[data-testid="stMetricLabel"] {{ font-family: 'IBM Plex Mono', monospace !important; text-transform: uppercase; font-size: 0.70rem !important; letter-spacing: 0.06em; color: var(--muted) !important; }}
[data-testid="stMetricValue"] {{ font-family: 'Fraunces', serif !important; color: var(--ink) !important; }}
.feature-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 22px; box-shadow: 0 1px 3px rgba(27,36,48,0.05); }}
.stButton > button {{ background: var(--primary); color: #fff; border: none; border-radius: 8px; padding: 11px 22px; font-weight: 600; font-family: 'Inter', sans-serif; box-shadow: 0 1px 2px rgba(27,36,48,0.12); transition: all 0.15s ease; }}
.stButton > button:hover {{ background: var(--primary-light); transform: translateY(-1px); box-shadow: 0 4px 10px rgba(47,111,98,0.25); }}
.stDownloadButton > button {{ background: #fff; color: var(--primary); border: 1.5px solid var(--primary); border-radius: 8px; font-weight: 600; }}
.stDownloadButton > button:hover {{ background: var(--primary); color: #fff; }}
div[data-testid="stAlert"] {{ border-radius: 10px; border: 1px solid var(--border); }}
button[data-baseweb="tab"] {{ font-family: 'Inter', sans-serif; font-weight: 600; color: var(--muted); }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: var(--primary); }}
[data-testid="stSlider"] [role="slider"] {{ background-color: var(--primary) !important; }}
hr {{ display: none; }}
.streak-badge {{ display: inline-flex; align-items: center; gap: 6px; background: rgba(217,164,65,0.12); border: 1px solid rgba(217,164,65,0.35); color: var(--medium) !important; border-radius: 999px; padding: 4px 14px; font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem; font-weight: 600; }}
.breathing-circle-wrap {{ display: flex; justify-content: center; padding: 1.8rem 0; }}
.breathing-circle {{ width: 140px; height: 140px; border-radius: 50%; background: radial-gradient(circle, var(--primary-light), var(--primary)); animation: breathe 16s ease-in-out infinite; box-shadow: 0 0 40px rgba(47,111,98,0.35); }}
@keyframes breathe {{ 0% {{ transform: scale(0.7); opacity: 0.8; }} 25% {{ transform: scale(1.15); opacity: 1; }} 50% {{ transform: scale(1.15); opacity: 1; }} 75% {{ transform: scale(0.7); opacity: 0.8; }} 100% {{ transform: scale(0.7); opacity: 0.8; }} }}
.entry-row {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 10px 16px; margin-bottom: 8px; }}
.login-box {{ max-width: 400px; margin: 2rem auto; padding: 2rem; background: #fff; border: 1px solid rgba(27,36,48,0.10); border-radius: 14px; text-align: center; }}
.login-icon {{ font-size: 3rem; margin-bottom: 0.5rem; }}
.login-title {{ font-family: 'Fraunces', serif; font-size: 1.6rem; color: var(--ink); margin-bottom: 0.3rem; }}
.login-sub {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 1.5rem; }}
.user-pill {{ display: inline-flex; align-items: center; gap: 6px; background: rgba(47,111,98,0.10); border: 1px solid rgba(47,111,98,0.25); color: var(--primary); border-radius: 999px; padding: 5px 14px; font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; font-weight: 600; }}
.lock-screen {{ text-align: center; padding: 3rem 1rem; }}
.lock-screen h2 {{ font-family: 'Fraunces', serif; color: var(--ink); }}
.crisis-banner {{ background: linear-gradient(135deg, {COLOR_HIGH}22, {COLOR_HIGH}11); border: 2px solid {COLOR_HIGH}; border-radius: 12px; padding: 20px; margin: 16px 0; text-align: center; }}
.companion-card {{ background: linear-gradient(135deg, {COLOR_PRIMARY}15, {COLOR_PRIMARY_LIGHT}10); border: 1px solid {COLOR_PRIMARY}40; border-radius: 16px; padding: 24px; margin: 20px 0; }}
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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS user_history (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, date TEXT, mood TEXT, sleep_hours REAL, stress_level REAL, anxiety_level REAL, exercise_minutes REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS predictions (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, date TEXT, risk_level TEXT, wellness_score REAL, factors TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS goals (username TEXT PRIMARY KEY, target_sleep REAL, target_exercise REAL, target_stress_max REAL, updated_at TEXT)")
    # NEW TABLES
    cur.execute("CREATE TABLE IF NOT EXISTS crisis_plan (username TEXT PRIMARY KEY, warning_signs TEXT, coping_strategies TEXT, distraction_places TEXT, support_contacts TEXT, professional_contacts TEXT, means_safety TEXT, reasons_for_living TEXT, updated_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS ema_surveys (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, timestamp TEXT, mood INTEGER, context TEXT, energy INTEGER, social_connection INTEGER, location_type TEXT, triggered_by TEXT, notes TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS micro_checkins (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, timestamp TEXT, emoji TEXT, energy_level INTEGER, stress_level INTEGER, took_meds INTEGER, sleep_quality INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS cultural_profile (username TEXT PRIMARY KEY, country_code TEXT, primary_language TEXT, cultural_values TEXT, stress_expression_style TEXT, family_structure TEXT, religious_spiritual TEXT, accessibility_needs TEXT, trauma_history_disclosed INTEGER, updated_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS clinician_links (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_username TEXT, clinician_code TEXT, consent_given INTEGER DEFAULT 0, share_level TEXT DEFAULT 'summary', linked_at TEXT, last_sync TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS ai_companion (username TEXT PRIMARY KEY, companion_name TEXT DEFAULT 'Companion', personality_tone TEXT DEFAULT 'warm', memory_notes TEXT, empathy_level INTEGER DEFAULT 5, created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS model_audit (id INTEGER PRIMARY KEY AUTOINCREMENT, prediction_id INTEGER, model_version TEXT, feature_weights TEXT, confidence_lower REAL, confidence_upper REAL, bias_flags TEXT, audited_at TEXT)")
    conn.commit()
    conn.close()

# ============================================================================
# FEATURE 1: PROACTIVE CRISIS ESCALATION ENGINE
# ============================================================================

CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end it all", "no point living", "want to die",
    "self-harm", "cutting", "hurt myself", "overdose", "not worth living",
    "hopeless", "can't go on", "give up", "better off dead", "nobody cares"
]

CRISIS_RESOURCES = {
    "US": {"name": "988 Suicide & Crisis Lifeline", "number": "988", "text": "988"},
    "UK": {"name": "Samaritans", "number": "116 123", "text": None},
    "CA": {"name": "Crisis Services Canada", "number": "1-833-456-4566", "text": "45645"},
    "AU": {"name": "Lifeline Australia", "number": "13 11 14", "text": "0477 13 11 14"},
    "IN": {"name": "iCall (TISS)", "number": "9152987821", "text": None},
    "DE": {"name": "Telefonseelsorge", "number": "0800 1110111", "text": None},
    "FR": {"name": "SOS Amitie", "number": "09 72 39 40 50", "text": None},
    "DEFAULT": {"name": "Find local resources", "number": "", "text": None},
}


def detect_crisis_signals(username):
    signals = []
    severity = 0
    df = get_history_data()
    mine = df[df["username"].astype(str) == username].sort_values("date") if not df.empty else df
    if not mine.empty and len(mine) >= 3:
        recent = mine.tail(3)["wellness_score"].tolist()
        if recent[0] > recent[1] > recent[2] and recent[2] < 40:
            signals.append("Wellness declining 3 entries in a row below 40")
            severity += 3
    jdf = get_journal_entries(username)
    if not jdf.empty:
        latest = jdf.iloc[0]
        if latest["polarity"] < -0.5:
            signals.append(f"Recent journal sentiment very negative ({latest['polarity']:.2f})")
            severity += 2
        text_lower = str(latest["text"]).lower()
        found_keywords = [kw for kw in CRISIS_KEYWORDS if kw in text_lower]
        if found_keywords:
            signals.append(f"Crisis keywords detected: {', '.join(found_keywords[:3])}")
            severity += 4
    conn = get_connection()
    ema = pd.read_sql_query("SELECT * FROM ema_surveys WHERE username=? ORDER BY timestamp DESC LIMIT 3", conn, params=(username,))
    conn.close()
    if not ema.empty:
        avg_mood = ema["mood"].mean()
        if avg_mood < 3:
            signals.append(f"Recent EMA mood very low (avg: {avg_mood:.1f}/10)")
            severity += 2
    is_crisis = severity >= 4
    return is_crisis, signals, severity


def save_crisis_plan(username, warning_signs, coping_strategies, distraction_places, support_contacts_json, professional_contacts, means_safety, reasons_for_living):
    conn = get_connection()
    conn.execute("INSERT INTO crisis_plan (username, warning_signs, coping_strategies, distraction_places, support_contacts, professional_contacts, means_safety, reasons_for_living, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(username) DO UPDATE SET warning_signs=excluded.warning_signs, coping_strategies=excluded.coping_strategies, distraction_places=excluded.distraction_places, support_contacts=excluded.support_contacts, professional_contacts=excluded.professional_contacts, means_safety=excluded.means_safety, reasons_for_living=excluded.reasons_for_living, updated_at=excluded.updated_at", (username, warning_signs, coping_strategies, distraction_places, support_contacts_json, professional_contacts, means_safety, reasons_for_living, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def get_crisis_plan(username):
    conn = get_connection()
    row = conn.execute("SELECT * FROM crisis_plan WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_localized_crisis_resource(country_code="US"):
    return CRISIS_RESOURCES.get(country_code, CRISIS_RESOURCES["DEFAULT"])


# ============================================================================
# FEATURE 2: DIGITAL PHENOTYPING SIMULATOR
# ============================================================================

def calculate_sleep_consistency(sleep_hours_list):
    if len(sleep_hours_list) < 3:
        return 50
    std_dev = np.std(sleep_hours_list)
    consistency = max(0, 100 - (std_dev * 20))
    return round(consistency, 1)


def calculate_social_rhythm_index(df):
    if len(df) < 7:
        return 50
    sleep_diff = df["sleep_hours"].diff().abs().mean()
    exercise_diff = df["exercise_minutes"].diff().abs().mean()
    srm = max(0, 100 - (sleep_diff * 10 + exercise_diff * 0.5))
    return round(srm, 1)


def calculate_circadian_alignment(df):
    if df.empty or "date" not in df.columns:
        return 50
    df = df.copy()
    df["hour"] = df["date"].dt.hour
    hour_std = df["hour"].std()
    alignment = max(0, 100 - (hour_std * 8))
    return round(alignment, 1)


def get_digital_phenotype(username):
    df = get_history_data()
    mine = df[df["username"].astype(str) == username].sort_values("date") if not df.empty else df
    if mine.empty:
        return None
    sleep_list = mine["sleep_hours"].tolist()
    phenotype = {
        "sleep_consistency": calculate_sleep_consistency(sleep_list),
        "social_rhythm_index": calculate_social_rhythm_index(mine),
        "circadian_alignment": calculate_circadian_alignment(mine),
        "avg_sleep": mine["sleep_hours"].mean(),
        "sleep_variability": mine["sleep_hours"].std(),
        "activity_level": mine["exercise_minutes"].mean(),
        "stress_trend": "increasing" if len(mine) > 3 and mine.tail(3)["stress_level"].is_monotonic_increasing else "stable",
        "mood_volatility": mine["mood_num"].std() if "mood_num" in mine.columns else None,
        "assessment_count": len(mine),
        "days_span": (mine["date"].max() - mine["date"].min()).days if len(mine) > 1 else 0,
    }
    return phenotype


# ============================================================================
# FEATURE 3: EXPLAINABLE AI RISK MODEL
# ============================================================================

def explainable_risk_prediction(stress, sleep, anxiety, exercise, mood):
    contributions = {}
    stress_contrib = (10 - stress) * 5
    contributions["Stress Management"] = {"value": stress, "max": 10, "points": stress_contrib, "max_possible": 50, "explanation": f"Stress level {stress}/10 -> {stress_contrib}/50 points"}
    sleep_contrib = min(sleep, 10) * 3
    contributions["Sleep Quality"] = {"value": sleep, "max": 10, "points": sleep_contrib, "max_possible": 30, "explanation": f"Sleep {sleep}h -> {sleep_contrib}/30 points"}
    anxiety_contrib = (10 - anxiety) * 5
    contributions["Anxiety Regulation"] = {"value": anxiety, "max": 10, "points": anxiety_contrib, "max_possible": 50, "explanation": f"Anxiety {anxiety}/10 -> {anxiety_contrib}/50 points"}
    exercise_contrib = min(exercise, 120) / 2
    contributions["Physical Activity"] = {"value": exercise, "max": 120, "points": exercise_contrib, "max_possible": 60, "explanation": f"Exercise {exercise}min -> {exercise_contrib:.1f}/60 points"}
    mood_scale = {"Very Bad": 1, "Bad": 2, "Neutral": 3, "Good": 4, "Very Good": 5}
    mood_val = mood_scale.get(mood, 3)
    mood_contrib = mood_val * 4
    contributions["Mood State"] = {"value": mood, "max": 5, "points": mood_contrib, "max_possible": 20, "explanation": f"Mood: {mood} -> {mood_contrib}/20 points"}
    total_score = sum(c["points"] for c in contributions.values())
    wellness_score = min(total_score, 100)
    if wellness_score < 40:
        risk = "High"
        confidence = 0.85 if stress > 7 or anxiety > 7 else 0.70
    elif wellness_score < 70:
        risk = "Medium"
        confidence = 0.75
    else:
        risk = "Low"
        confidence = 0.80 if sleep >= 7 and exercise >= 30 else 0.65
    counterfactuals = []
    if sleep < 7:
        improved_sleep = min(sleep + 2, 10)
        new_score = min(total_score + (improved_sleep - sleep) * 3, 100)
        counterfactuals.append(f"If you slept {improved_sleep:.0f}h instead of {sleep:.0f}h, score would be {new_score:.0f}/100 (+{new_score-wellness_score:.0f})")
    if exercise < 30:
        improved_exercise = min(exercise + 15, 120)
        new_score = min(total_score + (improved_exercise - exercise) / 2, 100)
        counterfactuals.append(f"If you exercised {improved_exercise:.0f}min instead of {exercise:.0f}min, score would be {new_score:.0f}/100 (+{new_score-wellness_score:.0f})")
    if stress > 5:
        reduced_stress = max(stress - 2, 0)
        new_score = min(total_score + (stress - reduced_stress) * 5, 100)
        counterfactuals.append(f"If stress dropped to {reduced_stress:.0f}/10, score would be {new_score:.0f}/100 (+{new_score-wellness_score:.0f})")
    return {"wellness_score": wellness_score, "risk_level": risk, "confidence": confidence, "confidence_interval": (max(0, wellness_score - 15), min(100, wellness_score + 15)), "contributions": contributions, "counterfactuals": counterfactuals, "model_version": "MindTrack-v2.1-explainable", "top_driver": max(contributions.items(), key=lambda x: x[1]["max_possible"] - x[1]["points"])[0]}


def create_explanation_chart(contributions):
    categories = list(contributions.keys())
    points = [contributions[c]["points"] for c in categories]
    max_points = [contributions[c]["max_possible"] for c in categories]
    gaps = [max_points[i] - points[i] for i in range(len(categories))]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Earned Points", x=categories, y=points, marker_color=COLOR_PRIMARY, width=0.6))
    fig.add_trace(go.Bar(name="Potential Gap", x=categories, y=gaps, marker_color="rgba(193,85,74,0.3)", width=0.6, base=points))
    fig.update_layout(title="Score Breakdown: What You Earned vs. What's Possible", barmode="stack", yaxis_title="Points", showlegend=True)
    return style_plot(fig)


# ============================================================================
# FEATURE 4: CLINICIAN PORTAL
# ============================================================================

def link_clinician(patient_username, clinician_code, share_level="summary"):
    conn = get_connection()
    conn.execute("INSERT INTO clinician_links (patient_username, clinician_code, share_level, linked_at) VALUES (?, ?, ?, ?)", (patient_username, clinician_code, share_level, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def get_clinician_patients(clinician_code):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM clinician_links WHERE clinician_code=? AND consent_given=1", (clinician_code,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_patient_summary_for_clinician(patient_username, share_level="summary"):
    df = get_history_data()
    mine = df[df["username"].astype(str) == patient_username].sort_values("date") if not df.empty else df
    if mine.empty:
        return None
    summary = {"patient": patient_username, "total_entries": len(mine), "date_range": f"{mine['date'].min().strftime('%Y-%m-%d')} to {mine['date'].max().strftime('%Y-%m-%d')}", "current_risk": mine.iloc[-1].get("wellness_score", 50), "risk_trend": "improving" if len(mine) > 3 and mine.tail(3)["wellness_score"].is_monotonic_increasing else "stable/declining", "avg_wellness": mine["wellness_score"].mean(), "sleep_avg": mine["sleep_hours"].mean(), "stress_avg": mine["stress_level"].mean(), "anxiety_avg": mine["anxiety_level"].mean(), "exercise_avg": mine["exercise_minutes"].mean(), "mood_distribution": mine["mood"].value_counts().to_dict(), "alerts": []}
    if mine.iloc[-1]["wellness_score"] < 40:
        summary["alerts"].append("HIGH RISK: Latest wellness score below 40")
    if mine["stress_level"].tail(7).mean() > 7:
        summary["alerts"].append("Elevated stress trend over past week")
    if trend_nudge(mine):
        summary["alerts"].append("Declining wellness trend over last 3 entries")
    jdf = get_journal_entries(patient_username)
    if not jdf.empty:
        summary["journal_sentiment_trend"] = jdf.head(5)["polarity"].mean()
        if summary["journal_sentiment_trend"] < -0.3:
            summary["alerts"].append("Negative journal sentiment trend")
    return summary


# ============================================================================
# FEATURE 5: CULTURAL & EQUITY ADAPTATION
# ============================================================================

def save_cultural_profile(username, country_code, primary_language, cultural_values, stress_expression_style, family_structure, religious_spiritual, accessibility_needs, trauma_history_disclosed=0):
    conn = get_connection()
    conn.execute("INSERT INTO cultural_profile (username, country_code, primary_language, cultural_values, stress_expression_style, family_structure, religious_spiritual, accessibility_needs, trauma_history_disclosed, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(username) DO UPDATE SET country_code=excluded.country_code, primary_language=excluded.primary_language, cultural_values=excluded.cultural_values, stress_expression_style=excluded.stress_expression_style, family_structure=excluded.family_structure, religious_spiritual=excluded.religious_spiritual, accessibility_needs=excluded.accessibility_needs, trauma_history_disclosed=excluded.trauma_history_disclosed, updated_at=excluded.updated_at", (username, country_code, primary_language, cultural_values, stress_expression_style, family_structure, religious_spiritual, accessibility_needs, trauma_history_disclosed, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def get_cultural_profile(username):
    conn = get_connection()
    row = conn.execute("SELECT * FROM cultural_profile WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def culturally_adjusted_sentiment(text, stress_expression_style="direct"):
    sentiment, polarity = analyze_sentiment(text)
    if stress_expression_style in ["indirect", "somatic", "behavioral"]:
        somatic_keywords = ["tired", "headache", "pain", "sick", "body", "stomach", "chest", "dizzy", "weak", "exhausted", "can't sleep"]
        text_lower = text.lower()
        somatic_count = sum(1 for kw in somatic_keywords if kw in text_lower)
        if somatic_count >= 2 and polarity > -0.1:
            polarity = max(-0.3, polarity - 0.3)
            sentiment = "negative" if polarity < -0.1 else sentiment
    return sentiment, polarity


# ============================================================================
# FEATURE 6: ADAPTIVE ENGAGEMENT + MICRO-CHECKINS
# ============================================================================

def save_micro_checkin(username, emoji, energy_level, stress_level, took_meds=None, sleep_quality=None):
    conn = get_connection()
    conn.execute("INSERT INTO micro_checkins (username, timestamp, emoji, energy_level, stress_level, took_meds, sleep_quality) VALUES (?, ?, ?, ?, ?, ?, ?)", (username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), emoji, energy_level, stress_level, took_meds, sleep_quality))
    conn.commit()
    conn.close()


def get_micro_checkins(username, days=7):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM micro_checkins WHERE username=? AND timestamp >= date('now', '-{} days') ORDER BY timestamp DESC".format(days), conn, params=(username,))
    conn.close()
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def get_optimal_checkin_time(username):
    df = get_history_data()
    mine = df[df["username"].astype(str) == username] if not df.empty else df
    if mine.empty or len(mine) < 3:
        return 9
    mine = mine.copy()
    mine["hour"] = mine["date"].dt.hour
    optimal_hour = mine["hour"].mode().iloc[0] if not mine["hour"].mode().empty else 9
    return int(optimal_hour)


def generate_progress_narrative(username):
    df = get_history_data()
    mine = df[df["username"].astype(str) == username].sort_values("date") if not df.empty else df
    if mine.empty or len(mine) < 2:
        return "Start tracking to see your wellness story unfold."
    narratives = []
    recent_sleep = mine.tail(7)["sleep_hours"].mean()
    older_sleep = mine.head(min(7, len(mine)))["sleep_hours"].mean()
    sleep_change = ((recent_sleep - older_sleep) / older_sleep * 100) if older_sleep > 0 else 0
    if abs(sleep_change) > 10:
        direction = "improved" if sleep_change > 0 else "declined"
        narratives.append(f"Your sleep has {direction} by {abs(sleep_change):.0f}% recently. {'Good work!' if sleep_change > 0 else 'This might be worth attention.'}")
    recent_stress = mine.tail(7)["stress_level"].mean()
    if recent_stress < 4:
        narratives.append("Your stress levels have been manageable lately — that's a strong foundation.")
    elif recent_stress > 7:
        narratives.append("You've been carrying high stress. Consider the coping tools in the Support section.")
    dates_only = mine["date"].dt.date.tolist()
    streak_current, streak_longest = calculate_streaks(dates_only)
    if streak_current >= 3:
        narratives.append(f"You're on a {streak_current}-day check-in streak. Consistency builds insight.")
    recent_moods = mine.tail(7)["mood"].value_counts()
    if "Good" in recent_moods.index or "Very Good" in recent_moods.index:
        good_count = recent_moods.get("Good", 0) + recent_moods.get("Very Good", 0)
        narratives.append(f"{good_count} of your last 7 check-ins were positive. That's meaningful.")
    return " ".join(narratives) if narratives else "Keep checking in — your story is building."


# ============================================================================
# FEATURE 7: ECOLOGICAL MOMENTARY ASSESSMENT (EMA)
# ============================================================================

def save_ema_survey(username, mood, context, energy, social_connection, location_type="", triggered_by="", notes=""):
    conn = get_connection()
    conn.execute("INSERT INTO ema_surveys (username, timestamp, mood, context, energy, social_connection, location_type, triggered_by, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mood, context, energy, social_connection, location_type, triggered_by, notes))
    conn.commit()
    conn.close()


def get_ema_surveys(username, days=14):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM ema_surveys WHERE username=? AND timestamp >= date('now', '-{} days') ORDER BY timestamp".format(days), conn, params=(username,))
    conn.close()
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def analyze_ema_patterns(username):
    df = get_ema_surveys(username, days=30)
    if df.empty or len(df) < 5:
        return None
    patterns = {}
    context_mood = df.groupby("context")["mood"].mean().sort_values()
    if not context_mood.empty:
        worst_context = context_mood.index[0]
        best_context = context_mood.index[-1]
        patterns["context_insight"] = f"Mood tends to be lowest during: {worst_context} (avg: {context_mood.iloc[0]:.1f}/10)"
        patterns["best_context"] = f"Mood tends to be highest during: {best_context} (avg: {context_mood.iloc[-1]:.1f}/10)"
    df["hour"] = df["timestamp"].dt.hour
    time_mood = df.groupby(pd.cut(df["hour"], bins=[0, 6, 12, 18, 24], labels=["Night", "Morning", "Afternoon", "Evening"]))["mood"].mean()
    if not time_mood.empty:
        patterns["time_insight"] = f"Mood by time: {time_mood.to_dict()}"
    corr = df["social_connection"].corr(df["mood"])
    if not pd.isna(corr):
        patterns["social_insight"] = f"Social connection and mood correlation: {corr:.2f} ({'strong' if abs(corr) > 0.5 else 'moderate' if abs(corr) > 0.3 else 'weak'})"
    return patterns


# ============================================================================
# FEATURE 8: AI COMPANION / THERAPEUTIC ALLIANCE
# ============================================================================

def initialize_companion(username):
    conn = get_connection()
    conn.execute("INSERT INTO ai_companion (username, companion_name, personality_tone, created_at) VALUES (?, 'Companion', 'warm', ?) ON CONFLICT(username) DO NOTHING", (username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def get_companion(username):
    conn = get_connection()
    row = conn.execute("SELECT * FROM ai_companion WHERE username=?", (username,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    initialize_companion(username)
    return get_companion(username)


def update_companion(username, companion_name=None, personality_tone=None, empathy_level=None):
    conn = get_connection()
    if companion_name:
        conn.execute("UPDATE ai_companion SET companion_name=? WHERE username=?", (companion_name, username))
    if personality_tone:
        conn.execute("UPDATE ai_companion SET personality_tone=? WHERE username=?", (personality_tone, username))
    if empathy_level:
        conn.execute("UPDATE ai_companion SET empathy_level=? WHERE username=?", (empathy_level, username))
    conn.commit()
    conn.close()


def get_companion_message(companion, user_state="neutral"):
    name = companion.get("companion_name", "Companion")
    messages = {
        "distressed": [f"{name} here. I can see things feel heavy right now. That's valid, and you don't have to carry it alone.", f"Hey, it's {name}. I'm holding space for you right now. Breathe with me when you're ready.", f"{name} noticed you've been struggling. Would it help to try a grounding exercise together?"],
        "neutral": [f"Good to see you, friend. {name} is here to support your journey today.", f"{name} here — ready when you are. No pressure, just presence.", f"Welcome back. {name} has been thinking about how to make today a little easier for you."],
        "improving": [f"{name} sees your progress, and it's real. Keep going — you're building something meaningful.", f"Hey there! {name} noticed you've been doing the work. That matters.", f"{name} is proud of the steps you're taking. Wellness is a practice, and you're practicing."],
        "crisis": [f"{name} is really concerned about you right now. Your safety matters more than anything. Please reach out to someone who can help — I've put your safety plan right here for you.", f"This is {name}, and I need you to know: you matter. Please use the crisis resources I've gathered for you. You don't have to go through this alone."]
    }
    return random.choice(messages.get(user_state, messages["neutral"]))


def determine_user_state(username):
    df = get_history_data()
    mine = df[df["username"].astype(str) == username].sort_values("date") if not df.empty else df
    if mine.empty:
        return "neutral"
    latest = mine.iloc[-1]
    is_crisis, _, _ = detect_crisis_signals(username)
    if is_crisis:
        return "crisis"
    if latest["wellness_score"] < 40 or latest["stress_level"] > 8:
        return "distressed"
    if len(mine) >= 3:
        recent = mine.tail(3)["wellness_score"].tolist()
        if recent[0] < recent[1] < recent[2] and recent[2] > 60:
            return "improving"
    return "neutral"

# ============================================================================
# ORIGINAL FUNCTIONS (preserved)
# ============================================================================

def save_user_history(username, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes, entry_date=None):
    init_db()
    if entry_date is None:
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        date_str = datetime.combine(entry_date, datetime.now().time()).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    conn.execute("INSERT INTO user_history (username, date, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes) VALUES (?, ?, ?, ?, ?, ?, ?)", (username, date_str, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes))
    conn.commit()
    conn.close()


def save_prediction(username, risk_level, wellness_score, factors):
    init_db()
    conn = get_connection()
    conn.execute("INSERT INTO predictions (username, date, risk_level, wellness_score, factors) VALUES (?, ?, ?, ?, ?)", (username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), risk_level, wellness_score, str(factors)))
    conn.commit()
    conn.close()


def save_goals(username, target_sleep, target_exercise, target_stress_max):
    init_db()
    conn = get_connection()
    conn.execute("INSERT INTO goals (username, target_sleep, target_exercise, target_stress_max, updated_at) VALUES (?, ?, ?, ?, ?) ON CONFLICT(username) DO UPDATE SET target_sleep=excluded.target_sleep, target_exercise=excluded.target_exercise, target_stress_max=excluded.target_stress_max, updated_at=excluded.updated_at", (username, target_sleep, target_exercise, target_stress_max, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def get_goals(username):
    init_db()
    conn = get_connection()
    row = conn.execute("SELECT * FROM goals WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


JOURNAL_CSV = os.path.join(DATA_DIR, "journal_entries.csv")


def save_journal_entry(username, text, sentiment, polarity):
    os.makedirs(DATA_DIR, exist_ok=True)
    entry = {"id": datetime.now().strftime("%Y%m%d%H%M%S%f"), "username": username, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "text": text, "sentiment": sentiment, "polarity": round(polarity, 4)}
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
        st.markdown("<div class='lock-screen'><div style='font-size: 3rem; margin-bottom: 1rem;'>🔒</div><h2>Please Sign In</h2><p>You need to sign in to access this page.</p><p>Go to <b>🏠 Home</b> to sign in.</p></div>", unsafe_allow_html=True)
        st.stop()


def show_login_page():
    init_login_state()
    st.markdown("<div class='login-box'><div class='login-icon'>🧠</div><div class='login-title'>MindTrack</div><div class='login-sub'>Sign in to access your wellness dashboard</div></div>", unsafe_allow_html=True)
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
        st.sidebar.markdown(f"<div style='margin-bottom: 10px;'><span class='user-pill'>👤 {st.session_state.current_user}</span></div>", unsafe_allow_html=True)
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
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=6, alignment=1, textColor=brand_color)
    story.append(Paragraph("MindTrack Wellness Report", title_style))
    eyebrow_style = ParagraphStyle('Eyebrow', parent=styles['Normal'], fontSize=10, alignment=1, textColor=rl_colors.HexColor(COLOR_MUTED), spaceAfter=24)
    story.append(Paragraph("MENTAL HEALTH RISK ANALYSIS", eyebrow_style))
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Heading2'], fontSize=14, spaceAfter=16, textColor=ink_color)
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
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=rl_colors.HexColor(COLOR_MUTED))
    story.append(Paragraph("This report is a self-reflection summary, not a clinical diagnosis. If you are struggling, please consider speaking with a licensed professional.", footer_style))
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
    df["wellness_score"] = df.apply(lambda row: calculate_wellness_score(row["stress_level"], row["sleep_hours"], row["anxiety_level"], row["exercise_minutes"]), axis=1)
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
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(27,36,48,0.02)", font={"color": COLOR_INK, "family": "Inter, sans-serif"}, title_font={"family": "Fraunces, serif", "color": COLOR_INK, "size": 17}, margin=dict(l=20, r=20, t=50, b=20), legend={"font": {"color": COLOR_MUTED}})
    fig.update_xaxes(gridcolor="rgba(27,36,48,0.07)", color=COLOR_MUTED)
    fig.update_yaxes(gridcolor="rgba(27,36,48,0.07)", color=COLOR_MUTED)
    return fig


def create_wellness_radar(sleep, stress, anxiety, exercise, mood):
    mood_scale = {"Very Bad": 2, "Bad": 4, "Neutral": 6, "Good": 8, "Very Good": 10}
    categories = ["Sleep", "Exercise", "Mood", "Stress Balance", "Anxiety Balance"]
    values = [min(float(sleep), 10), min(float(exercise) / 12, 10), mood_scale.get(mood, 6), 10 - float(stress), 10 - float(anxiety)]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill="toself", name="Wellness Profile", line_color=COLOR_PRIMARY, fillcolor="rgba(47,111,98,0.20)"))
    fig.update_layout(title="Wellness Profile", polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(color=COLOR_MUTED)), angularaxis=dict(tickfont=dict(color=COLOR_INK))), showlegend=False)
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
        steps = [{'range': [lo, lo + span * 0.4], 'color': COLOR_HIGH}, {'range': [lo + span * 0.4, lo + span * 0.7], 'color': COLOR_MEDIUM}, {'range': [lo + span * 0.7, hi], 'color': COLOR_GOOD}]
    fig = go.Figure(go.Indicator(mode="gauge+number", value=value, domain={'x': [0, 1], 'y': [0, 1]}, title={'text': title, 'font': {'size': 20, 'color': COLOR_INK, 'family': 'Fraunces, serif'}}, number={'font': {'color': COLOR_INK, 'family': 'IBM Plex Mono, monospace'}}, gauge={'axis': {'range': list(value_range), 'tickwidth': 1, 'tickcolor': COLOR_MUTED}, 'bar': {'color': COLOR_PRIMARY}, 'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 1, 'bordercolor': COLOR_BORDER, 'steps': steps}))
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
    fig = go.Figure(data=go.Heatmap(z=matrix, x=[f"W{i + 1}" for i in range(weeks)], y=weekday_labels, colorscale=[[0, COLOR_HIGH], [0.5, COLOR_MEDIUM], [1, COLOR_GOOD]], zmin=1, zmax=5, hoverinfo="text", text=hovertext, xgap=3, ygap=3, showscale=False))
    fig.update_layout(title=f"Mood Calendar — Last {weeks} Weeks")
    return style_plot(fig)

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

PAGES = [
    "🏠 Home", "📋 Assessment", "🤖 Risk Prediction", "🎯 Goals",
    "📂 Bulk Upload", "📈 Dashboard", "📝 Journal", "📓 My Journals", "🗂️ My Entries",
    "🆘 Support & Coping", "📄 Report", "📊 Admin",
    # NEW PAGES
    "🛡️ Crisis Plan", "🔬 Digital Phenotype", "🧠 Explainable AI",
    "👨‍⚕️ Clinician Portal", "🌍 Cultural Profile", "⚡ Quick Check-in",
    "📍 EMA Survey", "🤖 My Companion"
]

st.sidebar.markdown("<div class='sidebar-brand'>🧠 MindTrack</div><div class='sidebar-tagline'>Wellness Intelligence</div>", unsafe_allow_html=True)

if 'nav_to' in st.session_state:
    _nav_map = {'assessment': "📋 Assessment", 'journal': "📝 Journal", 'support': "🆘 Support & Coping", 'goals': "🎯 Goals"}
    if st.session_state['nav_to'] in _nav_map:
        st.session_state['page_radio'] = _nav_map[st.session_state['nav_to']]
    del st.session_state['nav_to']

page = st.sidebar.radio("Go to", PAGES, key="page_radio", label_visibility="collapsed")

show_user_badge()

st.sidebar.markdown("<div class='sidebar-disclaimer'>MindTrack supports self-reflection and is not a diagnostic or emergency tool.<br>In crisis (US)? Call or text <b>988</b> — or see Support & Coping.</div>", unsafe_allow_html=True)

# ============================================================================
# HOME PAGE
# ============================================================================

if page == "🏠 Home":
    init_login_state()
    if not st.session_state.logged_in:
        show_login_page()
        st.stop()
    st.markdown(f"<div class='hero-wrap'><div class='hero-icon'>🧠</div><div class='hero-title'>MindTrack</div><div class='hero-tagline'>Welcome back, {st.session_state.current_user}</div></div>", unsafe_allow_html=True)
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

    # NEW: Companion greeting on home
    companion = get_companion(st.session_state.current_user)
    user_state = determine_user_state(st.session_state.current_user)
    companion_msg = get_companion_message(companion, user_state)
    st.markdown(f"<div class='companion-card'><div style='font-size:1.5rem;margin-bottom:8px;'>🤖</div><div style='font-family:Fraunces,serif;font-size:1.1rem;color:{COLOR_INK};margin-bottom:4px;'>{companion.get('companion_name', 'Companion')}</div><div style='color:{COLOR_MUTED};font-style:italic;'>'{companion_msg}'</div></div>", unsafe_allow_html=True)

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
    wellness_tips = ["Take a 5-minute walk outside 🌳", "Practice deep breathing for 2 minutes 🧘", "Drink a glass of water 💧", "Call a friend or family member 📞", "Write down 3 things you're grateful for ✍️", "Stretch your body for 10 minutes 🤸", "Listen to your favorite song 🎵", "Take a short break from screens 📵"]
    st.markdown("## 🌟 Daily Wellness Tip")
    st.info(random.choice(wellness_tips))

    pulse_divider()
    quotes = ["The greatest glory in living lies not in never falling, but in rising every time we fall. – Nelson Mandela", "The way to get started is to quit talking and begin doing. – Walt Disney", "Your time is limited, don't waste it living someone else's life. – Steve Jobs", "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt", "It does not matter how slowly you go as long as you do not stop. – Confucius"]
    st.markdown("## 💬 Motivation")
    st.success(random.choice(quotes))

# ============================================================================
# ASSESSMENT PAGE
# ============================================================================

elif page == "📋 Assessment":
    require_login()
    page_header("📋", "Daily Check-in", "Mental Health Assessment", "A few quick questions to understand how you're doing today.")
    username = st.text_input("👤 Your name", st.session_state.get("current_user", "Guest User"))
    entry_date = st.date_input("📅 Date of this assessment", value=datetime.now().date())
    st.markdown("## Answer the following questions:")
    mood_emojis = {"Very Bad": "😢", "Bad": "😔", "Neutral": "😐", "Good": "😊", "Very Good": "😄"}
    mood = st.select_slider("How is your mood today?", options=["Very Bad", "Bad", "Neutral", "Good", "Very Good"], value="Good", format_func=lambda x: f"{mood_emojis[x]} {x}")
    col1, col2 = st.columns(2)
    with col1:
        sleep_hours = st.slider("😴 How many hours did you sleep last night?", 0, 12, 7)
        stress_level = st.slider("😰 How stressed are you? (0-10)", 0, 10, 3)
    with col2:
        anxiety_level = st.slider("😟 How anxious are you? (0-10)", 0, 10, 3)
        exercise_minutes = st.slider("🏃 How many minutes did you exercise today?", 0, 180, 30)
    preview_score = calculate_wellness_score(stress_level, sleep_hours, anxiety_level, exercise_minutes)
    st.metric("Preview Wellness Score", f"{preview_score}/100")
    goals = get_goals(username)
    if goals:
        st.caption(f"🎯 Your goals: {goals['target_sleep']:.0f}h sleep · {goals['target_exercise']:.0f} min exercise · stress under {goals['target_stress_max']:.0f}")
    if st.button("✅ Submit Assessment"):
        save_user_history(username, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes, entry_date=entry_date)
        st.session_state['assessment_data'] = {"username": username, "date": entry_date, "mood": mood, "sleep_hours": sleep_hours, "stress_level": stress_level, "anxiety_level": anxiety_level, "exercise_minutes": exercise_minutes}
        st.success(f"🎉 Assessment saved for {entry_date.strftime('%Y-%m-%d')}!")

# ============================================================================
# RISK PREDICTION PAGE (ENHANCED WITH EXPLAINABLE AI)
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

        # Use explainable prediction
        result = explainable_risk_prediction(stress, sleep, anxiety, exercise, mood)
        risk, factors, wellness_score = result["risk_level"], [result["top_driver"]], result["wellness_score"]
        recommendations = get_recommendations(stress, sleep, anxiety, exercise)

        st.markdown("## 📊 Prediction Results")
        st.plotly_chart(gauge_figure(wellness_score, "Wellness Score"), use_container_width=True)
        col1, col2 = st.columns(2)
        with col1:
            risk_badge(risk)
        with col2:
            st.metric("Wellness Score", f"{wellness_score}/100")
            st.caption(f"Model: {result['model_version']} | Confidence: {result['confidence']*100:.0f}%")

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

        # NEW: Counterfactual suggestions
        if result['counterfactuals']:
            pulse_divider()
            st.markdown("### 💡 What If?")
            for cf in result['counterfactuals']:
                st.write(f"• {cf}")

        save_prediction(username, risk, wellness_score, factors)

        hist = get_history_data()
        mine = hist[hist["username"].astype(str) == str(username)] if not hist.empty else hist
        if not mine.empty and trend_nudge(mine):
            pulse_divider()
            st.warning("Your recent check-ins suggest things have felt harder lately. That's worth paying attention to — consider reaching out to a professional or someone you trust. The **Support & Coping** page has resources if you'd like them.")

# ============================================================================
# GOALS PAGE
# ============================================================================

elif page == "🎯 Goals":
    require_login()
    page_header("🎯", "Personal Targets", "Your Wellness Goals", "Set targets that matter to you — we'll track your progress against them.")
    username = st.text_input("👤 Your name", st.session_state.get("current_user", "Guest User"), key="goals_username")
    existing = get_goals(username)
    col1, col2, col3 = st.columns(3)
    with col1:
        target_sleep = st.slider("🎯 Target sleep (hours)", 4, 10, int(existing["target_sleep"]) if existing else 8)
    with col2:
        target_exercise = st.slider("🎯 Target exercise (min/day)", 0, 120, int(existing["target_exercise"]) if existing else 30)
    with col3:
        target_stress_max = st.slider("🎯 Max comfortable stress", 0, 10, int(existing["target_stress_max"]) if existing else 5)
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
        g = get_goals(username) or {"target_sleep": target_sleep, "target_exercise": target_exercise, "target_stress_max": target_stress_max}
        gcol1, gcol2, gcol3 = st.columns(3)
        gcol1.metric("Sleep (latest)", f"{last['sleep_hours']:.1f}h", f"{last['sleep_hours'] - g['target_sleep']:+.1f}h vs goal")
        gcol2.metric("Exercise (latest)", f"{last['exercise_minutes']:.0f} min", f"{last['exercise_minutes'] - g['target_exercise']:+.0f} min vs goal")
        gcol3.metric("Stress (latest)", f"{last['stress_level']:.0f}", f"{last['stress_level'] - g['target_stress_max']:+.0f} vs max", delta_color="inverse")

# ============================================================================
# BULK UPLOAD PAGE
# ============================================================================

elif page == "📂 Bulk Upload":
    require_login()
    page_header("📂", "Batch Processing", "Bulk Upload & Analyze", "Upload an Excel file to analyze many records at once.")
    st.write("Upload an Excel file (.xlsx) with multiple records to analyze them all at once, instead of entering them one by one in the Assessment page.")
    REQUIRED_COLUMNS = ["username", "mood", "sleep_hours", "stress_level", "anxiety_level", "exercise_minutes"]
    with st.expander("📋 Expected file format / download a template"):
        st.write(f"Your Excel file must contain these columns: `{'`, `'.join(REQUIRED_COLUMNS)}`")
        st.caption("`mood` must be one of: Very Bad, Bad, Neutral, Good, Very Good. A `date` column is optional.")
        template_df = pd.DataFrame([{"username": "John Doe", "mood": "Good", "sleep_hours": 7, "stress_level": 3, "anxiety_level": 2, "exercise_minutes": 30}])
        st.download_button(label="📥 Download Template (Excel)", data=export_to_excel(template_df, sheet_name="Template"), file_name="bulk_upload_template.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
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
                st.error(f"❌ Missing required column(s): {', '.join(missing_cols)}. Check the template above for the expected format.")
            elif bulk_df.empty:
                st.warning("⚠️ The uploaded file has no rows.")
            else:
                bulk_df = bulk_df.copy()
                if "date" not in bulk_df.columns:
                    bulk_df["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                risk_levels, wellness_scores, factor_lists = [], [], []
                for _, row in bulk_df.iterrows():
                    risk, factors, wellness = predict_risk(row["stress_level"], row["sleep_hours"], row["anxiety_level"], row["exercise_minutes"], row["mood"])
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
                    fig_risk = px.bar(risk_counts, x="Risk", y="Count", color="Risk", title="Risk Level Distribution", color_discrete_map=RISK_COLOR_MAP)
                    st.plotly_chart(style_plot(fig_risk), use_container_width=True)
                with c2:
                    fig_hist = px.histogram(bulk_df, x="wellness_score", nbins=15, title="Wellness Score Distribution", color_discrete_sequence=[COLOR_PRIMARY])
                    st.plotly_chart(style_plot(fig_hist), use_container_width=True)
                st.markdown("### 📥 Export or Save")
                dl_col, save_col = st.columns(2)
                with dl_col:
                    st.download_button(label="📥 Download Analyzed Results (Excel)", data=export_to_excel(bulk_df, sheet_name="Bulk Analysis"), file_name=f"bulk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                with save_col:
                    if st.button("➕ Add these records to the backend data", use_container_width=True):
                        init_db()
                        conn = get_connection()
                        history_rows = bulk_df[["username", "date", "mood", "sleep_hours", "stress_level", "anxiety_level", "exercise_minutes"]].values.tolist()
                        conn.executemany("INSERT INTO user_history (username, date, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes) VALUES (?, ?, ?, ?, ?, ?, ?)", history_rows)
                        prediction_rows = bulk_df[["username", "date", "risk_level", "wellness_score", "factors"]].values.tolist()
                        conn.executemany("INSERT INTO predictions (username, date, risk_level, wellness_score, factors) VALUES (?, ?, ?, ?, ?)", prediction_rows)
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
            filtered_df = filtered_df[(filtered_df["date"].dt.date >= start_date) & (filtered_df["date"].dt.date <= end_date)]
        if filtered_df.empty:
            st.warning("No records match the selected filters.")
        else:
            st.markdown("## 📊 Quick Stats")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Visible Entries", len(filtered_df))
            m2.metric("Avg Wellness", f"{filtered_df['wellness_score'].mean():.0f}/100")
            m3.metric("Avg Mood", f"{filtered_df['mood_num'].mean():.1f}/5")
            m4.metric("Avg Sleep", f"{filtered_df['sleep_hours'].mean():.1f}h")
            st.download_button(label="📥 Download History (Excel)", data=export_to_excel(filtered_df.drop(columns=["mood_num"], errors="ignore"), sheet_name="History"), file_name=f"patient_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            trends_tab, dist_tab, insights_tab = st.tabs(["📈 Trends", "🧩 Distributions", "🔎 Insights"])
            with trends_tab:
                col1, col2 = st.columns(2)
                line_shape = "spline" if chart_style == "Smooth" else "linear"
                with col1:
                    fig_mood = px.line(filtered_df.sort_values("date"), x="date", y="mood_num", markers=True, title="Mood Over Time", color_discrete_sequence=[COLOR_PRIMARY_LIGHT])
                    fig_mood.update_traces(line_shape=line_shape)
                    st.plotly_chart(style_plot(fig_mood), use_container_width=True)
                with col2:
                    fig_sleep = px.area(filtered_df.sort_values("date"), x="date", y="sleep_hours", title="Sleep Pattern", color_discrete_sequence=[COLOR_SLATE])
                    st.plotly_chart(style_plot(fig_sleep), use_container_width=True)
                col3, col4 = st.columns(2)
                with col3:
                    fig_stress = px.line(filtered_df.sort_values("date"), x="date", y="stress_level", markers=True, title="Stress Trend", color_discrete_sequence=[COLOR_MEDIUM])
                    fig_stress.update_traces(line_shape=line_shape)
                    st.plotly_chart(style_plot(fig_stress), use_container_width=True)
                with col4:
                    fig_exercise = px.bar(filtered_df.sort_values("date"), x="date", y="exercise_minutes", title="Exercise Activity", color="exercise_minutes", color_continuous_scale=[[0, "#E7EFEC"], [1, COLOR_PRIMARY]])
                    st.plotly_chart(style_plot(fig_exercise), use_container_width=True)
                fig_wellness = px.line(filtered_df.sort_values("date"), x="date", y="wellness_score", markers=True, title="Overall Wellness Score Trend", color_discrete_sequence=[COLOR_PRIMARY])
                fig_wellness.update_traces(line_shape=line_shape)
                st.plotly_chart(style_plot(fig_wellness), use_container_width=True)
            with dist_tab:
                col1, col2 = st.columns(2)
                with col1:
                    mood_counts = filtered_df["mood"].value_counts().reset_index()
                    mood_counts.columns = ["Mood", "Count"]
                    fig_mood_dist = px.pie(mood_counts, names="Mood", values="Count", hole=0.55, title="Mood Distribution", color_discrete_sequence=CHART_PALETTE)
                    st.plotly_chart(style_plot(fig_mood_dist), use_container_width=True)
                with col2:
                    fig_sleep_box = px.box(filtered_df, y="sleep_hours", points="all", title="Sleep Variability", color_discrete_sequence=[COLOR_SLATE])
                    st.plotly_chart(style_plot(fig_sleep_box), use_container_width=True)
                col3, col4 = st.columns(2)
                with col3:
                    fig_scatter = px.scatter(filtered_df, x="sleep_hours", y="stress_level", size="exercise_minutes", color="wellness_score", hover_data=["username", "mood"], title="Sleep vs Stress vs Exercise", color_continuous_scale=[[0, COLOR_HIGH], [0.5, COLOR_MEDIUM], [1, COLOR_GOOD]])
                    st.plotly_chart(style_plot(fig_scatter), use_container_width=True)
                with col4:
                    if not prediction_df.empty:
                        pred_filtered = prediction_df.copy()
                        if selected_user != "All Users":
                            pred_filtered = pred_filtered[pred_filtered["username"].astype(str) == selected_user]
                        if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                            pred_filtered = pred_filtered[(pred_filtered["date"].dt.date >= start_date) & (pred_filtered["date"].dt.date <= end_date)]
                        if not pred_filtered.empty:
                            risk_counts = pred_filtered["risk_level"].value_counts().reset_index()
                            risk_counts.columns = ["Risk", "Count"]
                            fig_risk = px.bar(risk_counts, x="Risk", y="Count", color="Risk", title="Risk Level Distribution", color_discrete_map=RISK_COLOR_MAP)
                            st.plotly_chart(style_plot(fig_risk), use_container_width=True)
                        else:
                            st.info("No prediction records available for the selected filters.")
                    else:
                        st.info("No prediction records available yet.")
            with insights_tab:
                corr_df = filtered_df[["sleep_hours", "stress_level", "anxiety_level", "exercise_minutes", "mood_num", "wellness_score"]].corr()
                heatmap = go.Figure(data=go.Heatmap(z=corr_df.values, x=corr_df.columns, y=corr_df.index, colorscale=[[0, COLOR_HIGH], [0.5, "#FFFFFF"], [1, COLOR_PRIMARY]], zmin=-1, zmax=1, text=np.round(corr_df.values, 2), texttemplate="%{text}"))
                heatmap.update_layout(title="Correlation Heatmap")
                st.plotly_chart(style_plot(heatmap), use_container_width=True)
                st.plotly_chart(create_mood_calendar(filtered_df), use_container_width=True)
                last_row = filtered_df.sort_values("date").iloc[-1]
                radar_col, info_col = st.columns([1.2, 1])
                with radar_col:
                    st.plotly_chart(create_wellness_radar(last_row["sleep_hours"], last_row["stress_level"], last_row["anxiety_level"], last_row["exercise_minutes"], last_row["mood"]), use_container_width=True)
                with info_col:
                    st.markdown("### Latest Snapshot")
                    st.metric("Latest Wellness", f"{last_row['wellness_score']:.0f}/100")
                    st.metric("Latest Mood", last_row["mood"])
                    st.metric("Latest Stress", f"{last_row['stress_level']}/10")
                    st.metric("Latest Anxiety", f"{last_row['anxiety_level']}/10")
                if trend_nudge(filtered_df):
                    st.warning("Wellness scores have been trending down over the last few check-ins. Consider visiting **Support & Coping** or reaching out to someone you trust.")

# ============================================================================
# JOURNAL PAGE (ENHANCED WITH CULTURAL ADAPTATION)
# ============================================================================

elif page == "📝 Journal":
    require_login()
    page_header("📝", "Reflection", "Journal & Sentiment Analysis", "Write about your day and we'll analyze your mood.")
    username = st.text_input("👤 Your name", st.session_state.get("current_user", "Guest User"), key="journal_username")
    journal_text = st.text_area("Your Journal Entry:", height=250, placeholder="How was your day? What made you happy or worried?")
    if st.button("🔍 Analyze & Save"):
        if journal_text.strip():
            # Check cultural profile for adjusted sentiment
            profile = get_cultural_profile(username)
            stress_style = profile.get("stress_expression_style", "direct") if profile else "direct"
            sentiment, polarity = culturally_adjusted_sentiment(journal_text.strip(), stress_style)
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
                if profile and stress_style in ["indirect", "somatic"]:
                    st.caption(f"💡 Analysis adjusted for {stress_style} expression style")
            with col2:
                fig_polarity = gauge_figure(polarity, "Polarity", value_range=(-1, 1), steps=[{'range': [-1, -0.1], 'color': COLOR_HIGH}, {'range': [-0.1, 0.1], 'color': COLOR_MEDIUM}, {'range': [0.1, 1], 'color': COLOR_GOOD}])
                st.plotly_chart(fig_polarity, use_container_width=True)
            st.markdown("### 📝 Your Entry:")
            st.write(journal_text)
            st.success(f"✅ Entry saved for {username} at {entry['date']}!")
            if sentiment == "negative" and polarity < -0.4:
                pulse_divider()
                st.info("That sounds like a heavy day. Writing it down is a good step — if it would help, the **Support & Coping** page has grounding techniques and resources.")
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
            fig = px.line(df_chart, x="date", y="polarity", markers=True, title="Polarity Over Time", color_discrete_sequence=[COLOR_PRIMARY])
            fig.add_scatter(x=df_chart["date"], y=df_chart["polarity_smooth"], mode="lines", name="Trend", line=dict(color=COLOR_MEDIUM, width=2))
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
            st.download_button("📥 Download My Journals (Excel)", data=export_journal_to_excel(username), file_name=f"{username}_journals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
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
        st.download_button("📥 Download My Data (Excel)", data=export_to_excel(mine.drop(columns=["mood_num"], errors="ignore"), sheet_name="My History"), file_name=f"{username}_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
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
    prompts = ["What's one thing that felt hard today, and one thing that helped?", "What would I tell a friend who felt the way I feel right now?", "What's one small thing I can do in the next hour to take care of myself?"]
    for p in prompts:
        st.info(p)
    pulse_divider()
    st.markdown("### 📞 If You Need to Talk to Someone")
    # Show localized resources
    profile = get_cultural_profile(st.session_state.get("current_user", ""))
    country = profile.get("country_code", "US") if profile else "US"
    resource = get_localized_crisis_resource(country)
    st.error(f"**{resource['name']}** — call or text **{resource['number']}**")
    st.warning("**Crisis Text Line** — text **HOME** to **741741** (US & Canada).")
    st.info("**Outside the US** — search '[your country] crisis helpline' or contact local emergency services.")
    st.caption("MindTrack is a self-reflection tool, not a diagnostic service or emergency line. If you are in immediate danger, please contact local emergency services right away.")

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
        st.download_button("📥 Download PDF Report", data=pdf_buffer, file_name=f"mental_health_report_{username}.pdf", mime="application/pdf")

# ============================================================================
# ADMIN PAGE
# ============================================================================

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
                st.download_button("📥 Download Patient History (Excel)", data=export_to_excel(df_history, sheet_name="Patient History"), file_name=f"patient_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
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
                st.download_button("📥 Download Predictions (Excel)", data=export_to_excel(df_predictions, sheet_name="Predictions"), file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
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

# ============================================================================
# NEW FEATURE PAGE 1: CRISIS PLAN
# ============================================================================

elif page == "🛡️ Crisis Plan":
    require_login()
    page_header("🛡️", "Safety First", "Your Personal Safety Plan",
                "Evidence-based crisis planning, always accessible — even offline.")

    username = st.text_input("👤 Your name", st.session_state.get("current_user", ""), key="crisis_username")
    existing = get_crisis_plan(username)

    # Crisis detection banner
    is_crisis, signals, severity = detect_crisis_signals(username)
    if is_crisis:
        st.markdown(f"<div class='crisis-banner'><h3>🚨 CRISIS SIGNALS DETECTED</h3><p>Severity: {severity}/10</p></div>", unsafe_allow_html=True)
        for sig in signals:
            st.warning(f"• {sig}")
        st.info("Please use your safety plan below or contact emergency services immediately.")

    # One-tap crisis resources (always visible)
    st.markdown("### 🆘 Immediate Support")
    profile = get_cultural_profile(username)
    country = profile.get("country_code", "US") if profile else "US"
    resource = get_localized_crisis_resource(country)

    c1, c2, c3 = st.columns(3)
    with c1:
        if resource["number"]:
            st.markdown(f"**📞 {resource['name']}**  \n<a href='tel:{resource['number']}' style='font-size:1.5rem;'>☎️ {resource['number']}</a>", unsafe_allow_html=True)
    with c2:
        if resource["text"]:
            st.markdown(f"**💬 Text**  \n`{resource['text']}`")
    with c3:
        st.markdown("**🌐 Global**  \n[FindAHelpline.com](https://findahelpline.com)")

    pulse_divider()

    # Safety Plan Builder (Stanley & Brown model)
    st.markdown("### 📝 Build Your Safety Plan")
    st.caption("Based on the Stanley & Brown Safety Planning Intervention — evidence-based and clinically validated.")

    with st.form("safety_plan_form"):
        warning_signs = st.text_area("1. Warning Signs", 
            value=existing["warning_signs"] if existing else "",
            placeholder="What thoughts, feelings, or situations tell you a crisis might be coming?")

        coping_strategies = st.text_area("2. Internal Coping Strategies",
            value=existing["coping_strategies"] if existing else "",
            placeholder="What can you do on your own to distract or soothe yourself?")

        distraction_places = st.text_area("3. Places for Distraction",
            value=existing["distraction_places"] if existing else "",
            placeholder="Where can you go to feel safer or calmer?")

        st.markdown("#### 4. People Who Can Help")
        col1, col2, col3 = st.columns(3)
        with col1:
            contact1_name = st.text_input("Name", value="", key="c1_name")
            contact1_phone = st.text_input("Phone", value="", key="c1_phone")
            contact1_relation = st.text_input("Relationship", value="", key="c1_rel")
        with col2:
            contact2_name = st.text_input("Name", value="", key="c2_name")
            contact2_phone = st.text_input("Phone", value="", key="c2_phone")
            contact2_relation = st.text_input("Relationship", value="", key="c2_rel")
        with c3:
            contact3_name = st.text_input("Name", value="", key="c3_name")
            contact3_phone = st.text_input("Phone", value="", key="c3_phone")
            contact3_relation = st.text_input("Relationship", value="", key="c3_rel")

        professional_contacts = st.text_area("5. Professional Contacts",
            value=existing["professional_contacts"] if existing else "",
            placeholder="Therapist, psychiatrist, or other professional contacts")

        means_safety = st.text_area("6. Means Safety Plan",
            value=existing["means_safety"] if existing else "",
            placeholder="Steps to make your environment safer during a crisis")

        reasons_for_living = st.text_area("7. Reasons for Living",
            value=existing["reasons_for_living"] if existing else "",
            placeholder="What makes life worth living for you?")

        submitted = st.form_submit_button("💾 Save Safety Plan", use_container_width=True)
        if submitted:
            contacts = []
            for name, phone, rel in [(contact1_name, contact1_phone, contact1_relation),
                                      (contact2_name, contact2_phone, contact2_relation),
                                      (contact3_name, contact3_phone, contact3_relation)]:
                if name and phone:
                    contacts.append({"name": name, "phone": phone, "relation": rel})
            save_crisis_plan(username, warning_signs, coping_strategies,
                           distraction_places, json.dumps(contacts),
                           professional_contacts, means_safety, reasons_for_living)
            st.success("✅ Safety plan saved! It's stored locally and accessible offline.")

    # Display existing plan
    if existing:
        pulse_divider()
        st.markdown("### 📋 Your Saved Safety Plan")
        st.info(f"**Warning Signs:** {existing['warning_signs']}")
        st.success(f"**Coping Strategies:** {existing['coping_strategies']}")
        st.write(f"**Distraction Places:** {existing['distraction_places']}")
        if existing['support_contacts']:
            contacts = json.loads(existing['support_contacts'])
            for c in contacts:
                st.markdown(f"👤 **{c['name']}** ({c['relation']}) — 📞 {c['phone']}")
        st.write(f"**Professional Contacts:** {existing['professional_contacts']}")
        st.warning(f"**Means Safety:** {existing['means_safety']}")
        st.write(f"**Reasons for Living:** {existing['reasons_for_living']}")

# ============================================================================
# NEW FEATURE PAGE 2: DIGITAL PHENOTYPE
# ============================================================================

elif page == "🔬 Digital Phenotype":
    require_login()
    page_header("🔬", "Deep Signals", "Your Digital Phenotype",
                "Transdiagnostic markers that reveal patterns across mood, sleep, and activity.")

    username = st.text_input("👤 Your name", st.session_state.get("current_user", ""), key="pheno_username")
    phenotype = get_digital_phenotype(username)

    if phenotype is None:
        st.info("Complete at least 3 assessments to generate your digital phenotype.")
    else:
        st.markdown("### 🧬 Transdiagnostic Markers")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sleep Consistency", f"{phenotype['sleep_consistency']}/100",
                     help="How regular your sleep schedule is. Low consistency is a risk marker for mood disorders.")
        with col2:
            st.metric("Social Rhythm Index", f"{phenotype['social_rhythm_index']}/100",
                     help="Regularity of daily routines. Irregular rhythms predict mood episodes.")
        with col3:
            st.metric("Circadian Alignment", f"{phenotype['circadian_alignment']}/100",
                     help="How consistently you check in at the same time of day.")

        pulse_divider()
        st.markdown("### 📊 Detailed Patterns")

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Avg Sleep", f"{phenotype['avg_sleep']:.1f}h")
            st.metric("Sleep Variability", f"±{phenotype['sleep_variability']:.1f}h")
            st.metric("Activity Level", f"{phenotype['activity_level']:.0f} min/day")
        with c2:
            st.metric("Stress Trend", phenotype['stress_trend'])
            st.metric("Mood Volatility", f"{phenotype['mood_volatility']:.2f}" if phenotype['mood_volatility'] else "N/A")
            st.metric("Tracking Span", f"{phenotype['days_span']} days")

        # Phenotype visualization
        categories = ["Sleep\nConsistency", "Social\nRhythm", "Circadian\nAlignment"]
        values = [phenotype['sleep_consistency'], phenotype['social_rhythm_index'], phenotype['circadian_alignment']]
        fig = go.Figure(go.Bar(x=categories, y=values, marker_color=[COLOR_PRIMARY, COLOR_SLATE, COLOR_PRIMARY_LIGHT]))
        fig.update_layout(title="Digital Phenotype Profile", yaxis_range=[0, 100])
        st.plotly_chart(style_plot(fig), use_container_width=True)

        # Interpretation
        pulse_divider()
        st.markdown("### 🧠 What This Means")
        if phenotype['sleep_consistency'] < 50:
            st.warning("Your sleep consistency is low. Irregular sleep is one of the strongest predictors of mood instability. Consider setting a consistent bedtime.")
        if phenotype['social_rhythm_index'] < 50:
            st.warning("Your daily routines are quite variable. Regular routines (meals, exercise, sleep) act as 'anchors' for emotional stability.")
        if phenotype['sleep_consistency'] > 70 and phenotype['social_rhythm_index'] > 70:
            st.success("Your sleep and routines are well-regulated. This is a strong protective factor for mental health.")

# ============================================================================
# NEW FEATURE PAGE 3: EXPLAINABLE AI
# ============================================================================

elif page == "🧠 Explainable AI":
    require_login()
    page_header("🧠", "Transparent AI", "Explainable Risk Analysis",
                "See exactly how your wellness score is calculated — no black boxes.")

    if 'assessment_data' not in st.session_state:
        st.warning("⚠️ Please complete the Assessment first!")
    else:
        data = st.session_state['assessment_data']
        result = explainable_risk_prediction(
            data["stress_level"], data["sleep_hours"],
            data["anxiety_level"], data["exercise_minutes"], data["mood"]
        )

        st.markdown("### 📊 Your Wellness Score Breakdown")
        st.metric("Wellness Score", f"{result['wellness_score']}/100",
                 help=f"Model: {result['model_version']} | Confidence: {result['confidence']*100:.0f}%")

        # Explanation chart
        st.plotly_chart(create_explanation_chart(result['contributions']), use_container_width=True)

        # Detailed contributions
        st.markdown("### 🔍 How Each Factor Contributed")
        for factor, details in result['contributions'].items():
            progress = details['points'] / details['max_possible']
            color = COLOR_GOOD if progress > 0.7 else COLOR_MEDIUM if progress > 0.4 else COLOR_HIGH
            st.markdown(f"""
            <div style="margin-bottom: 12px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                    <b>{factor}</b>
                    <span style="color:{color}">{details['points']:.1f}/{details['max_possible']}</span>
                </div>
                <div style="background:#eee; border-radius:4px; height:8px;">
                    <div style="background:{color}; width:{progress*100}%; height:100%; border-radius:4px;"></div>
                </div>
                <small style="color:{COLOR_MUTED}">{details['explanation']}</small>
            </div>
            """, unsafe_allow_html=True)

        # Top driver
        st.info(f"🔑 **Top Improvement Opportunity:** {result['top_driver']} — this is where you have the most room to grow.")

        # Counterfactuals
        if result['counterfactuals']:
            pulse_divider()
            st.markdown("### 💡 What If? (Counterfactual Analysis)")
            st.caption("See how small changes could improve your score:")
            for cf in result['counterfactuals']:
                st.success(cf)

        # Confidence interval
        pulse_divider()
        st.markdown("### 📈 Uncertainty & Confidence")
        st.write(f"**Confidence Interval:** {result['confidence_interval'][0]:.0f} — {result['confidence_interval'][1]:.0f}")
        st.caption("This range reflects the natural variability in self-reported data. Your true wellness likely falls within this band.")

        # Bias audit note
        st.markdown("### ⚖️ Fairness & Bias Check")
        st.write("This model uses the same transparent rules for all users. No demographic data is used in scoring. Risk factors are based on established clinical literature (sleep, stress, anxiety, exercise, mood).")

# ============================================================================
# NEW FEATURE PAGE 4: CLINICIAN PORTAL
# ============================================================================

elif page == "👨‍⚕️ Clinician Portal":
    require_login()
    page_header("👨‍⚕️", "Shared Care", "Clinician Dashboard",
                "Collaborative care with your mental health professional.")

    tab1, tab2 = st.tabs(["🔗 Link to Clinician", "📋 Clinician View"])

    with tab1:
        st.markdown("### Connect with Your Clinician")
        username = st.text_input("Your name", st.session_state.get("current_user", ""), key="clinician_patient")
        clinician_code = st.text_input("Clinician Access Code", placeholder="Enter code provided by your clinician")
        share_level = st.select_slider("Data Sharing Level", 
            options=["summary", "detailed", "full"],
            value="summary",
            format_func=lambda x: {"summary": "Summary only", "detailed": "Trends + alerts", "full": "All data including journals"}[x])

        if st.button("🔗 Request Link"):
            link_clinician(username, clinician_code, share_level)
            st.success("Link request sent! Your clinician will need to approve it.")
            st.info("You can revoke this at any time from this page.")

    with tab2:
        st.markdown("### Clinician Access")
        clinician_code = st.text_input("Enter your clinician code", key="clinician_code")
        patients = get_clinician_patients(clinician_code)

        if not patients:
            st.info("No approved patient links found.")
        else:
            st.success(f"{len(patients)} patient(s) linked")
            for p in patients:
                with st.expander(f"👤 {p['patient_username']}"):
                    summary = get_patient_summary_for_clinician(p['patient_username'], p['share_level'])
                    if summary:
                        st.metric("Current Wellness", f"{summary['current_risk']:.0f}/100")
                        st.metric("Risk Trend", summary['risk_trend'])
                        st.metric("Total Entries", summary['total_entries'])

                        if summary['alerts']:
                            st.error("🚨 Active Alerts:")
                            for alert in summary['alerts']:
                                st.warning(f"• {alert}")

                        st.write(f"**Sleep:** {summary['sleep_avg']:.1f}h | **Stress:** {summary['stress_avg']:.1f}/10 | **Anxiety:** {summary['anxiety_avg']:.1f}/10")
                        st.write(f"**Exercise:** {summary['exercise_avg']:.0f}min/day")

                        if 'journal_sentiment_trend' in summary:
                            st.write(f"**Journal Sentiment Trend:** {summary['journal_sentiment_trend']:.2f}")


# ============================================================================
# NEW FEATURE PAGE 5: CULTURAL PROFILE
# ============================================================================

elif page == "🌍 Cultural Profile":
    require_login()
    page_header("🌍", "Your Context", "Cultural & Accessibility Profile",
                "Help us understand your context so we can support you better.")

    username = st.text_input("Your name", st.session_state.get("current_user", ""), key="cultural_username")
    existing = get_cultural_profile(username)

    with st.form("cultural_form"):
        col1, col2 = st.columns(2)
        with col1:
            country_options = ["US", "UK", "CA", "AU", "IN", "DE", "FR", "Other"]
            country_idx = 0
            if existing and existing.get("country_code") in country_options:
                country_idx = country_options.index(existing.get("country_code"))
            country_code = st.selectbox("Country/Region", country_options, index=country_idx)
            primary_language = st.text_input("Primary Language", value=existing["primary_language"] if existing else "")
            stress_options = ["direct", "indirect", "somatic", "behavioral"]
            stress_idx = 0
            if existing and existing.get("stress_expression_style") in stress_options:
                stress_idx = stress_options.index(existing.get("stress_expression_style"))
            stress_expression = st.selectbox("How do you typically express stress?", stress_options, index=stress_idx)
        with col2:
            cultural_values = st.text_area("Cultural Values (optional)", value=existing["cultural_values"] if existing else "", placeholder="e.g., collectivism, family honor, individual achievement")
            family_structure = st.text_input("Family Structure (optional)", value=existing["family_structure"] if existing else "")
            religious_spiritual = st.text_input("Religious/Spiritual Background (optional)", value=existing["religious_spiritual"] if existing else "")

        accessibility_options = ["None", "Screen reader", "High contrast", "Dyslexia-friendly font", "Large text", "Reduced motion", "Cognitive accessibility"]
        default_access = []
        if existing and existing.get("accessibility_needs"):
            default_access = [a.strip() for a in existing.get("accessibility_needs").split(",") if a.strip() in accessibility_options]
        accessibility_needs = st.multiselect("Accessibility Needs", accessibility_options, default=default_access)

        trauma_history = st.checkbox("I have experienced trauma and would like trauma-informed content", value=bool(existing["trauma_history_disclosed"]) if existing else False)

        submitted = st.form_submit_button("💾 Save Profile")
        if submitted:
            save_cultural_profile(username, country_code, primary_language, cultural_values, stress_expression, family_structure, religious_spiritual, ",".join(accessibility_needs), 1 if trauma_history else 0)
            st.success("Profile saved! Your crisis resources and sentiment analysis will now be adapted.")

    if existing:
        pulse_divider()
        st.markdown("### 🌍 Your Localized Resources")
        resource = get_localized_crisis_resource(existing.get("country_code", "US"))
        st.info(f"Crisis support for your region: **{resource['name']}** — {resource['number']}")
        if existing.get("stress_expression_style") in ["indirect", "somatic"]:
            st.info("💡 Your profile indicates you may express distress through physical symptoms. We'll watch for somatic language in your journal entries.")

# ============================================================================
# NEW FEATURE PAGE 6: QUICK CHECK-IN
# ============================================================================

elif page == "⚡ Quick Check-in":
    require_login()
    page_header("⚡", "30 Seconds", "Quick Check-in",
                "A micro-assessment for when you don't have time for the full form.")

    username = st.text_input("Your name", st.session_state.get("current_user", ""), key="quick_username")

    st.markdown("### How are you right now?")

    col1, col2, col3, col4, col5 = st.columns(5)
    emoji_selected = st.session_state.get('selected_emoji', None)

    with col1:
        if st.button("😢", use_container_width=True):
            st.session_state['selected_emoji'] = "😢"
            st.rerun()
    with col2:
        if st.button("😔", use_container_width=True):
            st.session_state['selected_emoji'] = "😔"
            st.rerun()
    with col3:
        if st.button("😐", use_container_width=True):
            st.session_state['selected_emoji'] = "😐"
            st.rerun()
    with col4:
        if st.button("😊", use_container_width=True):
            st.session_state['selected_emoji'] = "😊"
            st.rerun()
    with col5:
        if st.button("😄", use_container_width=True):
            st.session_state['selected_emoji'] = "😄"
            st.rerun()

    if st.session_state.get('selected_emoji'):
        st.success(f"Selected: {st.session_state['selected_emoji']}")

    energy = st.slider("Energy level", 1, 5, 3, help="1 = exhausted, 5 = energized")
    stress = st.slider("Stress level", 1, 5, 3, help="1 = calm, 5 = overwhelmed")

    on_meds = st.checkbox("I'm on medication")
    took_meds = None
    if on_meds:
        took_meds = 1 if st.checkbox("Took prescribed medication today") else 0
    sleep_quality = st.slider("Last night's sleep quality", 1, 5, 3, help="1 = terrible, 5 = excellent")

    if st.button("✅ Save Quick Check-in", use_container_width=True):
        emoji = st.session_state.get('selected_emoji', '😐')
        save_micro_checkin(username, emoji, energy, stress, took_meds, sleep_quality)
        st.success("Quick check-in saved! ⚡")
        st.session_state['selected_emoji'] = None

        recent = get_micro_checkins(username, days=7)
        if not recent.empty:
            st.markdown("### 📈 Your Recent Quick Check-ins")
            fig = px.scatter(recent, x="timestamp", y="energy_level", color="stress_level", size="sleep_quality",
                           title="Energy vs. Stress Over Time", color_continuous_scale=[COLOR_GOOD, COLOR_MEDIUM, COLOR_HIGH])
            st.plotly_chart(style_plot(fig), use_container_width=True)

    optimal = get_optimal_checkin_time(username)
    st.caption(f"💡 Based on your patterns, you tend to engage best around {optimal}:00. Consider setting a reminder then.")

    pulse_divider()
    narrative = generate_progress_narrative(username)
    st.markdown("### 📖 Your Wellness Story")
    st.info(narrative)

# ============================================================================
# NEW FEATURE PAGE 7: EMA SURVEY
# ============================================================================

elif page == "📍 EMA Survey":
    require_login()
    page_header("📍", "Right Now", "Ecological Momentary Assessment",
                "Capture how you feel in the moment — context matters.")

    username = st.text_input("Your name", st.session_state.get("current_user", ""), key="ema_username")

    st.markdown("### How do you feel RIGHT NOW?")
    st.caption("This captures your momentary state, not how you felt earlier today.")

    with st.form("ema_form"):
        mood = st.slider("Current mood", 1, 10, 5, help="1 = terrible, 10 = excellent")
        energy = st.slider("Current energy", 1, 10, 5)
        social = st.slider("Social connection right now", 1, 10, 5, help="1 = very isolated, 10 = deeply connected")

        context = st.selectbox("What are you doing right now?",
            ["work", "home", "socializing", "commuting", "exercising", "relaxing", "eating", "sleeping_prep", "other"])

        location = st.selectbox("Where are you?",
            ["home", "work", "school", "outdoors", "public_transport", "social_venue", "healthcare", "other"])

        triggered = st.text_input("What triggered this feeling? (optional)", placeholder="e.g., argument, good news, nothing specific")
        notes = st.text_area("Anything else? (optional)", height=80)

        submitted = st.form_submit_button("📍 Log This Moment")
        if submitted:
            save_ema_survey(username, mood, context, energy, social, location, triggered, notes)
            st.success("Moment captured! 📍")

    patterns = analyze_ema_patterns(username)
    if patterns:
        pulse_divider()
        st.markdown("### 🧩 Your Situational Patterns")
        for key, insight in patterns.items():
            st.info(insight)

    ema_df = get_ema_surveys(username, days=14)
    if not ema_df.empty and len(ema_df) >= 3:
        pulse_divider()
        st.markdown("### 📊 EMA Trends")
        fig = px.line(ema_df, x="timestamp", y=["mood", "energy", "social_connection"],
                     title="Your Momentary States Over Time",
                     color_discrete_sequence=[COLOR_PRIMARY, COLOR_SLATE, COLOR_PRIMARY_LIGHT])
        st.plotly_chart(style_plot(fig), use_container_width=True)

        context_mood = ema_df.groupby("context")["mood"].mean().reset_index()
        fig2 = px.bar(context_mood, x="context", y="mood", title="Average Mood by Context",
                     color="mood", color_continuous_scale=[COLOR_HIGH, COLOR_MEDIUM, COLOR_GOOD])
        st.plotly_chart(style_plot(fig2), use_container_width=True)

# ============================================================================
# NEW FEATURE PAGE 8: AI COMPANION
# ============================================================================

elif page == "🤖 My Companion":
    require_login()
    page_header("🤖", "Your Ally", "My Wellness Companion",
                "A consistent, empathetic presence that learns with you.")

    username = st.text_input("Your name", st.session_state.get("current_user", ""), key="companion_username")
    companion = get_companion(username)

    user_state = determine_user_state(username)
    message = get_companion_message(companion, user_state)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLOR_PRIMARY}15, {COLOR_PRIMARY_LIGHT}10); border: 1px solid {COLOR_PRIMARY}40; border-radius: 16px; padding: 24px; margin: 20px 0;">
        <div style="font-size: 2rem; margin-bottom: 8px;">🤖</div>
        <div style="font-family: 'Fraunces', serif; font-size: 1.2rem; color: {COLOR_INK}; margin-bottom: 8px;">
            {companion.get('companion_name', 'Companion')}
        </div>
        <div style="color: {COLOR_MUTED}; font-style: italic;">
            "{message}"
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("⚙️ Customize Your Companion"):
        with st.form("companion_form"):
            new_name = st.text_input("Name your companion", value=companion.get("companion_name", "Companion"))
            tone_options = ["warm", "gentle", "encouraging", "direct", "playful"]
            tone_idx = tone_options.index(companion.get("personality_tone", "warm")) if companion.get("personality_tone") in tone_options else 0
            tone = st.selectbox("Personality tone", tone_options, index=tone_idx)
            empathy = st.slider("Empathy level", 1, 10, companion.get("empathy_level", 5),
                              help="Higher = more emotionally attuned, Lower = more practical/action-oriented")

            if st.form_submit_button("💾 Save"):
                update_companion(username, new_name, tone, empathy)
                st.success(f"{new_name} is ready to support you!")
                st.rerun()

    state_colors = {"crisis": COLOR_HIGH, "distressed": COLOR_MEDIUM, "neutral": COLOR_SLATE, "improving": COLOR_GOOD}
    st.caption(f"Current state detected: **{user_state.title()}** | Tone calibrated accordingly")

    pulse_divider()
    st.markdown("### 🔍 About Your Companion")
    name = companion.get('companion_name', 'Companion')
    st.write(f"**{name}** is an AI-powered wellness companion, not a human therapist. Here's what that means:")
    st.write(f"- **Consistent presence**: {name} remembers your preferences and progress")
    st.write(f"- **Empathy calibration**: Tone adjusts based on your detected state")
    st.write(f"- **Not a replacement**: {name} complements — never replaces — professional care")
    st.write(f"- **Human handoff**: When needed, {name} will guide you to real human support")
    st.write(f"- **Your data stays yours**: All memories are stored locally on your device")
    st.info(f"💡 **Research note**: Studies show AI companions can establish strong working alliances, but empathy gaps exist. We've designed {name} to be transparent about being AI while maintaining consistent, warm support.")
