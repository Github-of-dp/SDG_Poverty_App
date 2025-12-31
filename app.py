from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import numpy as np

app = Flask(__name__)

# -----------------------------
# Country-based poverty lines (monthly, approx)
# -----------------------------
POVERTY_LINES = {
    "India": 8000,
    "USA": 1100,
    "UK": 900,
    "UAE": 3000
}

# -----------------------------
# Load dataset
# -----------------------------
df = pd.read_csv("poverty_data.csv")

X = df[['income', 'education', 'employment']]
y = df['poverty_risk']

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_scaled, y)

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html", countries=POVERTY_LINES.keys())

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    income = float(data["income"])
    education = float(data["education"])
    employment = float(data["employment"])
    country = data["country"]

    poverty_line = POVERTY_LINES[country]

    # Normalize income by country poverty line
    normalized_income = income / poverty_line

    features = np.array([[normalized_income, education, employment]])
    features_scaled = scaler.transform(features)

    probability = model.predict_proba(features_scaled)[0][1] * 100

    status = "High Poverty Risk" if probability > 50 else "Low Poverty Risk"

    return jsonify({
        "risk": round(probability, 2),
        "status": status,
        "poverty_line": poverty_line
    })

if __name__ == "__main__":
    app.run(debug=True)
