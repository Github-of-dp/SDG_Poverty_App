from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

app = Flask(__name__)

# ---------------------------
# Country normalization data
# ---------------------------
COUNTRY_BASELINES = {
    "India": 12000,
    "USA": 40000,
    "UK": 35000,
    "UAE": 30000,
    "Nigeria": 8000
}

# ---------------------------
# Load dataset
# ---------------------------
df = pd.read_csv("poverty_data.csv")

X = df[['income', 'education', 'employment']]
y = df['poverty_risk']

# ---------------------------
# ML Pipeline
# ---------------------------
model = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression())
])

model.fit(X, y)

# ---------------------------
# Routes
# ---------------------------
@app.route("/")
def home():
    return render_template("index.html", countries=COUNTRY_BASELINES.keys())

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    country = data["country"]
    income = float(data["income"])
    education = float(data["education"])
    employment = float(data["employment"])

    baseline = COUNTRY_BASELINES.get(country, 15000)
    normalized_income = income / baseline

    features = [[normalized_income, education, employment]]
    probability = model.predict_proba(features)[0][1]

    return jsonify({
        "risk_probability": round(probability * 100, 2),
        "status": "High Poverty Risk" if probability > 0.5 else "Low Poverty Risk",
        "baseline": baseline
    })

# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
