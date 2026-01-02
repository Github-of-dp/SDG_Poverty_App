from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import numpy as np

app = Flask(__name__)

# ---------------- DATA + MODEL ----------------
# Expanded dataset for more realistic training (example values)
data = pd.DataFrame([
    # India
    [5000, 2, 0, 1], [10000, 5, 0, 1], [20000, 8, 1, 0], [40000, 12, 1, 0], [80000, 16, 1, 0],
    # USA
    [10000, 5, 0, 1], [30000, 8, 1, 0], [60000, 12, 1, 0], [100000, 16, 1, 0],
    # UK
    [12000, 5, 0, 1], [25000, 8, 1, 0], [50000, 12, 1, 0], [90000, 16, 1, 0],
    # UAE
    [20000, 5, 0, 1], [40000, 8, 1, 0], [80000, 12, 1, 0], [150000, 16, 1, 0],
    # Nigeria
    [3000, 2, 0, 1], [6000, 5, 0, 1], [15000, 8, 1, 0], [30000, 12, 1, 0],
    # Brazil
    [5000, 2, 0, 1], [10000, 5, 0, 1], [25000, 8, 1, 0], [50000, 12, 1, 0]
], columns=["income","education","employment","poverty_risk"])

X = data[["income", "education", "employment"]]
y = data["poverty_risk"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = LogisticRegression()
model.fit(X_scaled, y)

# ---------------- COUNTRY NORMALIZATION ----------------
COUNTRY_INCOME_INDEX = {
    "India": 1.0,
    "USA": 1.0,
    "UK": 1.0,
    "UAE": 1.0,
    "Nigeria": 1.0,
    "Brazil": 1.0
}

GLOBAL_AVG_INDEX = 1.0

# ---------------- HELP SUGGESTIONS ----------------
HELP_SUGGESTIONS = {
    "India": "Explore government welfare schemes, skill development programs, and local NGOs.",
    "USA": "Look into SNAP benefits, job reskilling programs, and community support services.",
    "UK": "Check Universal Credit support and employment training programs.",
    "UAE": "Explore workforce upskilling initiatives and social support entities.",
    "Nigeria": "Seek NGO assistance, microfinance programs, and vocational training.",
    "Brazil": "Look into Bolsa Família programs and employment support services."
}

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    income = float(request.form["income"])
    education = float(request.form["education"])
    employment = int(request.form["employment"])
    country = request.form["country"]

    # ---------------- COUNTRY NORMALIZATION ----------------
    index = COUNTRY_INCOME_INDEX.get(country, 1.0)
    normalized_income = income * index

    # ---------------- MODEL PREDICTION ----------------
    features = scaler.transform([[normalized_income, education, employment]])
    probability = model.predict_proba(features)[0][1]
    risk_percent = round(probability * 100, 2)

    # ---------------- MANUAL RULE-BASED BOOST ----------------
    if normalized_income > 50000 and education >= 12 and employment == 1:
        risk_percent = min(risk_percent, 5)
    elif normalized_income > 30000 and education >= 10 and employment == 1:
        risk_percent = min(risk_percent, 15)

    # ---------------- RISK LABEL ----------------
    if risk_percent < 35:
        level = "Low"
        color = "#22c55e"  # green
    elif risk_percent < 65:
        level = "Medium"
        color = "#facc15"  # yellow
    else:
        level = "High"
        color = "#ef4444"  # red

    # ---------------- GLOBAL COMPARISON ----------------
    comparison = (
        "Below global average" if index < GLOBAL_AVG_INDEX else
        "Near global average" if index == GLOBAL_AVG_INDEX else
        "Above global average"
    )

    help_text = HELP_SUGGESTIONS.get(country, "Seek local community and educational support.")

    return jsonify({
        "risk": risk_percent,
        "level": level,
        "color": color,
        "comparison": comparison,
        "help": help_text
    })

if __name__ == "__main__":
    app.run(debug=True)
