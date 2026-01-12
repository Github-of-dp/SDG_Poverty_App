from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Real-world benchmark data (Simulated for this project)
COUNTRY_STATS = {
    "UAE": {"line": 16000, "avg_inc": 22000, "avg_edu": 14, "curr": "AED", "jobs": ["Tech", "Tourism", "Energy"]},
    "India": {"line": 10000, "avg_inc": 18000, "avg_edu": 10, "curr": "INR", "jobs": ["IT Services", "Agriculture", "Pharma"]},
    "USA": {"line": 2500, "avg_inc": 4500, "avg_edu": 13, "curr": "USD", "jobs": ["Healthcare", "Tech", "Retail"]},
    "UK": {"line": 2000, "avg_inc": 3100, "avg_edu": 13, "curr": "GBP", "jobs": ["Finance", "Education", "Construction"]},
    "Nigeria": {"line": 80000, "avg_inc": 120000, "avg_edu": 9, "curr": "NGN", "jobs": ["Oil & Gas", "Agriculture", "Telecom"]}
}

@app.route("/")
def home():
    return render_template("index.html", countries=COUNTRY_STATS)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    inc = float(data.get("income", 0))
    edu = float(data.get("education", 0))
    h_size = int(data.get("household_size", 1))
    country = data.get("country", "UAE")
    
    stats = COUNTRY_STATS.get(country, COUNTRY_STATS["UAE"])
    
    # 1. RISK CALCULATION (Same weighted logic)
    money_risk = max(0, (stats["line"] - inc) / stats["line"]) * 50
    dep_risk = min(20, (h_size / max(1, int(data.get("working_members", 1))) * 5))
    total_risk = round(min(100, money_risk + dep_risk + (max(0, 16-edu)*1.5)), 1)
    
    # 2. THE "SOLVER" (AI Recommendations)
    # Calculates exactly what is needed to reach "Safe" zone
    recommendations = []
    
    # Income Fix
    if inc < stats["line"]:
        needed = stats["line"] - inc
        recommendations.append(f"💰 Financial Gap: You need <b>{needed} {stats['curr']}</b> more to hit the stability floor.")
    
    # Education Fix
    if edu < stats["avg_edu"]:
        years = stats["avg_edu"] - edu
        recommendations.append(f"🎓 Skill Gap: The average person in {country} has <b>{years} more years</b> of education. Consider upskilling in <b>{', '.join(stats['jobs'])}</b>.")

    # 3. BENCHMARKING (You vs Average)
    comparison = {
        "income_pct": round((inc / stats["avg_inc"]) * 100, 1),
        "edu_diff": round(edu - stats["avg_edu"], 1),
        "status": "Above Average" if inc > stats["avg_inc"] else "Below Average"
    }

    return jsonify({
        "risk": total_risk,
        "recommendations": recommendations,
        "comparison": comparison,
        "stats": stats
    })

if __name__ == "__main__":
    app.run(debug=True)
