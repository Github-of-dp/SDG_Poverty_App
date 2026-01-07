from flask import Flask, render_template, request, jsonify, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "sdg1sessionkey"

# ---------------- COUNTRY DATA ----------------
POVERTY_LINE = {
    "India": 10000,    # annual income in local currency
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

SDG_INFO = "This model aligns with SDG-1: No Poverty, by helping households understand relative poverty risk and access support options."

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html", sdg_info=SDG_INFO)

@app.route("/predict", methods=["POST"])
def predict():
    income = float(request.form["income"])
    income = max(0, income)
    education = float(request.form["education"])
    employment = int(request.form["employment"])
    household_size = int(request.form.get("household_size", 1))
    working_members = int(request.form.get("working_members", 1))
    country = request.form["country"]

    poverty_line = POVERTY_LINE.get(country, 10000)

    # ---------------- RULE-BASED RISK ----------------
    if income >= poverty_line:
        base_risk = max(10, 30 - (income - poverty_line) * 0.001)
    else:
        deficit_ratio = (poverty_line - income) / poverty_line
        base_risk = 90 * deficit_ratio + 10

    modifier = education * 1.5 + employment * 5
    if base_risk > 50:
        risk_percent = max(base_risk - modifier, 50)
    else:
        risk_percent = max(base_risk - modifier, 10)

    risk_percent = min(100, max(0, risk_percent))

    if risk_percent < 35:
        level = "Low"
        color = "#22c55e"
    elif risk_percent < 65:
        level = "Medium"
        color = "#f59e0b"
    else:
        level = "High"
        color = "#ef4444"

    comparison = "Below global average" if income < poverty_line else "Above global average"
    help_text = HELP_SUGGESTIONS.get(country, "Seek local support programs.")

    # ---------------- SESSION INSIGHTS ----------------
    if "history" not in session:
        session["history"] = []

    session["history"].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "income": income,
        "education": education,
        "employment": employment,
        "household_size": household_size,
        "working_members": working_members,
        "risk": round(risk_percent, 2),
        "level": level
    })
    session.modified = True

    return jsonify({
        "risk": round(risk_percent, 2),
        "level": level,
        "color": color,
        "comparison": comparison,
        "help": help_text,
        "history": session["history"]
    })

if __name__ == "__main__":
    app.run(debug=True)
