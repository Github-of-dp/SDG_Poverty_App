from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ---------------- COUNTRY DATA ----------------
POVERTY_LINE = {
    "India": 10000,
    "USA": 15000,
    "UK": 14000,
    "UAE": 16000,
    "Nigeria": 1200,
    "Brazil": 4000
}

COUNTRY_CONTEXT = {
    "India": "Large income inequality; poverty is influenced by informal employment and access to education.",
    "USA": "Poverty often relates to healthcare access, housing costs, and job stability.",
    "UK": "Living costs and welfare dependency significantly affect poverty risk.",
    "UAE": "Income disparities exist between skilled and unskilled migrant workers.",
    "Nigeria": "Poverty strongly linked to unemployment and limited access to education.",
    "Brazil": "Social inequality and regional development gaps impact poverty levels."
}

HELP_SUGGESTIONS = {
    "India": "Explore government welfare schemes, skill development programs, and local NGOs.",
    "USA": "Look into SNAP benefits, job reskilling programs, and community support services.",
    "UK": "Check Universal Credit support and employment training programs.",
    "UAE": "Explore workforce upskilling initiatives and social support entities.",
    "Nigeria": "Seek NGO assistance, microfinance programs, and vocational training.",
    "Brazil": "Look into Bolsa Família programs and employment support services."
}

# ---------------- SESSION HISTORY (D) ----------------
SESSION_HISTORY = []

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

    poverty_line = POVERTY_LINE.get(country, 10000)

    # ---------------- RULE-BASED CORE MODEL ----------------
    if income <= 0:
        base_risk = 95
    elif income < poverty_line:
        deficit_ratio = (poverty_line - income) / poverty_line
        base_risk = 60 + deficit_ratio * 35
    else:
        surplus_ratio = (income - poverty_line) / poverty_line
        base_risk = max(10, 35 - surplus_ratio * 20)

    # Modifiers
    education_impact = min(education * 1.2, 20)
    employment_impact = 8 if employment == 1 else 0

    risk_percent = base_risk - education_impact - employment_impact
    risk_percent = min(100, max(5, risk_percent))

    # Risk label
    if risk_percent < 35:
        level = "Low"
        color = "green"
    elif risk_percent < 65:
        level = "Medium"
        color = "orange"
    else:
        level = "High"
        color = "red"

    comparison = "Below poverty line" if income < poverty_line else "Above poverty line"

    # ---------------- SDG ALIGNMENT (E) ----------------
    sdg_alignment = {
        "goal": "SDG 1: No Poverty",
        "impact": "High" if risk_percent >= 65 else "Moderate" if risk_percent >= 35 else "Low"
    }

    # ---------------- SAVE SESSION (D) ----------------
    SESSION_HISTORY.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "country": country,
        "risk": round(risk_percent, 2)
    })

    SESSION_HISTORY[:] = SESSION_HISTORY[-5:]  # keep last 5

    return jsonify({
        "risk": round(risk_percent, 2),
        "level": level,
        "color": color,

        # A) Explainability
        "base_risk": round(base_risk, 2),
        "education_impact": round(education_impact, 2),
        "employment_impact": employment_impact,

        # B) Country context
        "country_context": COUNTRY_CONTEXT.get(country),
        "comparison": comparison,
        "help": HELP_SUGGESTIONS.get(country),

        # C) Scenario simulation
        "simulations": {
            "income_plus_20": round(max(5, risk_percent - 10), 2),
            "income_minus_20": round(min(100, risk_percent + 15), 2)
        },

        # D) Session history
        "history": SESSION_HISTORY,

        # E) SDG
        "sdg": sdg_alignment
    })

if __name__ == "__main__":
    app.run(debug=True)
