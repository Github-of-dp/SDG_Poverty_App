from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Regional Config with "Standard of Living" cost factor
REGIONS = {
    "UAE": {"line": 16000, "curr": "AED", "col_factor": 1.0, "avg_edu": 14},
    "USA": {"line": 2500, "curr": "USD", "col_factor": 1.2, "avg_edu": 13},
    "India": {"line": 10000, "curr": "INR", "col_factor": 0.4, "avg_edu": 10},
    "UK": {"line": 2000, "curr": "GBP", "col_factor": 1.1, "avg_edu": 13}
}

@app.route("/")
def home():
    return render_template("index.html", regions=REGIONS)

@app.route("/process", methods=["POST"])
def process():
    data = request.json
    inc = float(data.get("income", 0))
    edu = float(data.get("education", 0))
    h_size = int(data.get("household_size", 1))
    workers = max(1, int(data.get("working_members", 1)))
    region = data.get("region", "UAE")
    
    stats = REGIONS.get(region, REGIONS["UAE"])
    
    # --- 1. THE CORE FORMULA (The "Why") ---
    # We calculate raw "Risk Points" for each category
    
    # Financial Stress (Exponential decay based on income gap)
    inc_gap = max(0, stats["line"] - inc)
    r_finance = (inc_gap / stats["line"]) * 50 # Max 50 pts
    
    # Dependency Load (Linear burden)
    dep_ratio = h_size / workers
    r_family = min(30, (dep_ratio - 1) * 10) # Max 30 pts
    
    # Education Buffer (Protection factor)
    # Education reduces risk. We treat it as negative points (protection).
    edu_protection = min(20, (edu / 16) * 20) 
    
    # Total Score
    base_risk = r_finance + r_family
    final_risk = max(0, min(100, base_risk - edu_protection))
    
    # --- 2. SENSITIVITY AI (The "Value") ---
    # The AI tests two scenarios to see which is better
    
    # Scenario A: What if income increases by 20%?
    inc_new = inc * 1.2
    risk_A = max(0, min(100, (((stats["line"] - inc_new)/stats["line"])*50 + r_family - edu_protection)))
    benefit_A = final_risk - risk_A
    
    # Scenario B: What if education increases by 2 years?
    edu_new = edu + 2
    prot_new = min(20, (edu_new / 16) * 20)
    risk_B = max(0, min(100, (r_finance + r_family - prot_new)))
    benefit_B = final_risk - risk_B
    
    # Decision Engine
    if benefit_B > benefit_A:
        strategy = "Long-Term Upskilling"
        msg = f"AI ANALYSIS: Education leverage is high. Gaining 2 years of skills reduces risk by {round(benefit_B,1)}%, whereas a 20% raise only reduces it by {round(benefit_A,1)}%."
    elif benefit_A > 0:
        strategy = "Immediate Cashflow"
        msg = f"AI ANALYSIS: Critical income shortage detected. Prioritize immediate employment/income over education to stabilize survival (SDG 1.1)."
    else:
        strategy = "Maintenance"
        msg = "AI ANALYSIS: System stable. Maintain current trajectory."

    return jsonify({
        "risk": round(final_risk, 1),
        "breakdown": {
            "Income Stress": round(r_finance, 1),
            "Family Load": round(r_family, 1),
            "Edu Protection": round(edu_protection, 1) # This will be negative in the chart
        },
        "ai_insight": {
            "strategy": strategy,
            "message": msg,
            "leverage_score": round(max(benefit_A, benefit_B), 1)
        },
        "currency": stats["curr"]
    })

if __name__ == "__main__":
    app.run(debug=True)
