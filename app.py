from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ---------------- COUNTRY POVERTY LINES (Monthly Income in Local Currency) ----------------
POVERTY_LINE = {
    "India": 10000,
    "USA": 15000,
    "UK": 14000,
    "UAE": 16000,
    "Nigeria": 1200
}

# ---------------- HELP TEXTS ----------------
HELP_SUGGESTIONS = {
    "India": "Explore government welfare schemes, skill development programs, and local NGOs.",
    "USA": "Look into SNAP benefits, job reskilling programs, and community support services.",
    "UK": "Check Universal Credit support and employment training programs.",
    "UAE": "Explore workforce upskilling initiatives and social support entities.",
    "Nigeria": "Seek NGO assistance, microfinance programs, and vocational training."
}

# ---------------- PREDICTION LOGIC ----------------
def calculate_risk(income, education, employment, household_size, working_members, country):
    poverty_line = POVERTY_LINE.get(country, 10000)
    income = max(0, income)
    household_ratio = working_members / max(1, household_size)  # fraction of working members
    
    # ---------------- RULE-BASED POVERTY RISK ----------------
    if income >= poverty_line:
        base_risk = max(10, 30 - (income - poverty_line) * 0.001)
    else:
        deficit_ratio = (poverty_line - income) / poverty_line
        base_risk = 90 * deficit_ratio + 10

    # Modify based on education and employment
    modifier = education * 1.5 + employment * 5 + household_ratio * 10
    if base_risk > 50:
        risk_percent = max(base_risk - modifier, 50)  # can't go below 50 if income low
    else:
        risk_percent = max(base_risk - modifier, 10)
    
    # Clamp final risk
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
    
    # Global comparison
    comparison = "Above global average" if income >= poverty_line else "Below global average"
    help_text = HELP_SUGGESTIONS.get(country, "Seek local community and educational support.")
    
    return round(risk_percent, 2), level, color, comparison, help_text

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.form
    income = float(data.get("income", 0))
    education = float(data.get("education", 0))
    employment = int(data.get("employment", 0))
    household_size = int(data.get("household_size", 1))
    working_members = int(data.get("working_members", 0))
    country = data.get("country", "India")
    
    risk, level, color, comparison, help_text = calculate_risk(
        income, education, employment, household_size, working_members, country
    )
    
    return jsonify({
        "risk": risk,
        "level": level,
        "color": color,
        "comparison": comparison,
        "help": help_text
    })

if __name__ == "__main__":
    app.run(debug=True)