"""
Mental Health Risk Analysis — Streamlit App
Author: enhanced by Emergent E1

Four features in one file:
  1. Risk Predictor       — Random Forest on synthetic clinical data
  2. Journal & Sentiment  — TextBlob mood tracker + trend chart
  3. Clinical Screening   — PHQ-9 (depression) + GAD-7 (anxiety)
  4. AI Companion         — rule-based supportive chatbot with crisis detection
"""

from __future__ import annotations

import os
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from textblob import TextBlob


# ─────────────────────────  PAGE CONFIG + THEME  ──────────────────────────
st.set_page_config(
    page_title="Mental Health Risk Analysis",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
  :root {
    --sage:   #6B9080;
    --sage2:  #A4C3B2;
    --cream:  #F6FFF8;
    --peach:  #EAAC8B;
    --deep:   #354F52;
  }
  .stApp { background: linear-gradient(180deg,#F6FFF8 0%,#EAF4EA 100%); }
  h1, h2, h3 { color: var(--deep); font-family: 'Georgia', serif; }
  .hero {
      background: linear-gradient(120deg,#6B9080,#A4C3B2);
      color:#fff; padding:28px 32px; border-radius:18px;
      box-shadow: 0 6px 24px rgba(53,79,82,.15);
      margin-bottom: 18px;
  }
  .hero h1 { color:#fff !important; margin:0 0 6px; font-size: 2.1rem; }
  .hero p  { color:#F6FFF8; margin:0; opacity:.95;}
  .metric-card{
      background:#fff;border-radius:14px;padding:16px 18px;
      box-shadow:0 3px 10px rgba(53,79,82,.08);
      border-left:5px solid var(--sage);
  }
  .risk-low   { color:#2E7D32; font-weight:700; }
  .risk-mod   { color:#EF6C00; font-weight:700; }
  .risk-high  { color:#C62828; font-weight:700; }
  .stButton>button{
      background:var(--sage); color:#fff; border:0; border-radius:10px;
      padding:.55rem 1.2rem; font-weight:600;
  }
  .stButton>button:hover{ background:var(--deep); color:#fff; }
  .bubble-user{
      background:#DDE7DE;padding:10px 14px;border-radius:14px 14px 2px 14px;
      margin:6px 0 6px 22%;display:inline-block;max-width:78%;
  }
  .bubble-bot{
      background:#fff;padding:10px 14px;border-radius:14px 14px 14px 2px;
      margin:6px 22% 6px 0;display:inline-block;max-width:78%;
      border-left:4px solid var(--sage);
  }
  .crisis-box{
      background:#FFF3F0;border:2px solid #C62828;border-radius:12px;
      padding:14px 18px;margin:10px 0;color:#7A0C0C;
  }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
      <h1>🧠 Mental Health Risk Analysis</h1>
      <p>A caring companion powered by machine learning, clinical screeners, and sentiment analysis. Not a substitute for professional care.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────  DATA + MODEL (cached)  ─────────────────────────
DATA_PATH = "mental_health_data.csv"
CATEGORICAL = ["gender", "occupation"]


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        st.error(
            f"Dataset file '{DATA_PATH}' not found. "
            "Please add it to the repo root (run generate_dataset.py)."
        )
        st.stop()
    return pd.read_csv(DATA_PATH)


@st.cache_resource(show_spinner="Training risk model…")
def train_model(df: pd.DataFrame):
    df = df.copy()
    encoders: dict[str, LabelEncoder] = {}
    for col in CATEGORICAL:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    y = df["risk_level"]
    X = df.drop(columns=["risk_level"])

    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = RandomForestClassifier(
        n_estimators=300, max_depth=12, random_state=42, n_jobs=-1
    )
    model.fit(Xtr, ytr)
    acc = accuracy_score(yte, model.predict(Xte))
    importances = pd.Series(
        model.feature_importances_, index=X.columns
    ).sort_values(ascending=False)
    return model, encoders, X.columns.tolist(), acc, importances


df = load_data()
model, encoders, feature_order, model_acc, feat_importances = train_model(df)


# ─────────────────────────  SIDEBAR  ───────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    page = st.radio(
        "Go to",
        ["Risk Predictor", "Journal & Mood", "Clinical Screening", "AI Companion", "About Data"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("#### 📊 Model")
    st.metric("Accuracy (holdout)", f"{model_acc*100:.1f}%")
    st.caption(f"Trained on {len(df):,} samples")
    st.markdown("---")
    st.markdown("#### ☎️ Crisis Support")
    st.caption(
        "**India:** iCall +91-9152987821  \n"
        "**Vandrevala:** 1860-2662-345  \n"
        "**US:** 988  •  **UK:** 116 123"
    )


# ═════════════════════════  TAB 1 — RISK PREDICTOR  ═══════════════════════
def page_predictor():
    st.subheader("🔮 Personal Risk Assessment")
    st.write(
        "Fill in the questionnaire below. The trained Random Forest model will "
        "estimate your mental-health risk and show which factors influenced it."
    )

    with st.form("risk_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Age", 16, 65, 25)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            occupation = st.selectbox(
                "Occupation",
                ["Student", "Employed", "Unemployed", "Self-Employed", "Retired"],
            )
            sleep_hours = st.slider("Sleep hours / night", 2.0, 12.0, 7.0, 0.1)
            physical_activity_hours = st.slider(
                "Physical activity (hrs / week)", 0.0, 20.0, 3.0, 0.5
            )
            screen_time_hours = st.slider("Screen time (hrs / day)", 0.0, 16.0, 6.0, 0.5)
        with c2:
            work_study_hours = st.slider("Work / study hrs / day", 0.0, 16.0, 8.0, 0.5)
            stress_level = st.slider("Stress level", 1, 10, 5)
            social_support = st.slider("Social support", 1, 10, 6)
            mood_score = st.slider("Current mood (higher = better)", 1, 10, 6)
            energy_level = st.slider("Energy level", 1, 10, 6)
        with c3:
            concentration_difficulty = st.slider("Concentration difficulty", 1, 10, 4)
            hopelessness = st.slider("Feelings of hopelessness", 1, 10, 3)
            appetite_change = st.radio("Recent appetite change?", ["No", "Yes"], horizontal=True)
            previous_mh_history = st.radio(
                "Previous mental-health diagnosis?", ["No", "Yes"], horizontal=True
            )
            family_history = st.radio("Family mental-health history?", ["No", "Yes"], horizontal=True)
            alcohol_use = st.selectbox("Alcohol use", ["None", "Occasional", "Regular"])

        submitted = st.form_submit_button("Analyze my risk", use_container_width=True)

    if not submitted:
        return

    row = {
        "age": age,
        "gender": encoders["gender"].transform([gender])[0],
        "occupation": encoders["occupation"].transform([occupation])[0],
        "sleep_hours": sleep_hours,
        "physical_activity_hours": physical_activity_hours,
        "screen_time_hours": screen_time_hours,
        "work_study_hours": work_study_hours,
        "stress_level": stress_level,
        "social_support": social_support,
        "mood_score": mood_score,
        "energy_level": energy_level,
        "concentration_difficulty": concentration_difficulty,
        "hopelessness": hopelessness,
        "appetite_change": 1 if appetite_change == "Yes" else 0,
        "previous_mh_history": 1 if previous_mh_history == "Yes" else 0,
        "family_history": 1 if family_history == "Yes" else 0,
        "alcohol_use": ["None", "Occasional", "Regular"].index(alcohol_use),
    }
    x = pd.DataFrame([row])[feature_order]
    pred = model.predict(x)[0]
    proba = dict(zip(model.classes_, model.predict_proba(x)[0]))

    label_class = {"Low": "risk-low", "Moderate": "risk-mod", "High": "risk-high"}[pred]
    top_conf = proba[pred] * 100

    lc, rc = st.columns([1.1, 1])
    with lc:
        st.markdown(
            f"<div class='metric-card'><h3>Predicted Risk Level</h3>"
            f"<div style='font-size:2.4rem' class='{label_class}'>{pred}</div>"
            f"<div>Confidence: <b>{top_conf:.1f}%</b></div></div>",
            unsafe_allow_html=True,
        )
        # gauge
        gauge_val = {"Low": 25, "Moderate": 60, "High": 90}[pred]
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=gauge_val,
            number={"suffix": " / 100"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#354F52"},
                "steps": [
                    {"range": [0, 40], "color": "#B5E48C"},
                    {"range": [40, 75], "color": "#F9DC5C"},
                    {"range": [75, 100], "color": "#F28482"},
                ],
            },
            title={"text": "Risk score"},
        ))
        gauge.update_layout(height=280, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(gauge, use_container_width=True)

    with rc:
        st.markdown("#### Class probabilities")
        pdf = pd.DataFrame({"Risk": list(proba.keys()),
                            "Probability": [v * 100 for v in proba.values()]})
        fig = px.bar(pdf, x="Risk", y="Probability", color="Risk",
                     color_discrete_map={"Low": "#6B9080", "Moderate": "#EAAC8B", "High": "#C62828"},
                     text=pdf["Probability"].round(1).astype(str) + "%")
        fig.update_layout(height=280, showlegend=False, margin=dict(l=10, r=10, t=10, b=10),
                          yaxis_title="%", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 🧩 Top factors influencing your prediction")
    top = feat_importances.head(8).reset_index()
    top.columns = ["Feature", "Importance"]
    fig2 = px.bar(top, x="Importance", y="Feature", orientation="h",
                  color="Importance", color_continuous_scale="Teal")
    fig2.update_layout(height=340, yaxis={"categoryorder": "total ascending"},
                       margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)

    # Personalized suggestions
    tips = []
    if sleep_hours < 6:      tips.append("😴 Aim for 7–9 hrs of sleep — consistent bedtime helps.")
    if stress_level >= 7:    tips.append("🧘 Try 10 min of breathing or meditation each day.")
    if physical_activity_hours < 2: tips.append("🚶 Add a 20-min walk 3× a week.")
    if social_support <= 4:  tips.append("💬 Reach out to one person you trust this week.")
    if hopelessness >= 7 or mood_score <= 3:
        tips.append("🤝 Please consider talking to a mental-health professional.")
    if not tips:
        tips.append("🌱 You're doing well — keep up your healthy routines!")
    st.markdown("#### 💡 Personalized suggestions")
    for t in tips:
        st.write("- " + t)


# ═════════════════════════  TAB 2 — JOURNAL & MOOD  ═══════════════════════
def page_journal():
    st.subheader("📝 Daily Journal & Mood Tracker")
    st.write("Write about your day. We'll analyse the sentiment and plot your mood trend.")

    if "journal" not in st.session_state:
        st.session_state.journal = []  # list of dicts

    entry = st.text_area("How are you feeling today?", height=140,
                         placeholder="Today I felt…")
    if st.button("Save entry"):
        if entry.strip():
            blob = TextBlob(entry)
            polarity = blob.sentiment.polarity        # -1..1
            subjectivity = blob.sentiment.subjectivity
            mood = round((polarity + 1) * 5, 2)       # 0..10
            st.session_state.journal.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "text": entry.strip(),
                "polarity": round(polarity, 3),
                "subjectivity": round(subjectivity, 3),
                "mood_0_10": mood,
            })
            st.success("Entry saved.")
        else:
            st.warning("Write something first 🙂")

    if not st.session_state.journal:
        st.info("Your journal is empty. Save your first entry above.")
        return

    j = pd.DataFrame(st.session_state.journal)

    c1, c2, c3 = st.columns(3)
    c1.metric("Entries", len(j))
    c2.metric("Avg mood (0–10)", f"{j['mood_0_10'].mean():.2f}")
    last_trend = "→"
    if len(j) >= 2:
        delta = j["mood_0_10"].iloc[-1] - j["mood_0_10"].iloc[-2]
        last_trend = "↑ Better" if delta > 0.2 else ("↓ Lower" if delta < -0.2 else "→ Stable")
    c3.metric("Latest trend", last_trend)

    fig = px.line(j, x="time", y="mood_0_10", markers=True,
                  title="Mood trend over time", range_y=[0, 10])
    fig.update_traces(line_color="#6B9080")
    fig.add_hline(y=5, line_dash="dot", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)

    # crisis keywords
    crisis_kw = ["suicide", "kill myself", "end my life", "hopeless", "worthless",
                 "self harm", "cutting", "no reason to live"]
    text_all = " ".join(j["text"].tolist()).lower()
    hits = [k for k in crisis_kw if k in text_all]
    if hits:
        st.markdown(
            f"<div class='crisis-box'>⚠️ Concerning words detected in your entries "
            f"({', '.join(hits)}). Please reach out to someone you trust or a helpline "
            f"listed in the sidebar. You matter. 💚</div>", unsafe_allow_html=True)

    with st.expander("📖 See all my entries"):
        st.dataframe(j[::-1], use_container_width=True, hide_index=True)


# ═════════════════════════  TAB 3 — CLINICAL SCREENING  ═══════════════════
PHQ9_Q = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling / staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself — or that you're a failure",
    "Trouble concentrating on things",
    "Moving or speaking slowly — or being fidgety / restless",
    "Thoughts that you would be better off dead or hurting yourself",
]
GAD7_Q = [
    "Feeling nervous, anxious, or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless it's hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid something awful might happen",
]
OPTS = {
    "Not at all": 0, "Several days": 1, "More than half the days": 2, "Nearly every day": 3
}


def phq9_severity(s):
    if s <= 4:  return "Minimal", "#2E7D32"
    if s <= 9:  return "Mild", "#66BB6A"
    if s <= 14: return "Moderate", "#FBC02D"
    if s <= 19: return "Moderately Severe", "#EF6C00"
    return "Severe", "#C62828"


def gad7_severity(s):
    if s <= 4:  return "Minimal", "#2E7D32"
    if s <= 9:  return "Mild", "#66BB6A"
    if s <= 14: return "Moderate", "#EF6C00"
    return "Severe", "#C62828"


def _run_screener(title, questions, key_prefix, sev_fn, max_score):
    st.markdown(f"### {title}")
    st.caption("Over the last 2 weeks, how often have you been bothered by…")
    scores = []
    for i, q in enumerate(questions):
        choice = st.radio(f"{i+1}. {q}", list(OPTS.keys()),
                          key=f"{key_prefix}_{i}", horizontal=True, index=0)
        scores.append(OPTS[choice])
    total = sum(scores)
    label, color = sev_fn(total)
    st.markdown(
        f"<div class='metric-card'><b>Score:</b> {total} / {max_score} — "
        f"<span style='color:{color};font-weight:700'>{label}</span></div>",
        unsafe_allow_html=True,
    )
    g = go.Figure(go.Indicator(
        mode="gauge+number", value=total,
        gauge={"axis": {"range": [0, max_score]}, "bar": {"color": color}},
        title={"text": f"{title} score"},
    ))
    g.update_layout(height=260, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(g, use_container_width=True)
    return total, label


def page_screening():
    st.subheader("🏥 Clinical Screening (PHQ-9 & GAD-7)")
    st.write("These are the standard tools used in clinics worldwide — for screening only, not diagnosis.")
    left, right = st.columns(2)
    with left:
        _run_screener("PHQ-9 (Depression)", PHQ9_Q, "phq", phq9_severity, 27)
    with right:
        _run_screener("GAD-7 (Anxiety)", GAD7_Q, "gad", gad7_severity, 21)

    st.info("If your scores are Moderate or higher, please consider consulting a mental-health "
            "professional. The helplines in the sidebar can help you get started.")


# ═════════════════════════  TAB 4 — AI COMPANION  ═════════════════════════
CRISIS_WORDS = ["suicide", "kill myself", "end my life", "want to die",
                "self harm", "cutting myself", "no reason to live"]

RESPONSES = {
    "sad": [
        "I hear you, and I'm sorry you're feeling this way. Would you like to talk about what triggered it?",
        "It sounds heavy. Remember — feelings pass. What's one small thing that usually brings you a bit of comfort?",
    ],
    "anxious": [
        "That anxious feeling can be exhausting. Try breathing in for 4, hold 4, out 6 — three times. I'll wait.",
        "Anxiety often shrinks when we name what's beneath it. What worry is loudest right now?",
    ],
    "angry": [
        "It's okay to feel angry. Would it help to write down what triggered it?",
        "Anger often protects a softer feeling underneath — sadness, fear, hurt. Does anything come to mind?",
    ],
    "happy": [
        "That's wonderful to hear! What made today feel good?",
        "Love that. Savor the moment — small joys are the antidote to burnout.",
    ],
    "tired": [
        "Being tired is a signal, not a weakness. What's one thing you can drop today?",
        "Rest is productive. Can you carve out 15 min just for yourself?",
    ],
    "lonely": [
        "Loneliness is hard. Is there one person you could message — even a small hello?",
        "You're not alone in feeling alone. I'm here to listen.",
    ],
    "default": [
        "Thank you for sharing that with me. Can you tell me a little more?",
        "I'm listening. How has this been affecting your day?",
        "That sounds important. What would feel supportive right now?",
    ],
}

EMOTION_KEYWORDS = {
    "sad":     ["sad", "cry", "down", "depressed", "unhappy", "miserable", "empty"],
    "anxious": ["anxious", "worry", "panic", "nervous", "stressed", "overwhelmed", "scared"],
    "angry":   ["angry", "furious", "mad", "irritated", "annoyed", "hate"],
    "happy":   ["happy", "great", "good", "wonderful", "excited", "grateful", "joy"],
    "tired":   ["tired", "exhausted", "drained", "burned out", "no energy"],
    "lonely":  ["lonely", "alone", "isolated", "no friends", "nobody"],
}


def detect_emotion(text: str) -> str:
    t = text.lower()
    for emo, words in EMOTION_KEYWORDS.items():
        if any(w in t for w in words):
            return emo
    # fall back to polarity
    pol = TextBlob(text).sentiment.polarity
    if pol < -0.2:  return "sad"
    if pol >  0.2:  return "happy"
    return "default"


def companion_reply(text: str) -> tuple[str, bool]:
    low = text.lower()
    if any(w in low for w in CRISIS_WORDS):
        return (
            "I'm really glad you told me. Your safety matters most right now. "
            "Please reach out immediately — in India call **iCall +91-9152987821** or "
            "**Vandrevala 1860-2662-345**. In the US dial **988**. You are not alone. 💚",
            True,
        )
    emo = detect_emotion(text)
    bank = RESPONSES.get(emo, RESPONSES["default"])
    idx = len(text) % len(bank)  # deterministic variety
    return bank[idx], False


def page_companion():
    st.subheader("💬 Supportive Companion")
    st.caption("A gentle, rule-based listener. Not a therapist — but always here.")

    if "chat" not in st.session_state:
        st.session_state.chat = [
            ("bot", "Hi 👋 I'm here to listen. How are you feeling today?", False)
        ]

    for who, msg, crisis in st.session_state.chat:
        cls = "bubble-user" if who == "user" else "bubble-bot"
        st.markdown(f"<div class='{cls}'>{msg}</div>", unsafe_allow_html=True)
        if crisis:
            st.markdown(
                "<div class='crisis-box'>⚠️ Crisis language detected — please see helplines in the sidebar.</div>",
                unsafe_allow_html=True,
            )

    user_msg = st.chat_input("Type your message…")
    if user_msg:
        st.session_state.chat.append(("user", user_msg, False))
        reply, crisis = companion_reply(user_msg)
        st.session_state.chat.append(("bot", reply, crisis))
        st.rerun()

    if st.button("🔄 Reset conversation"):
        st.session_state.chat = [
            ("bot", "Hi 👋 I'm here to listen. How are you feeling today?", False)
        ]
        st.rerun()


# ═════════════════════════  TAB 5 — ABOUT DATA  ═══════════════════════════
def page_about():
    st.subheader("📊 About the training data")
    st.write(
        f"The Random Forest was trained on **{len(df):,}** synthetic samples "
        "grounded in validated clinical questionnaires (PHQ-9, GAD-7) "
        "and known psychosocial risk factors."
    )

    c1, c2 = st.columns(2)
    with c1:
        counts = df["risk_level"].value_counts().reset_index()
        counts.columns = ["risk_level", "count"]
        fig = px.pie(counts, names="risk_level", values="count", hole=0.5,
                     color="risk_level",
                     color_discrete_map={"Low": "#6B9080", "Moderate": "#EAAC8B", "High": "#C62828"},
                     title="Risk-level distribution")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.histogram(df, x="stress_level", color="risk_level", nbins=10,
                           color_discrete_map={"Low": "#6B9080", "Moderate": "#EAAC8B", "High": "#C62828"},
                           title="Stress level by risk group")
        st.plotly_chart(fig, use_container_width=True)

    fig = px.box(df, x="risk_level", y="sleep_hours", color="risk_level",
                 color_discrete_map={"Low": "#6B9080", "Moderate": "#EAAC8B", "High": "#C62828"},
                 title="Sleep hours by risk group")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 🌟 Feature importance (from Random Forest)")
    fi = feat_importances.reset_index()
    fi.columns = ["Feature", "Importance"]
    fig = px.bar(fi, x="Importance", y="Feature", orientation="h",
                 color="Importance", color_continuous_scale="Teal")
    fig.update_layout(height=520, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Preview training data"):
        st.dataframe(df.head(50), use_container_width=True, hide_index=True)


# ─────────────────────────  ROUTER  ────────────────────────────────────────
PAGES = {
    "Risk Predictor":     page_predictor,
    "Journal & Mood":     page_journal,
    "Clinical Screening": page_screening,
    "AI Companion":       page_companion,
    "About Data":         page_about,
}
PAGES[page]()

st.markdown("---")
st.caption(
    "⚠️ This tool provides educational information and self-reflection support only. "
    "It is **not** a medical diagnosis. If you are struggling, please contact a licensed "
    "mental-health professional or one of the helplines listed in the sidebar."
)
