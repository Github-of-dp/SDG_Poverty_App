from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.linear_model import LogisticRegression
from datetime import datetime

app = Flask(__name__)

# ---------- MODEL ----------
df = pd.read_csv("poverty_data.csv")
X = df[['income', 'education', 'employment']]
y = df['poverty_risk']

model = LogisticRegression()
model.fit(X, y)

# ---------- STORAGE (Feature E) ----------
history = []

# ---------- ROUTES ----------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    income = float(data["income"])
    education = float(data["education"])
    employment = float(data["employment"])

    prob = model.predict_proba([[income, education, employment]])[0][1]
    risk = round(prob * 100, 2)

    status = "High Poverty Risk" if risk > 50 else "Low Poverty Risk"

    # Feature B – Recommendations
    recommendations = []
    if risk > 50:
        recommendations = [
            "Government welfare schemes",
            "Skill development programs",
            "Education scholarships",
            "Employment assistance"
        ]

    # Feature D – Awareness Comparison
    comparison = {
        "global_average_risk": 35,
        "your_risk": risk
    }

    # Feature E – Progress tracking
    history.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "risk": risk
    })

    return jsonify({
        "risk": risk,
        "status": status,
        "recommendations": recommendations,
        "comparison": comparison,
        "history": history[-5:]  # last 5 checks
    })

if __name__ == "__main__":
    app.run(debug=True)
