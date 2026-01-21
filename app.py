from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Realistic benchmarks for SDG 1.2
REGIONS = {
    "UAE": {"line": 16000, "edu": 16, "currency": "AED"},
    "India": {"line": 8000, "edu": 12, "currency": "INR"},
    "USA": {"line": 2800, "edu": 16, "currency": "USD"}
}

@app.route("/")
def home():
    return render_template("index.html", regions=REGIONS.keys())

@app.route("/analyze", methods=["POST"])
def analyze():
    d = request.json
    meta = REGIONS[d['region']]
    
    # Data Extraction
    inc = float(d['income'])
    edu = float(d['education'])
    h_size = int(d['h_size'])
    workers = max(1, int(d['workers']))
    
    # Balanced Weighting (Max 33.3% each)
    f_risk = max(0, (meta['line'] - inc) / meta['line']) * 33.3
    e_risk = max(0, (meta['edu'] - edu) / meta['edu']) * 33.3
    s_risk = min(33.3, ((h_size / workers) / 5) * 33.3)
    
    current_total = round(f_risk + e_risk + s_risk, 1)
    
    # 5-Year Forecast (Includes 3.5% economic drift/inflation impact)
    future_total = round(min(100, current_total * (1.035 ** 5)), 1)
    
    return jsonify({
        "current": current_total,
        "future": future_total,
        "breakdown": [
            {"label": "Monetary", "val": round(f_risk, 1)},
            {"label": "Capability", "val": round(e_risk, 1)},
            {"label": "Structural", "val": round(s_risk, 1)}
        ]
    })

if __name__ == "__main__":
    app.run(debug=True)