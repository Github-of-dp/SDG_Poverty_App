from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ---------------- COUNTRY POVERTY LINES ----------------
POVERTY_LINE = {
    "India": 10000,    # Monthly income in local currency
    "USA": 15000,
    "UK": 14000,
    "UAE": 16000,
    "Nigeria": 1200
}

HELP_SUGGESTIONS = {
    "India": "Explore government welfare schemes, skill development programs, and local NGOs.",
    "USA": "Look into SNAP benefits, job reskilling programs, and community support services.",
    "UK": "Check Universal Credit support and employment training programs.",
    "UAE": "Explore workforce upskilling initiatives and social support entities.",
    "Nigeria": "Seek NGO assistance, microfinance programs, and vocational training."
}

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")


def calculate_risk(income, education, employment, household_size, working_members, country):
    """Hybrid rule-based risk calculation"""
    poverty_line = POVERTY_LINE.get(country, 10000)

    # Basic poverty deficit ratio
    deficit_ratio = max(0, (poverty_line - income) / poverty_line)

    # Employment & household modifiers
    employment_factor = 0.2 if employment else 0.5  # Less employed → higher risk
    dependency_factor = 1 if household_size == 0 else household_size / max(1, working_members)

    # Education factor reduces risk slightly
    education_factor = max(0, (20 - education) / 20)

    # Combine factors
    raw_risk = deficit_ratio * 0.6 + employment_factor * 0.2 + education_factor * 0.2
    risk_percent = min(100, max(0, raw_risk * 100 * dependency_factor))

    # Risk labels
    if risk_percent < 35:
        level = "Low"
        color = "green"
    elif risk_percent < 65:
        level = "Medium"
        color = "orange"
    else:
        level = "High"
        color = "red"

    # Comparison
    comparison = "Above global average" if income >= poverty_line else "Below global average"
    help_text = HELP_SUGGESTIONS.get(country, "Seek local support programs.")

    return risk_percent, level, color, comparison, help_text


@app.route("/predict", methods=["POST"])
def predict():
    try:
        income = float(request.form.get("income", 0))
        education = float(request.form.get("education", 0))
        employment = int(request.form.get("employment", 0))
        household_size = int(request.form.get("household_size", 1))
        working_members = int(request.form.get("working_members", 1))
        country = request.form.get("country", "India")

        risk, level, color, comparison, help_text = calculate_risk(
            income, education, employment, household_size, working_members, country
        )

        return jsonify({
            "risk": round(risk, 2),
            "level": level,
            "color": color,
            "comparison": comparison,
            "help": help_text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)