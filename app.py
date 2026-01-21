from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Regional benchmarks for SDG 1.2
REGIONS = {
    "UAE": {"line": 16000, "edu": 16, "currency": "AED"},
    "India": {"line": 15000, "edu": 12, "currency": "INR"},
    "USA": {"line": 3200, "edu": 16, "currency": "USD"},
    "UK": {"line": 2500, "edu": 15, "currency": "GBP"},
    "Nigeria": {"line": 150000, "edu": 10, "currency": "NGN"},
    "Brazil": {"line": 3500, "edu": 12, "currency": "BRL"},
    "Singapore": {"line": 4500, "edu": 16, "currency": "SGD"},
    "Kenya": {"line": 25000, "edu": 11, "currency": "KES"}
}

@app.route("/")
def home():
    return render_template("index.html", regions=REGIONS.keys())

@app.route("/analyze", methods=["POST"])
def analyze():
    d = request.json
    meta = REGIONS[d['region']]
    
    # Calculation Logic
    inc = float(d['income'])
    edu = float(d['education'])
    h_size = int(d['h_size'])
    workers = max(1, int(d['workers']))
    
    # Balanced Weighting (Max 33.3% each)
    f_risk = max(0, (meta['line'] - inc) / meta['line']) * 33.3
    e_risk = max(0, (meta['edu'] - edu) / meta['edu']) * 33.3
    s_risk = min(33.3, ((h_size / workers) / 5) * 33.3)
    
    current_total = round(f_risk + e_risk + s_risk, 1)
    future_total = round(min(100, current_total * (1.035 ** 5)), 1)
    
    return jsonify({
        "current": current_total,
        "future": future_total,
        "breakdown": [
            {"label": "Money & Income", "val": round(f_risk, 1)},
            {"label": "Skills & Education", "val": round(e_risk, 1)},
            {"label": "Living Standards", "val": round(s_risk, 1)}
        ]
    })

if __name__ == "__main__":
    app.run(debug=True)