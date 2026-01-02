from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

# ---------------- DATA + HELP ----------------
COUNTRY_INCOME_INDEX = {
    "India": 0.013,      # 1 INR = 0.013 USD
    "USA": 1.0,          # USD
    "UK": 1.22,          # 1 GBP = 1.22 USD
    "UAE": 0.27,         # 1 AED = 0.27 USD
    "Nigeria": 0.0022,   # 1 NGN = 0.0022 USD
    "Brazil": 0.19       # 1 BRL = 0.19 USD
}

POVERTY_LINE_USD = {
    "India": 200,        # monthly USD equivalent
    "USA": 1500,
    "UK": 1400,
    "UAE": 1600,
    "Nigeria": 100,
    "Brazil": 300
}

GLOBAL_AVG_INDEX = 1.0

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
    income_local = float(request.form["income"])
    education = float(request.form["education"])
    employment = int(request.form["employment"])
    country = request.form["country"]

    # Convert local currency to USD
    conversion_rate = COUNTRY_INCOME_INDEX.get(country, 1.0)
    income_usd = income_local * conversion_rate
    poverty_threshold = POVERTY_LINE_USD.get(country, 1000)

    # ---------------- Better rule-based risk calculation ----------------
    if income_usd < poverty_threshold:
        # Below poverty line: high risk
        base_risk = 50 + 50 * (1 - income_usd / poverty_threshold)
    else:
        # Above poverty line: low risk
        excess = min(income_usd - poverty_threshold, poverty_threshold)
        base_risk = 50 - 45 * (excess / poverty_threshold)

    # Adjust for education and employment
    risk_percent = base_risk - (education * 2) - (employment * 10)
    risk_percent = max(0, min(100, risk_percent))

    # Risk label & color
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
    income_ratio = income_usd / poverty_threshold
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
    app.run(debug=True)
