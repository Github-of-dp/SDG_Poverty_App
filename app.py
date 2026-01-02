from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ---------------- COUNTRY NORMALIZATION + POVERTY LINE ----------------
COUNTRY_INCOME_INDEX = {
    "India": 0.013,      # 1 INR = 0.013 USD
    "USA": 1.0,          # USD
    "UK": 1.22,          # 1 GBP = 1.22 USD
    "UAE": 0.27,         # 1 AED = 0.27 USD
    "Nigeria": 0.0022,   # 1 NGN = 0.0022 USD
    "Brazil": 0.19       # 1 BRL = 0.19 USD
}

POVERTY_LINE_USD = {
    "India": 200,        
    "USA": 1500,
    "UK": 1400,
    "UAE": 1600,
    "Nigeria": 100,
    "Brazil": 300
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
    income_local = float(request.form["income"])
    education = float(request.form["education"])
    employment = int(request.form["employment"])
    country = request.form["country"]

    # Convert local currency to USD
    conversion_rate = COUNTRY_INCOME_INDEX.get(country, 1.0)
    income_usd = income_local * conversion_rate
    poverty_threshold = POVERTY_LINE_USD.get(country, 1000)

    # ---------------- REALISTIC RISK FORMULA ----------------
    # If income < poverty line -> high risk
    if income_usd < poverty_threshold:
        # Scale from 90-100% as income drops far below poverty line
        deficit_ratio = (poverty_threshold - income_usd) / poverty_threshold
        base_risk = 90 + 10 * min(deficit_ratio, 1.0)
    else:
        # Income above poverty line -> low risk scaling 0-50%
        excess_ratio = min(income_usd - poverty_threshold, poverty_threshold) / poverty_threshold
        base_risk = max(0, 50 - 50 * excess_ratio)

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
