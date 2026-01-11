from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

# ---------------- CONFIGURATION ----------------
COUNTRY_CONFIG = {
    "UAE": {"poverty_line": 16000, "currency": "AED", "help": "Explore Nafis and workforce upskilling."},
    "India": {"poverty_line": 10000, "currency": "INR", "help": "Explore welfare schemes and skill development."},
    "USA": {"poverty_line": 2500, "currency": "USD", "help": "Check SNAP and community support services."},
    "UK": {"poverty_line": 2000, "currency": "GBP", "help": "Check Universal Credit and training programs."},
    "Nigeria": {"poverty_line": 80000, "currency": "NGN", "help": "Seek NGO and vocational training."}
}

@app.route("/")
def home():
    return render_template("index.html", countries=COUNTRY_CONFIG)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        income = float(data.get("income", 0))
        education = float(data.get("education", 0))
        employment = int(data.get("employment", 0))
        h_size = int(data.get("household_size", 1))
        workers = int(data.get("working_members", 1))
        country = data.get("country", "UAE")

        config = COUNTRY_CONFIG.get(country, COUNTRY_CONFIG["UAE"])
        
        # --- SMOOTHED LOGIC ---
        # 1. Poverty Deficit (How far below the line)
        deficit = max(0, (config["poverty_line"] - income) / config["poverty_line"])
        
        # 2. Dependency Ratio (Capped so it doesn't break the math)
        dep_ratio = h_size / max(1, workers)
        dep_factor = min(2, dep_ratio) / 2 # Normalize to a 0-1 scale
        
        # 3. Education & Employment
        edu_factor = max(0, (16 - education) / 16)
        emp_factor = 0 if employment else 0.4

        # Weighted calculation
        # Income(50%) + Dependency(20%) + Education(15%) + Employment(15%)
        raw_score = (deficit * 0.5) + (dep_factor * 0.2) + (edu_factor * 0.15) + (emp_factor * 0.15)
        
        # Convert to percentage
        risk_percent = round(raw_score * 100, 1)
        
        # Level Logic
        if risk_percent < 30: level = "Low"
        elif risk_percent < 70: level = "Medium"
        else: level = "High"

        return jsonify({
            "risk": risk_percent,
            "level": level,
            "currency": config["currency"],
            "help": config["help"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
