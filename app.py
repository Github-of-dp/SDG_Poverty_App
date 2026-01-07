from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ---------------- COUNTRY DATA ----------------
POVERTY_LINE = {
    "India": 10000,    # Monthly income in local currency
    "USA": 1500,       # Adjusted monthly
    "UK": 1400,
    "UAE": 6000,
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

SESSION_HISTORY = []

# ---------------- HELPER FUNCTIONS ----------------
def calculate_risk(income, education, employment, household_size, working_members, country):
    poverty_line = POVERTY_LINE.get(country, 10000)
    dependency_ratio = 1 - (working_members / max(household_size,1))

    # Base risk based on income vs poverty line
    if income >= poverty_line:
        base_risk = max(5, 30 - (income - poverty_line) * 0.001)
    else:
        deficit_ratio = (poverty_line - income) / poverty_line
        base_risk = 90 * deficit_ratio + 10

    # Education and employment modifiers
    modifier = education * 1.5 + employment * 5 - dependency_ratio * 20
    risk_percent = base_risk - modifier

    # Clamp 0-100%
    risk_percent = min(100, max(0, risk_percent))

    # Risk level
    if risk_percent < 35:
        level = "Low"
        color = "#22c55e"
    elif risk_percent < 65:
        level = "Medium"
        color = "#f59e0b"
    else:
        level = "High"
        color = "#ef4444"

    # Why this result?
    reasons = []
    if income < poverty_line:
        reasons.append(f"Income below typical {country} household ({poverty_line})")
    else:
        reasons.append(f"Income above typical {country} household ({poverty_line})")

    if education < 8:
        reasons.append("Low education level reduces earning potential")
    else:
        reasons.append("Good education reduces poverty risk")

    if employment == 0:
        reasons.append("No employed member in household")
    else:
        reasons.append("At least one employed member")

    if dependency_ratio > 0.5:
        reasons.append("High dependency ratio in household")
    else:
        reasons.append("Balanced dependency ratio")

    # Country poverty context
    if income < poverty_line:
        comparison = f"Below typical income in {country}"
    else:
        comparison = f"Above typical income in {country}"

    return {
        "risk": round(risk_percent, 2),
        "level": level,
        "color": color,
        "why": reasons,
        "comparison": comparison
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
    household_size = int(request.form.get("household_size", 1))
    working_members = int(request.form.get("working_members", 1))
    country = request.form["country"]

    result = calculate_risk(income, education, employment, household_size, working_members, country)

    # Update session history
    SESSION_HISTORY.insert(0, {
        "income": income,
        "risk": result["risk"],
        "level": result["level"],
        "country": country
    })
    # Keep only latest 20
    SESSION_HISTORY[:] = SESSION_HISTORY[:20]

    # Session insights
    if SESSION_HISTORY:
        avg_risk = round(sum(h["risk"] for h in SESSION_HISTORY)/len(SESSION_HISTORY),2)
        high_count = sum(1 for h in SESSION_HISTORY if h["level"]=="High")
        medium_count = sum(1 for h in SESSION_HISTORY if h["level"]=="Medium")
        low_count = sum(1 for h in SESSION_HISTORY if h["level"]=="Low")
        session_insights = f"Avg Risk: {avg_risk}% | High: {high_count} | Medium: {medium_count} | Low: {low_count}"
    else:
        session_insights = "No session insights yet"

    return jsonify({
        **result,
        "session_history": SESSION_HISTORY,
        "session_insights": session_insights
    })

if __name__ == "__main__":
    app.run(debug=True)