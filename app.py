from flask import Flask, render_template, request, jsonify, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session

# ---------------- COUNTRY DATA ----------------
POVERTY_LINE = {
    "India": 12000,    # Annual income in local currency
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

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    income = max(0, float(request.form["income"]))
    education = float(request.form["education"])
    employment = int(request.form["employment"])
    country = request.form["country"]
    household_size = int(request.form.get("household_size", 1))
    working_members = int(request.form.get("working_members", 1))

    poverty_line = POVERTY_LINE.get(country, 10000)

    # ---------------- RULE-BASED RISK ----------------
    # Household-adjusted poverty risk
    per_capita_income = income / max(1, household_size)
    deficit_ratio = max(0, poverty_line - per_capita_income) / poverty_line
    base_risk = 90 * deficit_ratio + 10  # Minimum 10% risk

    # Education/employment/working members modifiers
    modifier = education * 1.5 + employment * 5 + working_members * 2
    risk_percent = max(base_risk - modifier, 5)
    risk_percent = min(100, risk_percent)

    # Risk label & color
    if risk_percent < 35:
        level = "Low"
        color = "#22c55e"  # green
    elif risk_percent < 65:
        level = "Medium"
        color = "#f97316"  # orange
    else:
        level = "High"
        color = "#ef4444"  # red

    # Global comparison
    comparison = "Below global average" if per_capita_income < poverty_line else "Above global average"

    help_text = HELP_SUGGESTIONS.get(country, "Seek local support programs.")

    # ---------------- SESSION HISTORY ----------------
    entry = {
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "income": income,
        "education": education,
        "employment": employment,
        "household_size": household_size,
        "working_members": working_members,
        "risk": round(risk_percent, 2),
        "level": level,
        "comparison": comparison,
        "help": help_text
    }

    if "history" not in session:
        session["history"] = []
    history = session["history"]
    history.append(entry)
    session["history"] = history

    # ---------------- SESSION INSIGHTS ----------------
    risks = [h["risk"] for h in history]
    session_insights = {
        "highest_risk": max(risks),
        "lowest_risk": min(risks),
        "average_risk": round(sum(risks)/len(risks), 2),
        "total_entries": len(risks)
    }

    return jsonify({
        "risk": round(risk_percent, 2),
        "level": level,
        "color": color,
        "comparison": comparison,
        "help": help_text,
        "session_insights": session_insights
    })

@app.route("/clear_history", methods=["POST"])
def clear_history():
    session.pop("history", None)
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(debug=True)
