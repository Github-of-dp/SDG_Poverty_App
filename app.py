from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# ---------------- DATA + MODEL ----------------
data = pd.read_csv("poverty_data.csv")

X = data[["income", "education", "employment"]]
y = data["poverty_risk"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = LogisticRegression()
model.fit(X_scaled, y)

# ---------------- COUNTRY NORMALIZATION ----------------
# Average monthly income in local currency used as reference
COUNTRY_INCOME_INDEX = {
    "India": 15000,     # INR
    "USA": 3000,        # USD
    "UK": 2500,         # GBP
    "UAE": 5000,        # AED
    "Nigeria": 60000,   # NGN
    "Brazil": 2000      # BRL
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

    # ---------------- Country normalization ----------------
    country_ref = COUNTRY_INCOME_INDEX.get(country, 15000)
    normalized_income = income / country_ref  # income as fraction of avg income

    # ---------------- Rule-based base risk ----------------
    if normalized_income <= 0:
        base_risk = 100
    elif normalized_income < 0.2:
        base_risk = 90
    elif normalized_income < 0.5:
        base_risk = 75
    elif normalized_income < 0.8:
        base_risk = 50
    elif normalized_income < 1.0:
        base_risk = 35
    else:
        base_risk = 20

    # ---------------- Model adjustment ----------------
    # Use model to adjust risk slightly based on education & employment
    # income set to 1 so that model adjustment is small
    features = scaler.transform([[1, education, employment]])
    model_adj = model.predict_proba(features)[0][1] * 10  # small contribution

    risk_percent = min(100, round(base_risk + model_adj, 2))

    # ---------------- Risk label & color ----------------
    if risk_percent < 35:
        level = "Low"
        color = "green"
    elif risk_percent < 65:
        level = "Medium"
        color = "orange"
    else:
        level = "High"
        color = "red"

    # Global comparison
    comparison = (
        "Below global average" if normalized_income < GLOBAL_AVG_INDEX else
        "Near global average" if normalized_income == GLOBAL_AVG_INDEX else
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
    app.run()
