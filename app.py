import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import random
from datetime import datetime
from textblob import TextBlob
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import io

# Page Configuration
st.set_page_config(page_title="Mental Health Risk Analysis", page_icon="🧠", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 50%, #ffecd2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 50%, #ffecd2 100%);
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .css-1d391kg {
        padding-top: 0;
    }
    .stMetric {
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(0,0,0,0.1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .feature-card {
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid rgba(0,0,0,0.1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
    }
    h1, h2, h3 {
        color: #2d3748 !important;
    }
    .stMarkdown, .stMarkdown p {
        color: #4a5568 !important;
    }
    .css-16huue1, .css-10trblm, .css-1c7yx88 {
        color: #2d3748 !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    .sidebar .sidebar-content {
        background: rgba(255,255,255,0.05);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 15px 30px;
        font-weight: bold;
        font-size: 1.1em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def ensure_data_files_exist():
    filenames = [
        "mental_health_dataset.xlsx",
        "user_history.xlsx",
        "predictions.xlsx"
    ]
    for filename in filenames:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            if filename == "user_history.xlsx":
                df = pd.DataFrame(columns=["username", "date", "mood", "sleep_hours", "stress_level", "anxiety_level", "exercise_minutes"])
                df.to_excel(filepath, index=False)
            elif filename == "predictions.xlsx":
                df = pd.DataFrame(columns=["username", "date", "risk_level", "wellness_score", "factors"])
                df.to_excel(filepath, index=False)
            else:
                pd.DataFrame().to_excel(filepath, index=False)

def save_user_history(username, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes):
    ensure_data_files_exist()
    filepath = os.path.join(DATA_DIR, "user_history.xlsx")
    try:
        df = pd.read_excel(filepath)
    except:
        df = pd.DataFrame(columns=["username", "date", "mood", "sleep_hours", "stress_level", "anxiety_level", "exercise_minutes"])
    new_entry = pd.DataFrame([{
        "username": username,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mood": mood,
        "sleep_hours": sleep_hours,
        "stress_level": stress_level,
        "anxiety_level": anxiety_level,
        "exercise_minutes": exercise_minutes
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_excel(filepath, index=False)
    return new_entry

def save_prediction(username, risk_level, wellness_score, factors):
    ensure_data_files_exist()
    filepath = os.path.join(DATA_DIR, "predictions.xlsx")
    try:
        df = pd.read_excel(filepath)
    except:
        df = pd.DataFrame(columns=["username", "date", "risk_level", "wellness_score", "factors"])
    new_prediction = pd.DataFrame([{
        "username": username,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "risk_level": risk_level,
        "wellness_score": wellness_score,
        "factors": str(factors)
    }])
    df = pd.concat([df, new_prediction], ignore_index=True)
    df.to_excel(filepath, index=False)
    return new_prediction

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
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30, alignment=1)
    story.append(Paragraph("Mental Health Report", title_style))
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Heading2'], fontSize=16, spaceAfter=20)
    story.append(Paragraph(f"For: {username}", subtitle_style))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
    story.append(Spacer(1, 20))
    info_style = ParagraphStyle('CustomInfo', parent=styles['Normal'], fontSize=12, spaceAfter=12)
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
    doc.build(story)
    buffer.seek(0)
    return buffer

def export_to_excel(df, sheet_name="Data"):
    """Convert a DataFrame into an in-memory Excel file (.xlsx) ready for download.
    Used to let users export their patient/history data straight from the UI."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    buffer.seek(0)
    return buffer

def mood_to_score(series):
    mood_map = {"Very Bad": 1, "Bad": 2, "Neutral": 3, "Good": 4, "Very Good": 5}
    return series.map(mood_map)

def get_history_data():
    history_path = os.path.join(DATA_DIR, "user_history.xlsx")
    if not os.path.exists(history_path):
        return pd.DataFrame()
    try:
        df = pd.read_excel(history_path)
    except Exception:
        return pd.DataFrame()
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
    predictions_path = os.path.join(DATA_DIR, "predictions.xlsx")
    if not os.path.exists(predictions_path):
        return pd.DataFrame()
    try:
        df = pd.read_excel(predictions_path)
    except Exception:
        return pd.DataFrame()
    if df.empty:
        return df
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    risk_map = {"Low": 1, "Medium": 2, "High": 3}
    df["risk_num"] = df["risk_level"].map(risk_map)
    return df.dropna(subset=["date"])

def style_plot(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.35)",
        font={"color": "#2d3748"},
        margin=dict(l=20, r=20, t=50, b=20),
    )
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
    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name="Wellness Profile",
            line_color="#667eea",
            fillcolor="rgba(102,126,234,0.30)",
        )
    )
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(color="#2d3748")),
            angularaxis=dict(tickfont=dict(color="#2d3748")),
        ),
        showlegend=False,
    )
    return style_plot(fig)

def create_factor_bar(stress, sleep, anxiety, exercise):
    categories = ["Stress", "Sleep", "Anxiety", "Exercise"]
    actual_values = [stress, sleep, anxiety, exercise]
    healthy_targets = [3, 8, 3, 45]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Your Values", x=categories, y=actual_values, marker_color="#667eea"))
    fig.add_trace(go.Bar(name="Healthy Target", x=categories, y=healthy_targets, marker_color="#00cc96"))
    fig.update_layout(barmode="group", title="Your Wellness Factors vs Healthy Targets")
    return style_plot(fig)

# Sidebar navigation
st.sidebar.markdown("# 🧭 Navigation")

# Handle quick navigation from home page
if 'nav_to' in st.session_state:
    if st.session_state['nav_to'] == 'assessment':
        page = "📋 Assessment"
    elif st.session_state['nav_to'] == 'journal':
        page = "📝 Journal"
    del st.session_state['nav_to']
else:
    page = st.sidebar.radio(
        "Go to",
        ["🏠 Home", "📋 Assessment", "🤖 Risk Prediction", "📂 Bulk Upload", "📈 Dashboard", "📝 Journal", "📄 Report", "📊 Admin"],
        label_visibility="collapsed"
    )

# Home Page
if page == "🏠 Home":
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h1 style="font-size: 4em; margin-bottom: 0;">🧠</h1>
        <h1 style="font-size: 3em; margin-top: 0;">Mental Health Risk Analysis</h1>
        <p style="font-size: 1.3em; opacity: 0.9;">Your personal wellness companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("## ⚡ Quick Start")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Start New Assessment", use_container_width=True):
            st.session_state['nav_to'] = 'assessment'
            st.rerun()
    with col2:
        if st.button("📝 Write in Journal", use_container_width=True):
            st.session_state['nav_to'] = 'journal'
            st.rerun()
    
    st.markdown("---")
    
    # Stats Preview
    history_path = os.path.join(DATA_DIR, "user_history.xlsx")
    if os.path.exists(history_path):
        try:
            df = pd.read_excel(history_path)
            if len(df) > 0:
                st.markdown("## 📊 Your Stats")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Assessments", len(df))
                m2.metric("Avg Sleep", f"{df['sleep_hours'].mean():.1f}h")
                m3.metric("Avg Stress", f"{df['stress_level'].mean():.1f}")
                m4.metric("Last Entry", df['date'].iloc[-1][:10])
                st.markdown("---")
        except:
            pass
    
    # Daily Wellness Tips
    wellness_tips = [
        "Take a 5-minute walk outside 🌳",
        "Practice deep breathing for 2 minutes 🧘",
        "Drink a glass of water 💧",
        "Call a friend or family member 📞",
        "Write down 3 things you're grateful for ✍️",
        "Stretch your body for 10 minutes 🤸",
        "Listen to your favorite song 🎵",
        "Take a short break from screens 📵"
    ]
    st.markdown("## 🌟 Daily Wellness Tip")
    st.info(random.choice(wellness_tips))
    
    st.markdown("---")
    
    # Motivational Quote
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
    st.title("📋 Mental Health Assessment")
    st.markdown("---")
    
    username = st.text_input("👤 Enter your name", "Guest User")
    
    st.markdown("## Answer the following questions:")
    
    # Mood selection with emojis
    mood_emojis = {"Very Bad": "😢", "Bad": "😔", "Neutral": "😐", "Good": "😊", "Very Good": "😄"}
    mood = st.select_slider(
        "How is your mood today?",
        options=["Very Bad", "Bad", "Neutral", "Good", "Very Good"],
        value="Good",
        format_func=lambda x: f"{mood_emojis[x]} {x}"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        sleep_hours = st.slider("😴 How many hours did you sleep last night?", 0, 12, 7)
        stress_level = st.slider("😰 How stressed are you? (0-10)", 0, 10, 3)
    with col2:
        anxiety_level = st.slider("😟 How anxious are you? (0-10)", 0, 10, 3)
        exercise_minutes = st.slider("🏃 How many minutes did you exercise today?", 0, 180, 30)
    
    # Quick preview of wellness score
    preview_score = calculate_wellness_score(stress_level, sleep_hours, anxiety_level, exercise_minutes)
    st.metric("Preview Wellness Score", f"{preview_score}/100")
    
    if st.button("✅ Submit Assessment"):
        entry = save_user_history(username, mood, sleep_hours, stress_level, anxiety_level, exercise_minutes)
        st.session_state['assessment_data'] = {
            "username": username,
            "mood": mood,
            "sleep_hours": sleep_hours,
            "stress_level": stress_level,
            "anxiety_level": anxiety_level,
            "exercise_minutes": exercise_minutes
        }
        st.success("🎉 Assessment saved successfully!")

# Risk Prediction Page
elif page == "🤖 Risk Prediction":
    st.title("🤖 Mental Health Risk Prediction")
    st.markdown("---")
    
    if 'assessment_data' not in st.session_state:
        st.warning("⚠️ Please complete the Assessment first!")
    else:
        data = st.session_state['assessment_data']
        stress = data["stress_level"]
        sleep = data["sleep_hours"]
        anxiety = data["anxiety_level"]
        exercise = data["exercise_minutes"]
        mood = data["mood"]
        username = data["username"]
        
        risk, factors, wellness_score = predict_risk(stress, sleep, anxiety, exercise, mood)
        recommendations = get_recommendations(stress, sleep, anxiety, exercise)
        
        # Gauge chart for wellness score
        st.markdown("## 📊 Prediction Results")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=wellness_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Wellness Score", 'font': {'size': 24, 'color': '#2d3748'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#2d3748"},
                'bar': {'color': "#00cc96"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "#2d3748",
                'steps': [
                    {'range': [0, 40], 'color': "#ef553b"},
                    {'range': [40, 70], 'color': "#ffaa00"},
                    {'range': [70, 100], 'color': "#00cc96"}
                ],
            }
        ))
        fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "#2d3748"})
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if risk == "Low":
                st.success(f"🎯 Risk Level: **{risk}**")
            elif risk == "Medium":
                st.warning(f"⚠️ Risk Level: **{risk}**")
            else:
                st.error(f"🚨 Risk Level: **{risk}**")
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

# Bulk Upload Page
elif page == "📂 Bulk Upload":
    st.title("📂 Bulk Upload & Analyze")
    st.markdown("---")
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
            label="📥 Download Template (Excel)",
            data=export_to_excel(template_df, sheet_name="Template"),
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
                    fig_risk = px.bar(
                        risk_counts, x="Risk", y="Count", color="Risk",
                        title="Risk Level Distribution",
                        color_discrete_map={"Low": "#00b894", "Medium": "#fdcb6e", "High": "#d63031"},
                    )
                    st.plotly_chart(style_plot(fig_risk), use_container_width=True)
                with c2:
                    fig_hist = px.histogram(bulk_df, x="wellness_score", nbins=15, title="Wellness Score Distribution")
                    st.plotly_chart(style_plot(fig_hist), use_container_width=True)

                st.markdown("### 📥 Export or Save")
                dl_col, save_col = st.columns(2)
                with dl_col:
                    st.download_button(
                        label="📥 Download Analyzed Results (Excel)",
                        data=export_to_excel(bulk_df, sheet_name="Bulk Analysis"),
                        file_name=f"bulk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                with save_col:
                    if st.button("➕ Add these records to the backend data", use_container_width=True):
                        ensure_data_files_exist()
                        history_path = os.path.join(DATA_DIR, "user_history.xlsx")
                        predictions_path = os.path.join(DATA_DIR, "predictions.xlsx")

                        try:
                            existing_history = pd.read_excel(history_path)
                        except Exception:
                            existing_history = pd.DataFrame(columns=["username", "date", "mood", "sleep_hours", "stress_level", "anxiety_level", "exercise_minutes"])
                        history_to_add = bulk_df[["username", "date", "mood", "sleep_hours", "stress_level", "anxiety_level", "exercise_minutes"]]
                        pd.concat([existing_history, history_to_add], ignore_index=True).to_excel(history_path, index=False)

                        try:
                            existing_predictions = pd.read_excel(predictions_path)
                        except Exception:
                            existing_predictions = pd.DataFrame(columns=["username", "date", "risk_level", "wellness_score", "factors"])
                        predictions_to_add = bulk_df[["username", "date", "risk_level", "wellness_score", "factors"]]
                        pd.concat([existing_predictions, predictions_to_add], ignore_index=True).to_excel(predictions_path, index=False)

                        st.success(f"✅ Added {len(bulk_df)} records to the backend. They'll now show up in Dashboard and Admin.")

# Dashboard Page
elif page == "📈 Dashboard":
    st.title("📈 Analytics Dashboard")
    st.markdown("---")

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
                    fig_mood = px.line(
                        filtered_df.sort_values("date"),
                        x="date",
                        y="mood_num",
                        markers=True,
                        title="Mood Over Time",
                        color_discrete_sequence=["#00b894"],
                    )
                    fig_mood.update_traces(line_shape=line_shape)
                    st.plotly_chart(style_plot(fig_mood), use_container_width=True)

                with col2:
                    fig_sleep = px.area(
                        filtered_df.sort_values("date"),
                        x="date",
                        y="sleep_hours",
                        title="Sleep Pattern",
                        color_discrete_sequence=["#6c5ce7"],
                    )
                    st.plotly_chart(style_plot(fig_sleep), use_container_width=True)

                col3, col4 = st.columns(2)
                with col3:
                    fig_stress = px.line(
                        filtered_df.sort_values("date"),
                        x="date",
                        y="stress_level",
                        markers=True,
                        title="Stress Trend",
                        color_discrete_sequence=["#e17055"],
                    )
                    fig_stress.update_traces(line_shape=line_shape)
                    st.plotly_chart(style_plot(fig_stress), use_container_width=True)

                with col4:
                    fig_exercise = px.bar(
                        filtered_df.sort_values("date"),
                        x="date",
                        y="exercise_minutes",
                        title="Exercise Activity",
                        color="exercise_minutes",
                        color_continuous_scale="Tealgrn",
                    )
                    st.plotly_chart(style_plot(fig_exercise), use_container_width=True)

                fig_wellness = px.line(
                    filtered_df.sort_values("date"),
                    x="date",
                    y="wellness_score",
                    markers=True,
                    title="Overall Wellness Score Trend",
                    color_discrete_sequence=["#0984e3"],
                )
                fig_wellness.update_traces(line_shape=line_shape)
                st.plotly_chart(style_plot(fig_wellness), use_container_width=True)

            with dist_tab:
                col1, col2 = st.columns(2)

                with col1:
                    mood_counts = filtered_df["mood"].value_counts().reset_index()
                    mood_counts.columns = ["Mood", "Count"]
                    fig_mood_dist = px.pie(
                        mood_counts,
                        names="Mood",
                        values="Count",
                        hole=0.55,
                        title="Mood Distribution",
                        color_discrete_sequence=px.colors.qualitative.Set3,
                    )
                    st.plotly_chart(style_plot(fig_mood_dist), use_container_width=True)

                with col2:
                    fig_sleep_box = px.box(
                        filtered_df,
                        y="sleep_hours",
                        points="all",
                        title="Sleep Variability",
                        color_discrete_sequence=["#6c5ce7"],
                    )
                    st.plotly_chart(style_plot(fig_sleep_box), use_container_width=True)

                col3, col4 = st.columns(2)
                with col3:
                    fig_scatter = px.scatter(
                        filtered_df,
                        x="sleep_hours",
                        y="stress_level",
                        size="exercise_minutes",
                        color="wellness_score",
                        hover_data=["username", "mood"],
                        title="Sleep vs Stress vs Exercise",
                        color_continuous_scale="Viridis",
                    )
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
                            fig_risk = px.bar(
                                risk_counts,
                                x="Risk",
                                y="Count",
                                color="Risk",
                                title="Risk Level Distribution",
                                color_discrete_map={"Low": "#00b894", "Medium": "#fdcb6e", "High": "#d63031"},
                            )
                            st.plotly_chart(style_plot(fig_risk), use_container_width=True)
                        else:
                            st.info("No prediction records available for the selected filters.")
                    else:
                        st.info("No prediction records available yet.")

            with insights_tab:
                corr_df = filtered_df[["sleep_hours", "stress_level", "anxiety_level", "exercise_minutes", "mood_num", "wellness_score"]].corr()
                heatmap = go.Figure(
                    data=go.Heatmap(
                        z=corr_df.values,
                        x=corr_df.columns,
                        y=corr_df.index,
                        colorscale="RdYlGn",
                        zmin=-1,
                        zmax=1,
                        text=np.round(corr_df.values, 2),
                        texttemplate="%{text}",
                    )
                )
                heatmap.update_layout(title="Correlation Heatmap")
                st.plotly_chart(style_plot(heatmap), use_container_width=True)

                last_row = filtered_df.sort_values("date").iloc[-1]
                radar_col, info_col = st.columns([1.2, 1])
                with radar_col:
                    st.plotly_chart(
                        create_wellness_radar(
                            last_row["sleep_hours"],
                            last_row["stress_level"],
                            last_row["anxiety_level"],
                            last_row["exercise_minutes"],
                            last_row["mood"],
                        ),
                        use_container_width=True,
                    )
                with info_col:
                    st.markdown("### Latest Snapshot")
                    st.metric("Latest Wellness", f"{last_row['wellness_score']:.0f}/100")
                    st.metric("Latest Mood", last_row["mood"])
                    st.metric("Latest Stress", f"{last_row['stress_level']}/10")
                    st.metric("Latest Anxiety", f"{last_row['anxiety_level']}/10")

# Journal Page
elif page == "📝 Journal":
    st.title("📝 Journal & Sentiment Analysis")
    st.markdown("---")
    
    st.write("Write about your day and we'll analyze your mood!")
    journal_text = st.text_area("Your Journal Entry:", height=250, placeholder="How was your day? What made you happy or worried?")
    
    if st.button("🔍 Analyze Sentiment"):
        if journal_text:
            sentiment, polarity = analyze_sentiment(journal_text)
            
            st.markdown("## 📊 Sentiment Analysis Results")
            col1, col2 = st.columns(2)
            
            with col1:
                if sentiment == "positive":
                    st.success(f"Sentiment: **Positive** 😊")
                elif sentiment == "negative":
                    st.error(f"Sentiment: **Negative** 😔")
                else:
                    st.info(f"Sentiment: **Neutral** 😐")
            
            with col2:
                # Visual polarity meter
                fig_polarity = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=polarity,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Polarity", 'font': {'size': 20, 'color': '#2d3748'}},
                    gauge={
                        'axis': {'range': [-1, 1], 'tickwidth': 1, 'tickcolor': "#2d3748"},
                        'bar': {'color': "#636efa"},
                        'bgcolor': "rgba(0,0,0,0)",
                        'borderwidth': 2,
                        'bordercolor': "#2d3748",
                        'steps': [
                            {'range': [-1, -0.1], 'color': "#ef553b"},
                            {'range': [-0.1, 0.1], 'color': "#ffaa00"},
                            {'range': [0.1, 1], 'color': "#00cc96"}
                        ]
                    }
                ))
                fig_polarity.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "#2d3748"})
                st.plotly_chart(fig_polarity, use_container_width=True)
            
            st.markdown("### 📝 Your Entry:")
            st.write(journal_text)
        else:
            st.warning("⚠️ Please write something in your journal first!")

# Report Page
elif page == "📄 Report":
    st.title("📄 Health Report")
    st.markdown("---")
    
    if 'assessment_data' not in st.session_state:
        st.warning("⚠️ Please complete the Assessment first!")
    else:
        data = st.session_state['assessment_data']
        username = data["username"]
        stress = data["stress_level"]
        sleep = data["sleep_hours"]
        anxiety = data["anxiety_level"]
        exercise = data["exercise_minutes"]
        mood = data["mood"]
        
        risk, factors, wellness_score = predict_risk(stress, sleep, anxiety, exercise, mood)
        recommendations = get_recommendations(stress, sleep, anxiety, exercise)
        
        st.markdown("## 📋 Report Preview")
        
        st.markdown(f"**👤 Username:** {username}")
        if risk == "Low":
            st.success(f"🎯 Risk Level: **{risk}**")
        elif risk == "Medium":
            st.warning(f"⚠️ Risk Level: **{risk}**")
        else:
            st.error(f"🚨 Risk Level: **{risk}**")
        st.metric("🏆 Wellness Score", f"{wellness_score}/100")
        
        st.markdown("## 🔍 Key Factors")
        for factor in factors:
            st.info(f"• {factor}")
        
        st.markdown("## 💡 Recommendations")
        for rec in recommendations:
            st.success(rec)
        
        pdf_buffer = generate_pdf_report(username, risk, wellness_score, factors, recommendations)
        
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name=f"mental_health_report_{username}.pdf",
            mime="application/pdf"
        )

# Admin Page
elif page == "📊 Admin":
    st.title("📊 Admin Dashboard")
    st.markdown("---")
    
    st.markdown("## 📁 Data Management")
    history_path = os.path.join(DATA_DIR, "user_history.xlsx")
    predictions_path = os.path.join(DATA_DIR, "predictions.xlsx")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if os.path.exists(history_path):
            try:
                df_history = pd.read_excel(history_path)
                st.markdown("### 👥 User History Data")
                st.dataframe(df_history, use_container_width=True)
                st.metric("Total Entries", len(df_history))
                st.download_button(
                    label="📥 Download Patient History (Excel)",
                    data=export_to_excel(df_history, sheet_name="Patient History"),
                    file_name=f"patient_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            st.info("📭 User history file not found.")
    
    with col2:
        if os.path.exists(predictions_path):
            try:
                df_predictions = pd.read_excel(predictions_path)
                st.markdown("### 🤖 Predictions Data")
                st.dataframe(df_predictions, use_container_width=True)
                st.metric("Total Predictions", len(df_predictions))
                st.download_button(
                    label="📥 Download Predictions (Excel)",
                    data=export_to_excel(df_predictions, sheet_name="Predictions"),
                    file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            st.info("📭 Predictions file not found.")
