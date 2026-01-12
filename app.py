from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Data based on SDG-1.2 monitoring standards
REGIONS = {
    "India": {"line": 10000, "avg": 18000, "curr": "INR", "target": "SDG 1.2.1: Income Poverty"},
    "UAE": {"line": 16000, "avg": 22000, "curr": "AED", "target": "SDG 1.2.2: Multidimensional Poverty"},
    "USA": {"line": 2500, "avg": 5200, "curr": "USD", "target": "SDG 1.2.1: Relative Poverty"},
    "UK": {"line": 2000, "avg": 3300, "curr": "GBP", "target": "SDG 1.2.2: Capability Deprivation"}
}

@app.route("/")
def home():
    return render_template("index.html", regions=REGIONS)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    inc = float(data.get("income", 0))
    edu = float(data.get("education", 0))
    h_size = int(data.get("h_size", 1))
    workers = max(1, int(data.get("workers", 1)))
    region = data.get("region", "India")
    
    meta = REGIONS[region]
    
    # --- The "Why" Logic (SDG-1 Dimensions) ---
    # Dimension 1: Monetary (Weight 40%)
    monetary_risk = max(0, (meta["line"] - inc) / meta["line"]) * 40
    
    # Dimension 2: Capability/Education (Weight 30%)
    # Research shows 12 years of schooling is the "stability threshold"
    edu_risk = max(0, (12 - edu) / 12) * 30
    
    # Dimension 3: Structural/Family (Weight 30%)
    dep_ratio = h_size / workers
    structural_risk = min(30, (dep_ratio / 3) * 30)
    
    total_risk = round(monetary_risk + edu_risk + structural_risk, 1)

    return jsonify({
        "risk": total_risk,
        "status": "Resilient" if total_risk < 30 else "At Risk" if total_risk < 70 else "Vulnerable",
        "currency": meta["curr"],
        "target_info": meta["target"],
        "breakdown": [
            {"label": "Monetary Gap", "val": round(monetary_risk, 1), "desc": "Distance from local poverty line."},
            {"label": "Capability Gap", "val": round(edu_risk, 1), "desc": "Lack of educational buffer."},
            {"label": "Structural Load", "val": round(structural_risk, 1), "desc": "High dependency ratio."}
        ]
    })

if __name__ == "__main__":
    app.run(debug=True)
