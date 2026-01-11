from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ---------------- CONFIGURATION ----------------
COUNTRY_CONFIG = {
    "UAE": {"poverty_line": 16000, "currency": "AED", "help": "Explore workforce upskilling initiatives and Nafis program support."},
    "India": {"poverty_line": 10000, "currency": "INR", "help": "Explore government welfare schemes, skill development programs, and local NGOs."},
    "USA": {"poverty_line": 15000, "currency": "USD", "help": "Look into SNAP benefits, job reskilling programs, and community support services."},
    "UK": {"poverty_line": 14000, "currency": "GBP", "help": "Check Universal Credit support and employment training programs."},
    "Nigeria": {"poverty_line": 1200, "currency": "NGN", "help": "Seek NGO assistance, microfinance programs, and vocational training."}
}

@app.route("/")
def home():
    return render_template("index.html", countries=COUNTRY_CONFIG)

def calculate_risk(income, education, employment, household_size, working_members, country):
    config = COUNTRY_CONFIG.get(country, COUNTRY_CONFIG["India"])
    poverty_line = config["poverty_line"]

    # Basic poverty deficit ratio
    deficit_ratio = max(0, (poverty_line - income) / poverty_line)

    # Employment & household modifiers
    employment_factor = 0.2 if employment else 0.5  
    dependency_factor = 1 if household_size == 0 else household_size / max(1, working_members)

    # Education factor reduces risk slightly
    education_factor = max(0, (20 - education) / 20)

    # Combine factors based on your provided logic
    raw_risk = (deficit_ratio * 0.6) + (employment_factor * 0.2) + (education_factor * 0.2)
    risk_percent = min(100, max(0, raw_risk * 100 * dependency_factor))

    # Risk labels
    if risk_percent < 35:
        level, color = "Low", "green"
    elif risk_percent < 65:
        level, color = "Medium", "orange"
    else:
        level, color = "High", "red"

    comparison = "Above regional average" if income >= poverty_line else "Below regional average"
    
    return risk_percent, level, color, comparison, config["help"], config["currency"]

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        income = float(data.get("income", 0))
        education = float(data.get("education", 0))
        employment = int(data.get("employment", 0))
        household_size = int(data.get("household_size", 1))
        working_members = int(data.get("working_members", 1))
        country = data.get("country", "UAE")

        risk, level, color, comp, help_text, currency = calculate_risk(
            income, education, employment, household_size, working_members, country
        )

        return jsonify({
            "risk": round(risk, 2),
            "level": level,
            "color": color,
            "comparison": comp,
            "help": help_text,
            "currency": currency
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
