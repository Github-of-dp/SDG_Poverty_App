from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# SDG 1.2 Global Benchmark Data
SDG_METRICS = {
    "India": {"line": 10000, "target_reduction": 5000, "inflation": 0.06},
    "UAE": {"line": 16000, "target_reduction": 8000, "inflation": 0.03},
    "USA": {"line": 2500, "target_reduction": 1250, "inflation": 0.02}
}

@app.route("/")
def home():
    return render_template("index.html", regions=SDG_METRICS)

@app.route("/ai_engine", methods=["POST"])
def ai_engine():
    d = request.json
    inc = float(d.get("income", 0))
    edu = float(d.get("education", 0))
    h_size = int(d.get("h_size", 1))
    workers = max(1, int(d.get("workers", 1)))
    region = d.get("region", "India")
    
    meta = SDG_METRICS[region]
    
    # 1. MPI Dimensional Logic
    # We weight three dimensions (SDG 1.2 standard)
    dim_financial = max(0, (meta["line"] - inc) / meta["line"]) * 33.3
    dim_capability = max(0, (12 - edu) / 12) * 33.3
    dim_structural = min(33.3, ((h_size / workers) / 4) * 33.3)
    
    risk_score = round(dim_financial + dim_capability + dim_structural, 1)

    # 2. AI RESILIENCE SHOCK SIMULATION
    # What happens if a 'Medical Shock' costs 3 months of income?
    shock_impact = (inc * 3) / meta["line"]
    resilience_score = round(100 - (risk_score + (shock_impact * 2)), 1)
    resilience_score = max(0, min(100, resilience_score))

    # 3. AI STRATEGIC PATHWAY
    if dim_financial > dim_capability and dim_financial > dim_structural:
        path = "Immediate Income Support"
        ai_msg = f"AI identifies Monetary Gap as your critical failure point. Target: Increase income by {round(meta['line']-inc)} to reach basic stability."
    elif dim_capability > dim_structural:
        path = "Skill Acquisition"
        ai_msg = "AI identifies Capability Deprivation. Your income is high, but your human capital is low, making you vulnerable to market changes."
    else:
        path = "Structural Adjustment"
        ai_msg = "AI identifies Dependency Stress. Your household size per worker is unsustainable for long-term SDG 1.2 goals."

    return jsonify({
        "risk": risk_score,
        "resilience": resilience_score,
        "pathway": path,
        "ai_analysis": ai_msg,
        "breakdown": [
            {"label": "Monetary", "val": round(dim_financial, 1)},
            {"label": "Capability", "val": round(dim_capability, 1)},
            {"label": "Structural", "val": round(dim_structural, 1)}
        ],
        "sdg_gap": round(max(0, inc - meta['target_reduction']), 1)
    })

if __name__ == "__main__":
    app.run(debug=True)
