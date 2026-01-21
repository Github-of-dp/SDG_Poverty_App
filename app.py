from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Real-world inspired thresholds for SDG 1.2 analysis
COUNTRY_DATA = {
    "UAE": {"line": 16000, "edu_target": 16, "weight": 1.2},
    "India": {"line": 8000, "edu_target": 12, "weight": 0.8},
    "USA": {"line": 2800, "edu_target": 16, "weight": 1.5},
    "Kenya": {"line": 4000, "edu_target": 10, "weight": 0.6}
}

@app.route("/")
def home():
    return render_template("index.html", countries=COUNTRY_DATA.keys())

@app.route("/analyze", methods=["POST"])
def analyze():
    d = request.json
    country = d.get('country', 'India')
    meta = COUNTRY_DATA[country]
    
    inc = float(d['income'])
    edu = float(d['education'])
    h_size = int(d['h_size'])
    workers = max(1, int(d['workers']))
    
    # 1. Calculation Logic
    m_risk = max(0, (meta['line'] - inc) / (meta['line'] / 40)) 
    e_risk = max(0, (meta['edu_target'] - edu) * 5)
    s_risk = (h_size / workers) * 7 * meta['weight']
    
    total_risk = round(min(100, m_risk + e_risk + s_risk), 1)
    future_risk = round(min(100, total_risk * (1.04 ** 5)), 1)
    
    return jsonify({
        "current": total_risk,
        "future": future_risk,
        "details": [
            {"label": "Monetary Gap", "score": round(m_risk, 1)},
            {"label": "Education Lag", "score": round(e_risk, 1)},
            {"label": "Dependency Load", "score": round(s_risk, 1)}
        ]
    })

if __name__ == "__main__":
    app.run(debug=True)