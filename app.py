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

# ---------------- COUNTRY & CURRENCY ----------------
CURRENCY_TO_USD = {
    "India": 0.012,    # INR to USD
    "USA": 1.0,        # USD
    "UK": 1.25,        # GBP to USD
    "UAE": 0.27,       # AED to USD
    "Nigeria": 0.0026, # NGN to USD
    "Brazil": 0.20     # BRL to USD
}

POVERTY_LINE_USD = {
    "India": 2000,
    "USA": 13000,
    "UK": 16000,
    "UAE": 22000,
    "Nigeria": 600,
    "Brazil": 2500
}

HELP_SUGGESTIONS = {
    "India": "Explore government welfare schemes, skill development programs, and local NGOs.",
    "USA": "Look into SNAP benefits, job reskilling programs, and community support services.",
    "UK": "Check Universal Credit support and employment training programs.",
    "UAE": "Explore workforce upskilling initiatives and social support entities.",
    "Nigeria": "Seek NGO assistance, microfinance programs, and vocational training.",
    "Brazil": "Look into Bolsa Família programs and employment support services."
}

GLOBAL_AVG_INDEX = 1.0

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    # ---- Fetch inputs ----
    income_local = float(request.form["income"])
    education = float(request.form["education"])
    employment = int(request.form["employment"])
    country = request.form["country"]

    # ---- Convert income to USD ----
    conversion_rate = CURRENCY_TO_USD.get(country, 1.0)
    income_usd = income_local * conversion_rate
    poverty_threshold = POVERTY_LINE_USD.get(country, 10000)

    # ---- Manual rule-based risk ----
    income_ratio = income_usd / poverty_threshold
    if income_ratio < 1:
        base_risk = 80 + (1 - income_ratio) * 20   # Boost if below poverty line
    else:
        base_risk = max(0, 50 - (income_ratio - 1) * 30)  # Lower risk for higher income

    # ---- Adjust with education & employment ----
    risk_percent = base_risk - (education * 2) - (employment * 10)
    risk_percent = max(0, min(100, risk_percent))

    # ---- Risk label & color ----
    if risk_percent < 35:
        level = "Low"
        color = "green"
    elif risk_percent < 65:
        level = "Medium"
        color = "orange"
    else:
        level = "High"
        color = "red"

    # ---- Global comparison ----
    comparison = (
        "Below global average" if income_ratio < GLOBAL_AVG_INDEX else
        "Near global average" if income_ratio == GLOBAL_AVG_INDEX else
        "Above global average"
    )

    help_text = HELP_SUGGESTIONS.get(country, "Seek local community and educational support.")

    return jsonify({
        "risk": round(risk_percent, 2),
        "level": level,
        "color": color,
        "comparison": comparison,
        "help": help_text
    })

if __name__ == "__main__":
    app.run()
