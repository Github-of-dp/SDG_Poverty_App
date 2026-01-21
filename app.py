from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Regional metadata for SDG 1.2 simulation
COUNTRY_DATA = {
    "UAE": {"line": 16000, "edu_target": 16, "description": "High-income urban context."},
    "India": {"line": 8000, "edu_target": 12, "description": "Rapidly developing multidimensional context."},
    "Kenya": {"line": 4000, "edu_target": 10, "description": "Emerging rural-to-urban transition."}
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
    
    # SDG 1.2 Math Logic
    m_risk = max(0, (meta['line'] - inc) / (meta['line'] / 40)) 
    e_risk = max(0, (meta['edu_target'] - edu) * 6)
    s_risk = (h_size / workers) * 8
    
    total_risk = round(min(100, m_risk + e_risk + s_risk), 1)
    
    return jsonify({
        "current": total_risk,
        "details": [
            {"label": "Monetary Depth", "score": round(m_risk, 1), "sdg": "1.2.1"},
            {"label": "Capability Gap", "score": round(e_risk, 1), "sdg": "1.2.2"},
            {"label": "Dependency Ratio", "score": round(s_risk, 1), "sdg": "1.2.2"}
        ],
        "meta": meta
    })

if __name__ == "__main__":
    app.run(debug=True)