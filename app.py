from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# SDG 1.2 Regional Benchmarks
REGIONS = {
    "UAE": {"line": 16000, "floor": 8000, "curr": "AED"},
    "India": {"line": 10000, "floor": 5000, "curr": "INR"},
    "USA": {"line": 2800, "floor": 1400, "curr": "USD"}
}

@app.route("/")
def home():
    return render_template("index.html", regions=REGIONS)

@app.route("/analyze", methods=["POST"])
def analyze():
    d = request.json
    inc = float(d.get('income', 0))
    edu = float(d.get('education', 0))
    h_size = int(d.get('h_size', 4))
    workers = max(1, int(d.get('workers', 1)))
    region = d.get('region', 'UAE')
    
    meta = REGIONS[region]
    
    # 1. MONETARY RISK (Weight 40%)
    m_risk = max(0, (meta['line'] - inc) / meta['line']) * 40
    
    # 2. CAPABILITY RISK (Education Detailed - Weight 30%)
    # Milestones: 16 (Degree), 12 (High School), 6 (Primary)
    if edu >= 16: edu_factor = 0
    elif edu >= 12: edu_factor = 0.2
    elif edu >= 6: edu_factor = 0.6
    else: edu_factor = 1.0
    c_risk = edu_factor * 30
    
    # 3. STRUCTURAL RISK (Dependency - Weight 30%)
    dep_ratio = h_size / workers
    s_risk = min(30, (dep_ratio / 5) * 30)
    
    total_risk = round(m_risk + c_risk + s_risk, 1)
    
    # Logic for "Risk Color"
    color = "#ccff00" # Safe (Lime)
    if total_risk > 60: color = "#ff0055" # Critical (Neon Red)
    elif total_risk > 30: color = "#ffaa00" # Warning (Orange)

    return jsonify({
        "total": total_risk,
        "color": color,
        "breakdown": [
            {"name": "Monetary Gap", "val": round(m_risk, 1), "impact": "High" if m_risk > 20 else "Low"},
            {"name": "Capability Gap", "val": round(c_risk, 1), "impact": "High" if c_risk > 15 else "Low"},
            {"name": "Structural Load", "val": round(s_risk, 1), "impact": "High" if s_risk > 15 else "Low"}
        ],
        "sdg_status": "Meeting SDG 1.2" if inc > meta['floor'] else "Below SDG 1.2 Target"
    })

if __name__ == "__main__":
    app.run(debug=True)
