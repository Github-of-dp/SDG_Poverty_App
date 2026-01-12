from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Real data mappings for SDG 1.2 Monitoring
DATA_MAP = {
    "UAE": {"line": 16000, "sdg_target": 8000, "avg_inc": 21000, "curr": "AED"},
    "India": {"line": 10000, "sdg_target": 5000, "avg_inc": 18000, "curr": "INR"},
    "USA": {"line": 2500, "sdg_target": 1250, "avg_inc": 5200, "curr": "USD"},
    "UK": {"line": 2000, "sdg_target": 1000, "avg_inc": 3300, "curr": "GBP"}
}

@app.route("/")
def home():
    return render_template("index.html", data=DATA_MAP)

@app.route("/analyze", methods=["POST"])
def analyze():
    d = request.json
    inc = float(d.get("income", 0))
    edu = float(d.get("education", 0))
    h_size = int(d.get("h_size", 1))
    workers = max(1, int(d.get("workers", 1)))
    region = d.get("region", "UAE")
    
    meta = DATA_MAP[region]
    
    # SDG 1.2 Multidimensional Math
    # 1. Income Dimension (Weight 1/3)
    inc_score = max(0, (meta["line"] - inc) / meta["line"]) * 100
    
    # 2. Education Dimension (Weight 1/3)
    edu_score = max(0, (12 - edu) / 12) * 100
    
    # 3. Living Standard/Dependency (Weight 1/3)
    dep_ratio = h_size / workers
    dep_score = min(100, (dep_ratio / 4) * 100)
    
    # Final Composite Risk
    total_risk = round((inc_score + edu_score + dep_score) / 3, 1)
    
    # SDG 1.2 Target Status
    # SDG 1.2 aims to reduce the "proportion" by half.
    is_below_target = inc < meta["sdg_target"]
    
    return jsonify({
        "risk": total_risk,
        "sdg_status": "Failing Target 1.2" if is_below_target else "Meeting SDG Threshold",
        "breakdown": {"Financial": round(inc_score, 1), "Educational": round(edu_score, 1), "Structural": round(dep_score, 1)},
        "plan": [
            "Increase income by " + str(round(meta["line"] - inc)) + " to exit poverty line." if inc < meta["line"] else "Income is stable.",
            "Upskill to 12+ years of education to maximize structural resilience." if edu < 12 else "Educational buffer is strong.",
            "Improve worker-to-dependent ratio to reduce structural load." if dep_ratio > 2 else "Household structure is efficient."
        ]
    })

if __name__ == "__main__":
    app.run(debug=True)
