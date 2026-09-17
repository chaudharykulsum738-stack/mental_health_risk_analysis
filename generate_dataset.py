"""
Synthetic Mental Health Risk dataset generator.

Creates a realistic labeled dataset for training an ML classifier that
predicts mental-health risk (Low / Moderate / High) from survey answers.

Features are grounded in validated clinical questionnaires (PHQ-9, GAD-7)
and known psychosocial risk factors from the literature.

Run:  python generate_dataset.py
Output: mental_health_data.csv  (2000 rows, 16 columns)
"""

import numpy as np
import pandas as pd

RNG = np.random.default_rng(seed=42)
N = 2000


def clip(x, lo, hi):
    return np.clip(x, lo, hi)


# ---------- Demographics ----------
age = RNG.integers(16, 65, size=N)
gender = RNG.choice(["Male", "Female", "Other"], size=N, p=[0.48, 0.48, 0.04])
occupation = RNG.choice(
    ["Student", "Employed", "Unemployed", "Self-Employed", "Retired"],
    size=N,
    p=[0.30, 0.45, 0.10, 0.10, 0.05],
)

# ---------- Lifestyle ----------
sleep_hours = clip(RNG.normal(7.0, 1.6, N), 2, 12).round(1)
physical_activity_hours = clip(RNG.normal(3.0, 2.5, N), 0, 20).round(1)
screen_time_hours = clip(RNG.normal(6.0, 3.0, N), 0, 16).round(1)
work_study_hours = clip(RNG.normal(8.0, 2.5, N), 0, 16).round(1)

# ---------- Psychosocial ----------
stress_level = RNG.integers(1, 11, size=N)                # 1..10
social_support = RNG.integers(1, 11, size=N)              # 1..10
mood_score = RNG.integers(1, 11, size=N)                  # 1..10 (higher = better mood)
energy_level = RNG.integers(1, 11, size=N)                # 1..10
concentration_difficulty = RNG.integers(1, 11, size=N)    # 1..10 (higher = worse)
hopelessness = RNG.integers(1, 11, size=N)                # 1..10 (higher = worse)

appetite_change = RNG.choice([0, 1], size=N, p=[0.55, 0.45])
previous_mh_history = RNG.choice([0, 1], size=N, p=[0.75, 0.25])
family_history = RNG.choice([0, 1], size=N, p=[0.70, 0.30])
alcohol_use = RNG.choice([0, 1, 2], size=N, p=[0.45, 0.40, 0.15])  # none/occasional/regular

# ---------- Compute a latent risk score ----------
# Weights loosely follow clinical intuition:
#   worse sleep, high stress, low support, low mood, high hopelessness -> higher risk
sleep_penalty = np.where(
    sleep_hours < 6, (6 - sleep_hours) * 1.2,
    np.where(sleep_hours > 9, (sleep_hours - 9) * 0.6, 0.0),
)

risk = (
    1.6 * stress_level
    + 1.4 * hopelessness
    + 1.2 * concentration_difficulty
    + 1.0 * (10 - mood_score)
    + 0.9 * (10 - energy_level)
    + 0.9 * (10 - social_support)
    + 1.1 * sleep_penalty
    + 0.4 * (screen_time_hours - 6)
    - 0.6 * physical_activity_hours
    + 2.2 * previous_mh_history
    + 1.4 * family_history
    + 1.0 * alcohol_use
    + 1.3 * appetite_change
    + RNG.normal(0, 2.0, N)  # noise
)

# Bucket into Low / Moderate / High using quantiles for balanced classes
q1, q2 = np.quantile(risk, [0.40, 0.75])
risk_level = np.where(risk < q1, "Low",
              np.where(risk < q2, "Moderate", "High"))

df = pd.DataFrame({
    "age": age,
    "gender": gender,
    "occupation": occupation,
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
    "appetite_change": appetite_change,
    "previous_mh_history": previous_mh_history,
    "family_history": family_history,
    "alcohol_use": alcohol_use,
    "risk_level": risk_level,
})

df.to_csv("mental_health_data.csv", index=False)
print(f"Saved mental_health_data.csv  shape={df.shape}")
print("\nClass balance:")
print(df["risk_level"].value_counts())
print("\nPreview:")
print(df.head())
