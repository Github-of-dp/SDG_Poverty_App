from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ---------------- COUNTRY DATA ----------------
POVERTY_LINE = {
    "India": 10000,    # annual household income in local currency
    "USA": 15000,
    "UK": 14000,
    "UAE": 16000,
    "Nigeria": 1200,
    "Brazil": 4000
}

HELP_SUGGESTIONS = {
    "India": "Explore government welfare schemes, skill development programs, and local NGOs.",
    "USA": "Look into SNAP benefits, job reskilling programs, and community support services.",
    "UK": "Check Universal Credit support and employment training programs.",
    "UAE": "Explore workforce upskilling initiatives and social support entities.",
    "Nigeria": "Seek NGO assistance, microfinance programs, and vocational training.",
    "Brazil": "Look into Bolsa Família programs and employment support services."
}

# ---------------- SESSION STORAGE ----------------
SESSION_HISTORY = []

# ---------------- UTILITY FUNCTIONS ----------------
def calculate_risk(income, education, employment, household_size, working_members, country):
    poverty_line = POVERTY_LINE.get(country, 10000)
    income = max(0, income)

    # ---------------- RULE-BASED POVERTY RISK ----------------
    if income >= poverty_line:
        base_risk = max(10, 30 - (income - poverty_line) * 0.001)
    else:
        deficit_ratio = (poverty_line - income) / poverty_line
        base_risk = 90 * deficit_ratio + 10

    # Household factors: average education per household, working ratio
    working_ratio = working_members / max(1, household_size)
    modifier = education * 1.5 + employment * 5 + working_ratio * 10

    if base_risk > 50:
        risk_percent = max(base_risk - modifier, 50)
    else:
        risk_percent = max(base_risk - modifier, 10)

    # Clamp final risk between 0-100%
    risk_percent = min(100, max(0, risk_percent))
    return round(risk_percent, 2)

def risk_label_color(risk_percent):
    if risk_percent < 35:
        return "Low", "green"
    elif risk_percent < 65:
        return "Medium", "orange"
    else:
        return "High", "red"

def global_comparison(income, country):
    poverty_line = POVERTY_LINE.get(country, 10000)
    return "Below global average" if income < poverty_line else "Above global average"

def update_session(risk):
    SESSION_HISTORY.append(risk)
    total = len(SESSION_HISTORY)
    highest = max(SESSION_HISTORY)
    lowest = min(SESSION_HISTORY)
    average = round(sum(SESSION_HISTORY)/total,2)
    return {"total_entries": total, "highest_risk": highest, "lowest_risk": lowest, "average_risk": average}

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    income = float(request.form.get("income", 0))
    education = float(request.form.get("education", 0))
    employment = int(request.form.get("employment", 0))
    household_size = int(request.form.get("household_size", 1))
    working_members = int(request.form.get("working_members", 1))
    country = request.form.get("country", "India")

    risk_percent = calculate_risk(income, education, employment, household_size, working_members, country)
    level, color = risk_label_color(risk_percent)
    comparison = global_comparison(income, country)
    help_text = HELP_SUGGESTIONS.get(country, "Seek local support programs.")
    session_stats = update_session(risk_percent)

    return jsonify({
        "risk": risk_percent,
        "level": level,
        "color": color,
        "comparison": comparison,
        "help": help_text,
        "session_insights": session_stats
    })

@app.route("/clear_history", methods=["POST"])
def clear_history():
    SESSION_HISTORY.clear()
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(debug=True)
