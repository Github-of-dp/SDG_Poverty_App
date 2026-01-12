from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# Real SDG 1.2 target thresholds
REGIONS = {
    "India": {"line": 10000, "target": 5000, "curr": "INR"},
    "UAE": {"line": 16000, "target": 8000, "curr": "AED"},
    "USA": {"line": 2500, "target": 1250, "curr": "USD"}
}

@app.route("/")
def home():
    return render_template("index.html", regions=REGIONS)

@app.route("/simulate", methods=["POST"])
def simulate():
    d = request.json
    inc, edu = float(d['income']), float(d['education'])
    h_size, workers = int(d['h_size']), max(1, int(d['workers']))
    
    # Calculate Base Risk (SDG 1.2 Multidimensional)
    meta = REGIONS[d['region']]
    inc_risk = max(0, (meta['line'] - inc) / meta['line']) * 40
    edu_risk = max(0, (12 - edu) / 12) * 30
    struct_risk = min(30, ((h_size / workers) / 4) * 30)
    
    total_risk = round(inc_risk + edu_risk + struct_risk, 1)
    
    # AI Logic: Target 1.2 Progress
    target_gap = round(((inc - meta['target']) / meta['target']) * 100, 1)
    
    return jsonify({
        "risk": total_risk,
        "sdg_msg": "Target 1.2 Achieved" if inc > meta['target'] else "Below SDG Target",
        "gap": target_gap,
        "breakdown": {"Financial": round(inc_risk), "Capability": round(edu_risk), "Structural": round(struct_risk)}
    })

if __name__ == "__main__":
    app.run(debug=True)
