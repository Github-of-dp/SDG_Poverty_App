from flask import Flask, request, jsonify, send_from_directory
import math

app = Flask(__name__)

# Poverty line (monthly income) by country (simplified)
POVERTY_LINES = {
    "India": 12000,
    "USA": 2500,
    "UK": 2200,
    "UAE": 3000,
    "Global": 1800
}

GLOBAL_AVERAGE_RISK = 32  # %

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    income = float(data["income"])
    education = int(data["education"])
    employment = int(data["employment"])
    country = data["country"]

    poverty_line = POVERTY_LINES.get(country, POVERTY_LINES["Global"])

    # Normalized income score
    income_ratio = income / poverty_line

    # Risk calculation (interpretable, not black-box)
    risk = 100
    risk -= min(income_ratio * 40, 40)
    risk -= min(education * 3, 30)
    risk -= employment * 15

    risk = max(0, min(100, risk))
    risk = round(risk, 1)

    # Comparison
    comparison = (
        "Above Global Average Poverty Risk"
        if risk > GLOBAL_AVERAGE_RISK
        else "Below Global Average Poverty Risk"
    )

    # Country-specific suggestions
    suggestions = []
    if risk > 50:
        if country == "India":
            suggestions = [
                "Explore government skill-development programs (PMKVY)",
                "Check eligibility for education scholarships",
                "Look into local employment exchange services"
            ]
        elif country == "USA":
            suggestions = [
                "Explore workforce development programs",
                "Check SNAP or educational grants",
                "Consider community college skill courses"
            ]
        else:
            suggestions = [
                "Seek vocational training opportunities",
                "Explore employment assistance programs",
                "Consider education or reskilling initiatives"
            ]
    else:
        suggestions = ["Your indicators suggest relatively lower poverty risk"]

    return jsonify({
        "risk": risk,
        "poverty_line": poverty_line,
        "comparison": comparison,
        "suggestions": suggestions
    })

if __name__ == "__main__":
    app.run(debug=True)
