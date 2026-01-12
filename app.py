from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

REGIONS = {
    "UAE": {"line": 16000, "floor": 8000},
    "India": {"line": 10000, "floor": 5000},
    "USA": {"line": 2800, "floor": 1400}
}

@app.route("/")
def home():
    return render_template("index.html", regions=REGIONS)

@app.route("/analyze", methods=["POST"])
def analyze():
    d = request.json
    inc, edu = float(d['income']), float(d['education'])
    h_size, workers = int(d['h_size']), max(1, int(d['workers']))
    meta = REGIONS[d['region']]
    
    # Logic: Factor Contributions
    monetary_risk = round(max(0, (meta['line'] - inc) / meta['line']) * 40, 1)
    # Education logic: Each year below 16 adds 2.5% risk
    edu_risk = round(max(0, (16 - edu) * 2.5), 1)
    # Structural logic: Dependency ratio (People per worker)
    struct_risk = round(min(30, (h_size / workers) * 5), 1)
    
    total_risk = round(monetary_risk + edu_risk + struct_risk, 1)
    
    # 5-Year Forecast (Economic Drift)
    # 5% annual inflation vs 2% wage growth = ~3% net decay per year
    future_risk = round(total_risk * (1.03 ** 5), 1)
    
    return jsonify({
        "total": total_risk,
        "future": min(100, future_risk),
        "factors": [
            {"name": "Low Income", "val": monetary_risk, "color": "#ff0055" if monetary_risk > 20 else "#ccff00"},
            {"name": "Edu Gap", "val": edu_risk, "color": "#ff0055" if edu_risk > 15 else "#ccff00"},
            {"name": "Dependency", "val": struct_risk, "color": "#ff0055" if struct_risk > 15 else "#ccff00"}
        ]
    })

if __name__ == "__main__":
    app.run(debug=True)
