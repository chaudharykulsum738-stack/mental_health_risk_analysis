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

/* Sidebar */
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

/* Page header + signature divider */
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

/* Hero */
.hero-wrap {{ text-align: center; padding: 2.6rem 0 1.6rem 0; }}
.hero-icon {{ font-size: 3.2rem; }}
.hero-title {{ font-family: 'Fraunces', serif; font-size: 2.6rem; margin: 0.25rem 0 0.35rem 0; color: var(--ink); font-weight: 700; }}
.hero-tagline {{
    font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.10em; text-transform: uppercase;
    font-size: 0.82rem; color: var(--primary); font-weight: 600;
}}

/* Cards & metrics */
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

/* Buttons */
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

/* Alerts / tabs / misc */
div[data-testid="stAlert"] {{ border-radius: 10px; border: 1px solid var(--border); }}
button[data-baseweb="tab"] {{ font-family: 'Inter', sans-serif; font-weight: 600; color: var(--muted); }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: var(--primary); }}
[data-testid="stSlider"] [role="slider"] {{ background-color: var(--primary) !important; }}
hr {{ display: none; }}

/* Streak badge */
.streak-badge {{
    display: inline-flex; align-items: center; gap: 6px; background: rgba(217,164,65,0.12);
    border: 1px solid rgba(217,164,65,0.35); color: var(--medium) !important; border-radius: 999px;
    padding: 4px 14px; font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem; font-weight: 600;
}}

/* Breathing exercise */
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

/* Entry row card (My Entries page) */
.entry-row {{
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    padding: 10px 16px; margin-bottom: 8px;
}}

/* Login styles */
.login-box {{
    max-width: 400px; margin: 2rem auto; padding: 2rem;
    background: #fff; border: 1px solid rgba(27,36,48,0.10);
    border-radius: 14px; text-align: center;
}}
.login-icon {{ font-size: 3rem; margin-bottom: 0.5rem; }}
.login-title {{
    font-family: 'Fraunces', serif; font-size: 1.8rem; font-weight: 700;
    color: var(--ink); margin: 0.5rem 0 0.2rem 0;
}}
.login-subtitle {{ color: var(--muted); font-size: 0.95rem; margin-bottom: 1.8rem; }}
.login-input {{ font-size: 1rem; }}
</style>
""", unsafe_allow_html=True)

DB_PATH = "mindtrack.db"

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, date TIMESTAMP, mood TEXT, mood_num INTEGER,
        stress_level INTEGER, sleep_hours FLOAT, anxiety_level INTEGER,
        exercise_minutes INTEGER, wellness_score FLOAT,
        cognitive_clarity INTEGER, emotional_stability INTEGER,
        social_connection INTEGER, physical_vitality INTEGER,
        stress_management INTEGER
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, date TIMESTAMP, risk_level TEXT,
        wellness_score FLOAT, factors TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recovery_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, date TIMESTAMP, 
        recovery_time_hours FLOAT, recovery_triggers TEXT,
        recovery_methods TEXT, effectiveness_score INTEGER
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, goal_name TEXT, target_value FLOAT,
        current_value FLOAT, category TEXT, created_date TIMESTAMP,
        deadline TIMESTAMP, status TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journal_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, date TIMESTAMP, text TEXT
    )
    """)
    
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)

def predict_risk(stress, sleep, anxiety, exercise, mood, cognitive=50, emotional=50, social=50, physical=50, management=50):
    """Enhanced risk prediction with new features."""
    risk_points = 0
    factors = []
    
    # Original factors
    if stress > 7: risk_points += 2; factors.append("High stress levels")
    if sleep < 6: risk_points += 2; factors.append("Insufficient sleep")
    if anxiety > 7: risk_points += 2; factors.append("Elevated anxiety")
    if exercise < 30: risk_points += 1; factors.append("Low physical activity")
    
    # New feature factors
    if cognitive < 40: risk_points += 1; factors.append("Low cognitive clarity")
    if emotional < 40: risk_points += 2; factors.append("Emotional instability")
    if social < 40: risk_points += 1; factors.append("Limited social connection")
    if physical < 40: risk_points += 1; factors.append("Low physical vitality")
    if management < 40: risk_points += 1; factors.append("Poor stress management")
    
    mood_map = {"😢 Very Low": 4, "😞 Low": 3, "😐 Neutral": 2, "🙂 Good": 1, "😄 Excellent": 0}
    mood_num = mood_map.get(mood, 2)
    if mood_num > 2: risk_points += mood_num - 1
    
    # Calculate wellness score (aggregate of all features)
    wellness_components = [
        (100 - stress * 10) * 0.15,
        (sleep / 8 * 100) * 0.15,
        (100 - anxiety * 10) * 0.15,
        (exercise / 60 * 100) * 0.15,
        cognitive * 0.12,
        emotional * 0.12,
        social * 0.08,
        physical * 0.08,
        management * 0.04
    ]
    wellness_score = max(0, min(100, sum(wellness_components)))
    
    if risk_points >= 6:
        return "High", factors, wellness_score
    elif risk_points >= 3:
        return "Medium", factors, wellness_score
    else:
        return "Low", factors, wellness_score

def get_recommendations(stress, sleep, anxiety, exercise):
    """Generate recommendations based on inputs."""
    recs = []
    if stress > 7: recs.append("Practice relaxation techniques (meditation, deep breathing)")
    if sleep < 6: recs.append("Prioritize sleep hygiene; aim for 7-8 hours")
    if anxiety > 7: recs.append("Consider cognitive behavioral techniques or professional support")
    if exercise < 30: recs.append("Increase physical activity to 30+ minutes daily")
    return recs if recs else ["Continue maintaining your wellness routine!"]

def save_assessment_data(username, mood, stress, sleep, anxiety, exercise, cognitive, emotional, social, physical, management):
    """Save assessment data including new features."""
    conn = get_connection()
    cursor = conn.cursor()
    
    risk, factors, wellness_score = predict_risk(stress, sleep, anxiety, exercise, mood, cognitive, emotional, social, physical, management)
    mood_num = {"😢 Very Low": 0, "😞 Low": 1, "😐 Neutral": 2, "🙂 Good": 3, "😄 Excellent": 4}.get(mood, 2)
    
    cursor.execute("""
    INSERT INTO user_history (username, date, mood, mood_num, stress_level, sleep_hours, anxiety_level,
                              exercise_minutes, wellness_score, cognitive_clarity, emotional_stability,
                              social_connection, physical_vitality, stress_management)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, datetime.now(), mood, mood_num, stress, sleep, anxiety, exercise, wellness_score,
          cognitive, emotional, social, physical, management))
    
    cursor.execute("""
    INSERT INTO predictions (username, date, risk_level, wellness_score, factors)
    VALUES (?, ?, ?, ?, ?)
    """, (username, datetime.now(), risk, wellness_score, " | ".join(factors)))
    
    conn.commit()
    conn.close()

def get_history_data():
    """Retrieve history data from database."""
    try:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM user_history", conn)
        conn.close()
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except:
        return pd.DataFrame()

def save_recovery_pattern(username, recovery_time, triggers, methods, effectiveness):
    """Save recovery pattern data."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO recovery_patterns (username, date, recovery_time_hours, recovery_triggers, recovery_methods, effectiveness_score)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (username, datetime.now(), recovery_time, triggers, methods, effectiveness))
    conn.commit()
    conn.close()

def get_recovery_patterns(username):
    """Get recovery patterns for a user."""
    try:
        conn = get_connection()
        df = pd.read_sql_query(
            "SELECT * FROM recovery_patterns WHERE username = ? ORDER BY date DESC", 
            (username,), 
            con=conn
        )
        conn.close()
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except:
        return pd.DataFrame()

def export_to_excel(df, sheet_name="Sheet1"):
    """Export dataframe to Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return output.getvalue()

def risk_badge(risk_level):
    """Display risk badge."""
    color = RISK_COLOR_MAP.get(risk_level, "#999")
    st.markdown(f'<span style="background: {color}20; border: 1px solid {color}; color: {color}; padding: 8px 12px; border-radius: 8px; font-weight: 600;">⚠️ Risk Level: {risk_level}</span>', unsafe_allow_html=True)

def page_header(icon, eyebrow, title, subtitle):
    """Display page header."""
    st.markdown(f'''
    <div class="page-header">
        <div class="page-header-icon">{icon}</div>
        <div style="flex: 1;">
            <div class="page-eyebrow">{eyebrow}</div>
            <h1 class="page-title">{title}</h1>
            <p class="page-subtitle">{subtitle}</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

def pulse_divider():
    """Display pulse divider."""
    st.markdown('<div class="pulse-divider">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</div>', unsafe_allow_html=True)

def require_login():
    if "current_user" not in st.session_state or not st.session_state.get("current_user"):
        st.error("Please log in first!")
        st.stop()

st.markdown(f'''
<div class="sidebar-brand">🧠 MindTrack</div>
<div class="sidebar-tagline">Wellness Intelligence</div>
''', unsafe_allow_html=True)

if "current_user" not in st.session_state:
    st.session_state.current_user = None

page = st.sidebar.radio("Navigation", [
    "🏠 Home",
    "📊 Assessment",
    "📈 Insights",
    "🔄 Recovery Patterns",
    "📖 Journal",
    "🗂️ My Entries",
    "🆘 Support & Coping",
    "📄 Report",
    "📊 Admin"
])

if st.session_state.current_user:
    st.sidebar.markdown(f"**👤 {st.session_state.current_user}**")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.current_user = None
        st.rerun()

st.sidebar.markdown('<div class="sidebar-disclaimer">MindTrack is a personal wellness reflection tool, not a diagnostic or treatment service.</div>', unsafe_allow_html=True)

if page == "🏠 Home":
    st.markdown('''
    <div class="hero-wrap">
        <div class="hero-icon">🧠</div>
        <h1 class="hero-title">MindTrack</h1>
        <p class="hero-tagline">Wellness Intelligence Platform</p>
    </div>
    ''', unsafe_allow_html=True)
    
    pulse_divider()
    
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("👤 Enter your name", placeholder="e.g., Alex Chen")
        if st.button("✨ Continue", use_container_width=True):
            if username:
                st.session_state.current_user = username
                st.rerun()
    
    with col2:
        st.info("🔐 No signup required—just enter your name to get started.")
    
    pulse_divider()
    
    st.markdown("### ✨ Features")
    feat_cols = st.columns(3)
    with feat_cols[0]:
        st.markdown("**📊 Smart Assessment**\nComprehensive wellness evaluation")
    with feat_cols[1]:
        st.markdown("**📈 Analytics**\nTrack trends & patterns over time")
    with feat_cols[2]:
        st.markdown("**🔄 Recovery Insights**\nUnderstand your recovery patterns")

elif page == "📊 Assessment":
    require_login()
    page_header("📊", "Your Wellness", "Quick Assessment", "Complete your wellness check-in with enhanced insights.")
    
    init_db()
    
    st.markdown("### Core Wellness Metrics")
    col1, col2 = st.columns(2)
    
    with col1:
        mood = st.select_slider("😊 How is your mood?", options=["😢 Very Low", "😞 Low", "😐 Neutral", "🙂 Good", "😄 Excellent"], value="😐 Neutral")
        stress_level = st.slider("😰 Stress Level (1-10)", 1, 10, 5, help="1=calm, 10=extremely stressed")
        anxiety_level = st.slider("😟 Anxiety Level (1-10)", 1, 10, 5)
    
    with col2:
        sleep_hours = st.slider("😴 Sleep Last Night (hours)", 0.0, 12.0, 7.0, step=0.5)
        exercise_minutes = st.slider("🏃 Exercise Today (minutes)", 0, 120, 30)
    
    pulse_divider()
    
    st.markdown("### 🆕 6 New Wellness Features (Added to Assessment)")
    st.caption("These 6 features aggregate into your overall wellness score alongside your core metrics.")
    
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.markdown("**1️⃣ Cognitive Clarity**")
        cognitive_clarity = st.slider(
            "Mental focus & clarity (0-100)",
            0, 100, 60,
            help="How sharp is your thinking? 0=foggy, 100=crystal clear"
        )
        st.caption(f"Score: {cognitive_clarity}/100")
    
    with feat_col2:
        st.markdown("**2️⃣ Emotional Stability**")
        emotional_stability = st.slider(
            "Emotional balance (0-100)",
            0, 100, 60,
            help="How stable are your emotions? 0=volatile, 100=very balanced"
        )
        st.caption(f"Score: {emotional_stability}/100")
    
    with feat_col3:
        st.markdown("**3️⃣ Social Connection**")
        social_connection = st.slider(
            "Sense of connection (0-100)",
            0, 100, 60,
            help="How connected do you feel? 0=isolated, 100=deeply connected"
        )
        st.caption(f"Score: {social_connection}/100")
    
    feat_col4, feat_col5, feat_col6 = st.columns(3)
    
    with feat_col4:
        st.markdown("**4️⃣ Physical Vitality**")
        physical_vitality = st.slider(
            "Energy & physical well-being (0-100)",
            0, 100, 60,
            help="How energetic do you feel? 0=exhausted, 100=full of energy"
        )
        st.caption(f"Score: {physical_vitality}/100")
    
    with feat_col5:
        st.markdown("**5️⃣ Stress Management**")
        stress_management = st.slider(
            "Ability to manage stress (0-100)",
            0, 100, 60,
            help="How well do you handle stress? 0=overwhelmed, 100=very capable"
        )
        st.caption(f"Score: {stress_management}/100")
    
    with feat_col6:
        st.markdown("**6️⃣ Overall Resilience**")
        resilience = st.slider(
            "Ability to bounce back (0-100)",
            0, 100, 60,
            help="How quickly do you recover from setbacks? 0=struggle, 100=very resilient"
        )
        st.caption(f"Score: {resilience}/100")
    
    pulse_divider()
    
    if st.button("💾 Save Assessment & Analyze", use_container_width=True):
        username = st.session_state.current_user
        
        # Average resilience with physical_vitality for additional weighting
        avg_new_features = (cognitive_clarity + emotional_stability + social_connection + physical_vitality + stress_management + resilience) / 6
        
        save_assessment_data(
            username, mood, stress_level, sleep_hours, anxiety_level, exercise_minutes,
            cognitive_clarity, emotional_stability, social_connection, physical_vitality, stress_management
        )
        
        risk, factors, wellness_score = predict_risk(
            stress_level, sleep_hours, anxiety_level, exercise_minutes, mood,
            cognitive_clarity, emotional_stability, social_connection, physical_vitality, stress_management
        )
        
        st.session_state.assessment_data = {
            "username": username,
            "mood": mood,
            "stress_level": stress_level,
            "sleep_hours": sleep_hours,
            "anxiety_level": anxiety_level,
            "exercise_minutes": exercise_minutes,
            "cognitive_clarity": cognitive_clarity,
            "emotional_stability": emotional_stability,
            "social_connection": social_connection,
            "physical_vitality": physical_vitality,
            "stress_management": stress_management,
            "resilience": resilience
        }
        
        st.success("✅ Assessment saved!")
        
        st.markdown("### 📊 Your Results")
        col_r1, col_r2, col_r3 = st.columns(3)
        
        with col_r1:
            st.metric("Wellness Score", f"{wellness_score:.0f}/100")
        with col_r2:
            risk_badge(risk)
        with col_r3:
            st.metric("Avg New Features", f"{avg_new_features:.0f}/100")
        
        st.markdown("### 🔍 Key Factors")
        for factor in factors:
            st.info(f"• {factor}")

elif page == "📈 Insights":
    require_login()
    page_header("📈", "Analytics", "Your Wellness Trends", "Visualize your progress over time.")
    
    username = st.session_state.current_user
    df = get_history_data()
    
    if df.empty:
        st.info("No assessment data yet. Complete an assessment to see insights!")
    else:
        mine = df[df["username"].astype(str) == username].sort_values("date")
        
        if mine.empty:
            st.info("No entries found for you yet.")
        else:
            st.markdown("### 📈 Wellness Score Over Time")
            fig = px.line(mine, x="date", y="wellness_score", markers=True, title="Wellness Trend")
            fig.update_layout(hovermode="x unified", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### 🎯 Key Metrics Distribution")
            metrics = ["stress_level", "sleep_hours", "anxiety_level", "exercise_minutes"]
            fig = px.box(mine, y=metrics, title="Metric Distributions")
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### 🆕 New Features Trend")
            if all(col in mine.columns for col in ["cognitive_clarity", "emotional_stability", "social_connection"]):
                fig = px.line(mine, x="date", y=["cognitive_clarity", "emotional_stability", "social_connection", "physical_vitality", "stress_management"], title="Feature Trends")
                st.plotly_chart(fig, use_container_width=True)

elif page == "🔄 Recovery Patterns":
    require_login()
    page_header("🔄", "Analysis", "Recovery Patterns", "Understand how you recover from stress and challenges.")
    
    username = st.session_state.current_user
    init_db()
    
    tab1, tab2, tab3 = st.tabs(["📊 Log Recovery", "📈 Analysis", "💡 Insights"])
    
    with tab1:
        st.markdown("### Record Your Recovery Journey")
        
        recovery_time = st.slider(
            "How long did recovery take? (hours)",
            0.0, 48.0, 4.0, step=0.5,
            help="Time from when you felt stressed/low to when you felt better"
        )
        
        triggers = st.multiselect(
            "What triggered the need for recovery?",
            ["Work stress", "Personal conflict", "Health issue", "Financial worry", "Sleep deprivation", "Overwork", "Social pressure", "Other"],
            default=["Work stress"]
        )
        triggers_str = ", ".join(triggers) if triggers else "Other"
        
        methods = st.multiselect(
            "What recovery methods did you use?",
            ["Sleep", "Exercise", "Meditation", "Social support", "Journaling", "Creative activity", "Time in nature", "Professional help", "Music", "Rest"],
            default=["Sleep"]
        )
        methods_str = ", ".join(methods) if methods else "Rest"
        
        effectiveness = st.slider(
            "How effective was your recovery? (1-10)",
            1, 10, 7,
            help="1=not effective, 10=very effective"
        )
        
        if st.button("💾 Save Recovery Pattern", use_container_width=True):
            save_recovery_pattern(username, recovery_time, triggers_str, methods_str, effectiveness)
            st.success("✅ Recovery pattern recorded!")
            st.rerun()
    
    with tab2:
        patterns = get_recovery_patterns(username)
        
        if patterns.empty:
            st.info("No recovery patterns recorded yet. Start by logging your recovery journey!")
        else:
            st.metric("Total Recovery Events Logged", len(patterns))
            avg_recovery_time = patterns["recovery_time_hours"].mean()
            avg_effectiveness = patterns["effectiveness_score"].mean()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Average Recovery Time", f"{avg_recovery_time:.1f} hours")
            with col2:
                st.metric("Average Effectiveness", f"{avg_effectiveness:.1f}/10")
            
            pulse_divider()
            
            st.markdown("### 📊 Recovery Timeline")
            fig = px.scatter(patterns, x="date", y="recovery_time_hours", color="effectiveness_score",
                           size="effectiveness_score", title="Recovery Time vs Effectiveness",
                           hover_data=["recovery_triggers", "recovery_methods"])
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### 📈 Effectiveness Over Time")
            fig = px.line(patterns, x="date", y="effectiveness_score", markers=True, title="Recovery Effectiveness Trend")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        patterns = get_recovery_patterns(username)
        
        if not patterns.empty:
            st.markdown("### 🎯 Your Recovery Profile")
            
            # Most common triggers
            all_triggers = []
            for t in patterns["recovery_triggers"]:
                all_triggers.extend([x.strip() for x in str(t).split(",")])
            trigger_counts = pd.Series(all_triggers).value_counts()
            
            st.markdown("**Most Common Triggers:**")
            for trigger, count in trigger_counts.head(5).items():
                st.write(f"• {trigger}: {count} times")
            
            pulse_divider()
            
            # Most common recovery methods
            all_methods = []
            for m in patterns["recovery_methods"]:
                all_methods.extend([x.strip() for x in str(m).split(",")])
            method_counts = pd.Series(all_methods).value_counts()
            
            st.markdown("**Most Effective Recovery Methods:**")
            for method, count in method_counts.head(5).items():
                st.write(f"• {method}: Used {count} times")
            
            pulse_divider()
            
            # Personalized recommendations
            st.markdown("### 💡 Personalized Recovery Recommendations")
            
            avg_time = patterns["recovery_time_hours"].mean()
            if avg_time > 12:
                st.warning("⏱️ Your average recovery time is longer than ideal. Consider diversifying your recovery methods.")
            elif avg_time < 3:
                st.success("⚡ You recover quickly! Continue what you're doing.")
            else:
                st.info("✅ Your recovery time is within a healthy range.")
            
            if avg_effectiveness < 5:
                st.error("⚠️ Your recovery methods aren't as effective as they could be. Try new approaches!")
            elif avg_effectiveness >= 8:
                st.success("🌟 Your recovery strategies are highly effective! Keep using them.")
            else:
                st.info("📌 There's room to optimize your recovery approach.")

elif page == "📖 Journal":
    require_login()
    page_header("📖", "Reflection", "Journal", "Write freely. Reflect deeply.")
    
    username = st.session_state.current_user
    init_db()
    
    st.markdown("### ✍️ What's on your mind today?")
    
    journal_text = st.text_area("Write your thoughts, feelings, or reflections...", height=250, placeholder="Start writing...")
    
    if st.button("💾 Save Entry", use_container_width=True):
        if journal_text.strip():
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO journal_entries (username, date, text)
            VALUES (?, ?, ?)
            """, (username, datetime.now(), journal_text))
            conn.commit()
            conn.close()
            st.success("✅ Journal entry saved!")
            st.rerun()
        else:
            st.warning("Please write something first.")
    
    pulse_divider()
    
    st.markdown("### 📚 Your Recent Entries")
    try:
        conn = get_connection()
        entries = pd.read_sql_query(
            "SELECT * FROM journal_entries WHERE username = ? ORDER BY date DESC LIMIT 10",
            (username,),
            con=conn
        )
        conn.close()
        
        if entries.empty:
            st.info("No journal entries yet. Start writing!")
        else:
            for _, row in entries.iterrows():
                with st.expander(f"📖 {row['date'].strftime('%Y-%m-%d %H:%M')}"):
                    st.write(row["text"])
                st.markdown("---")
    except:
        st.info("No entries yet.")

elif page == "🗂️ My Entries":
    require_login()
    page_header("🗂️", "Your Data", "My Entries", "Review, correct, or remove your own check-in history.")
    
    username = st.session_state.current_user
    df = get_history_data()
    
    if df.empty:
        st.info("No entries found yet.")
    else:
        mine = df[df["username"].astype(str) == username].sort_values("date", ascending=False)
        
        if mine.empty:
            st.info("No entries found for you yet.")
        else:
            st.caption(f"{len(mine)} entries found.")
            for _, row in mine.iterrows():
                c1, c2, c3, c4, c5 = st.columns([2, 1.2, 1, 1.2, 0.8])
                c1.markdown(f"**{row['date'].strftime('%Y-%m-%d %H:%M')}**")
                c2.write(f"Mood: {row['mood']}")
                c3.write(f"😴 {row['sleep_hours']:.0f}h")
                c4.write(f"Wellness: {row['wellness_score']:.0f}/100")

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
    st.info("**Outside the US** — search \"[your country] crisis helpline\" or contact local emergency services.")

elif page == "📄 Report":
    require_login()
    page_header("📄", "Documentation", "Health Report", "A shareable summary of your latest assessment.")
    
    if 'assessment_data' not in st.session_state:
        st.warning("⚠️ Please complete the Assessment first!")
    else:
        data = st.session_state['assessment_data']
        username = data["username"]
        
        risk, factors, wellness_score = predict_risk(
            data["stress_level"], data["sleep_hours"], data["anxiety_level"],
            data["exercise_minutes"], data["mood"],
            data["cognitive_clarity"], data["emotional_stability"],
            data["social_connection"], data["physical_vitality"], data["stress_management"]
        )
        recommendations = get_recommendations(
            data["stress_level"], data["sleep_hours"],
            data["anxiety_level"], data["exercise_minutes"]
        )
        
        st.markdown("## 📋 Report Preview")
        st.markdown(f"**👤 Username:** {username}")
        risk_badge(risk)
        
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("🏆 Wellness Score", f"{wellness_score}/100")
        with col_r2:
            st.metric("🧠 Cognitive Clarity", f"{data['cognitive_clarity']}/100")
        with col_r3:
            st.metric("❤️ Emotional Stability", f"{data['emotional_stability']}/100")
        
        st.markdown("## 🔍 Key Factors")
        for factor in factors:
            st.info(f"• {factor}")
        
        st.markdown("## 💡 Recommendations")
        for rec in recommendations:
            st.success(rec)

elif page == "📊 Admin":
    require_login()
    page_header("📊", "Back Office", "Admin Dashboard", "Manage and export the underlying data.")
    
    init_db()
    
    st.markdown("## 📁 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            conn = get_connection()
            df_history = pd.read_sql_query("SELECT * FROM user_history", conn)
            conn.close()
            st.markdown("### 👥 User History Data")
            st.dataframe(df_history, use_container_width=True)
            st.metric("Total Entries", len(df_history))
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
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    pulse_divider()
    
    st.markdown("### 🔄 Recovery Patterns Data")
    try:
        conn = get_connection()
        df_recovery = pd.read_sql_query("SELECT * FROM recovery_patterns", conn)
        conn.close()
        if not df_recovery.empty:
            st.dataframe(df_recovery, use_container_width=True)
            st.metric("Total Recovery Events", len(df_recovery))
    except Exception as e:
        st.error(f"❌ Error: {e}")
