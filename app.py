from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ---------------- COUNTRY DATA ----------------
POVERTY_LINE = {
    "India": 10000,    # monthly income in local currency
    "USA": 1500,
    "UK": 1400,
    "UAE": 6000,
    "Nigeria": 120,
    "Brazil": 400
}

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
    income = max(0, float(request.form["income"]))
    education = float(request.form.get("education", 0))
    employment = int(request.form.get("employment", 0))
    household_size = int(request.form.get("household_size", 1))
    working_members = int(request.form.get("working_members", 1))
    country = request.form.get("country", "India")

    poverty_line = POVERTY_LINE.get(country, 10000)

    # ---------------- RULE-BASED RISK ----------------
    # Base poverty risk based on income vs country poverty line
    if income >= poverty_line:
        base_risk = max(10, 30 - (income - poverty_line)*0.001)
    else:
        deficit_ratio = (poverty_line - income) / poverty_line
        base_risk = 90 * deficit_ratio + 10

    # Household modifier
    household_factor = max(1, household_size / working_members)
    base_risk *= household_factor

    # Education/Employment modifier
    modifier = education*1.5 + employment*5
    if base_risk > 50:
        risk_percent = max(base_risk - modifier, 50)
    else:
        risk_percent = max(base_risk - modifier, 10)
    risk_percent = min(100, max(0, risk_percent))

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

    comparison = "Below global average" if income < poverty_line else "Above global average"
    help_text = HELP_SUGGESTIONS.get(country, "Seek local support programs.")

    return jsonify({
        "risk": round(risk_percent,2),
        "level": level,
        "color": color,
        "comparison": comparison,
        "help": help_text
    })

if __name__ == "__main__":
    app.run(debug=True)
