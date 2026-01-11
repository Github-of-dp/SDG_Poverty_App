from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Regional Poverty Lines & Advice
COUNTRY_CONFIG = {
    "UAE": {"line": 16000, "curr": "AED", "help": "Explore Nafis and workforce upskilling initiatives."},
    "India": {"line": 10000, "curr": "INR", "help": "Explore welfare schemes and local NGO support."},
    "USA": {"line": 2500, "curr": "USD", "help": "Check SNAP benefits and community services."},
    "UK": {"line": 2000, "curr": "GBP", "help": "Check Universal Credit and training programs."},
    "Nigeria": {"line": 80000, "curr": "NGN", "help": "Seek microfinance and vocational training."}
}

@app.route("/")
def home():
    return render_template("index.html", countries=COUNTRY_CONFIG)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        income = float(data.get("income", 0))
        edu = float(data.get("education", 0))
        emp = int(data.get("employment", 0))
        h_size = int(data.get("household_size", 1))
        workers = int(data.get("working_members", 1))
        country = data.get("country", "UAE")

        conf = COUNTRY_CONFIG.get(country, COUNTRY_CONFIG["UAE"])
        
        # --- LOGIC BREAKDOWN (Why the score is what it is) ---
        # 1. Income Deficit (50% max influence)
        money_risk = max(0, (conf["line"] - income) / conf["line"]) * 50
        
        # 2. Dependency (20% max influence) - Family Size vs Workers
        dep_ratio = h_size / max(1, workers)
        family_risk = min(20, (dep_ratio * 5)) 
        
        # 3. Education Gap (15% max influence) - Based on 16 years standard
        edu_risk = max(0, (16 - edu) / 16) * 15
        
        # 4. Job Status (15% max influence)
        job_risk = 0 if emp == 1 else 15

        total_risk = round(money_risk + family_risk + edu_risk + job_risk, 1)
        total_risk = min(100, total_risk)

        # Interpret the percentage for a "common person"
        if total_risk < 30:
            meaning = "Stable: You have strong 'resilience' against poverty."
        elif total_risk < 70:
            meaning = "Vulnerable: One major medical bill or job loss could cause crisis."
        else:
            meaning = "Critical: High risk. Immediate social support is recommended."

        return jsonify({
            "risk": total_risk,
            "meaning": meaning,
            "currency": conf["curr"],
            "help": conf["help"],
            "breakdown": {
                "Money Shortage": round(money_risk, 1),
                "Family Load": round(family_risk, 1),
                "Education Gap": round(edu_risk, 1),
                "Unemployment": round(job_risk, 1)
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
