from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

COUNTRY_CONFIG = {
    "UAE": {"line": 16000, "curr": "AED", "help": "Explore Nafis and workforce upskilling initiatives.", "info": "The UAE focuses on 'Social Floor' protections and career nationalization (Nafis)."},
    "India": {"line": 10000, "curr": "INR", "help": "Explore government welfare schemes (PDS) and skill development.", "info": "India uses the Multidimensional Poverty Index (MPI) to track health, education, and living standards."},
    "USA": {"line": 2500, "curr": "USD", "help": "Check SNAP benefits and community services.", "info": "The US Poverty Threshold is updated annually by the Census Bureau based on food costs."},
    "UK": {"line": 2000, "curr": "GBP", "help": "Check Universal Credit and training programs.", "info": "The UK measures 'Relative Poverty'—households with less than 60% of median income."},
    "Nigeria": {"line": 80000, "curr": "NGN", "help": "Seek microfinance and vocational training.", "info": "Nigeria's poverty reduction focuses heavily on agricultural productivity and rural infrastructure."}
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
        
        # Weighted Logic
        money_risk = max(0, (conf["line"] - income) / conf["line"]) * 50
        dep_ratio = h_size / max(1, workers)
        family_risk = min(20, (dep_ratio * 5)) 
        edu_risk = max(0, (16 - edu) / 16) * 15
        job_risk = 0 if emp == 1 else 15

        total_risk = round(min(100, money_risk + family_risk + edu_risk + job_risk), 1)

        # High-level summary
        if total_risk < 30:
            status = "Resilient"
            color = "#10b981" # Green
        elif total_risk < 70:
            status = "At-Risk"
            color = "#f59e0b" # Orange
        else:
            status = "Vulnerable"
            color = "#ef4444" # Red

        return jsonify({
            "risk": total_risk,
            "status": status,
            "color": color,
            "currency": conf["curr"],
            "help": conf["help"],
            "info": conf["info"],
            "breakdown": [
                {"label": "Income Gap", "value": round(money_risk, 1), "desc": "Distance from poverty line"},
                {"label": "Dependency", "value": round(family_risk, 1), "desc": "Non-working vs working members"},
                {"label": "Edu Level", "value": round(edu_risk, 1), "desc": "Lack of academic buffer"},
                {"label": "Job Status", "value": round(job_risk, 1), "desc": "Current employment impact"}
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
