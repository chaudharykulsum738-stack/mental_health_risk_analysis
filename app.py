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

# ---------------------------------------------------------------------------
# Design tokens — calm clinical-trust palette. Risk colors carry real
# meaning wherever they appear (gauges, badges, charts, goal deltas).
# ---------------------------------------------------------------------------
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
</style>
""", unsafe_allow_html=True)


def pulse_divider():
    """Signature section break: a thin ECG-style pulse line."""
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
    """Create the SQL tables if they don't exist yet. Safe to call repeatedly."""
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



# ---------------------------------------------------------------------------
# Login / Session Management
# ---------------------------------------------------------------------------

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
    # Use a flag to trigger navigation on next rerun instead of touching widget key
    st.session_state["needs_nav_home"] = True

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
    """Returns (current_streak, longest_streak) in consecutive days, given a
    list of date objects (duplicates/unsorted are fine)."""
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
    """Average wellness score for the trailing 7 days vs the 7 days before that."""
    today = datetime.now().date()
    this_week = df[df["date"].dt.date >= today - timedelta(days=6)]
    last_week = df[(df["date"].dt.date >= today - timedelta(days=13)) &
                   (df["date"].dt.date <= today - timedelta(days=7))]
    this_avg = this_week["wellness_score"].mean() if not this_week.empty else None
    last_avg = last_week["wellness_score"].mean() if not last_week.empty else None
    return this_avg, last_avg

def trend_nudge(df):
    """Gentle, non-diagnostic signal: last 3 entries trending down and low."""
    d = df.sort_values("date")
    if len(d) < 3:
        return False
    recent = d.tail(3)["wellness_score"].tolist()
    return recent[0] > recent[1] > recent[2] and recent[2] < 40

def create_mood_calendar(df, weeks=12):
    """GitHub-style contribution calendar, colored by average daily mood."""
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

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
# The radio widget always renders and owns its own session_state key
# ("page_radio"), so Streamlit persists the selection across every rerun.
# Quick-nav buttons set that same key BEFORE the widget is instantiated
# rather than bypassing it -- this is what stops the app from snapping back
# to "Home" the moment you touch a slider on another page.
PAGES = [
    "🏠 Home", "📋 Assessment", "🤖 Risk Prediction", "🎯 Goals",
    "📂 Bulk Upload", "📈 Dashboard", "📝 Journal", "🗂️ My Entries",
    "🆘 Support & Coping", "📄 Report", "📊 Admin"
]

st.sidebar.markdown("""
<div class="sidebar-brand">🧠 MindTrack</div>
<div class="sidebar-tagline">Wellness Intelligence</div>
""", unsafe_allow_html=True)

# Handle post-logout navigation (must happen BEFORE radio widget renders)
if st.session_state.get("needs_nav_home"):
    st.session_state["page_radio"] = "🏠 Home"
    del st.session_state["needs_nav_home"]

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

# Home Page
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
        "Write down 3 things you're grateful for ✍️", "Stretch your body for 10 minutes 🤸",
        "Listen to your favorite song 🎵", "Take a short break from screens 📵"
    ]
    st.markdown("## 🌟 Daily Wellness Tip")
    st.info(random.choice(wellness_tips))

    pulse_divider()
    quotes = [
        "“The greatest glory in living lies not in never falling, but in rising every time we fall.” – Nelson Mandela",
        "“The way to get started is to quit talking and begin doing.” – Walt Disney",
        "“Your time is limited, don't waste it living someone else's life.” – Steve Jobs",
        "“The future belongs to those who believe in the beauty of their dreams.” – Eleanor Roosevelt",
        "“It does not matter how slowly you go as long as you do not stop.” – Confucius"
    ]
    st.markdown("## 💬 Motivation")
    st.success(random.choice(quotes))

# Assessment Page
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

    preview_score = calculate_wellness_score(stress_level, sleep_hours, anxiety_level, exercise_minutes)
    st.metric("Preview Wellness Score", f"{preview_score}/100")

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

# Risk Prediction Page
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

# Goals Page
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

# Bulk Upload Page
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

# Dashboard Page
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

# Journal Page
elif page == "📝 Journal":
    require_login()
    page_header("📝", "Reflection", "Journal & Sentiment Analysis", "Write about your day and we'll analyze your mood.")
    journal_text = st.text_area("Your Journal Entry:", height=250, placeholder="How was your day? What made you happy or worried?")

    if st.button("🔍 Analyze Sentiment"):
        if journal_text:
            sentiment, polarity = analyze_sentiment(journal_text)
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

            if sentiment == "negative" and polarity < -0.4:
                pulse_divider()
                st.info(
                    "That sounds like a heavy day. Writing it down is a good step — "
                    "if it would help, the **Support & Coping** page has grounding techniques and resources."
                )
        else:
            st.warning("⚠️ Please write something in your journal first!")

# My Entries Page
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

# Support & Coping Page
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
    st.caption(
        "MindTrack is a self-reflection tool, not a diagnostic service or emergency line. "
        "If you are in immediate danger, please contact local emergency services right away."
    )

# Report Page
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

# Admin Page
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
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
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
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
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
