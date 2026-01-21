from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Regional benchmarks for realistic scaling
REGIONS = {
    "UAE": {"line": 16000, "edu": 16},
    "India": {"line": 8000, "edu": 12},
    "USA": {"line": 2800, "edu": 16}
}

@app.route("/")
def home():
    return render_template("index.html", regions=REGIONS.keys())

@app.route("/analyze", methods=["POST"])
def analyze():
    d = request.json
    meta = REGIONS[d['region']]
    
    # 1. Financial Component (Weighted 33%)
    inc = float(d['income'])
    # Risk is 0 if income is above line, scales up if below.
    f_risk = max(0, (meta['line'] - inc) / meta['line']) * 33.3
    
    # 2. Education Component (Weighted 33%)
    edu = float(d['education'])
    # Every year missing from target adds risk
    e_risk = max(0, (meta['edu'] - edu) / meta['edu']) * 33.3
    
    # 3. Structural Component (Weighted 33%)
    h_size = int(d['h_size'])
    workers = max(1, int(d['workers']))
    dep_ratio = h_size / workers
    # A ratio of 4+ is high risk
    s_risk = min(33.3, (dep_ratio / 4) * 33.3)
    
    total_risk = round(f_risk + e_risk + s_risk, 1)
    
    return jsonify({
        "total": total_risk,
        "financial": round(f_risk, 1),
        "education": round(e_risk, 1),
        "structural": round(s_risk, 1)
    })

if __name__ == "__main__":
    app.run(debug=True)