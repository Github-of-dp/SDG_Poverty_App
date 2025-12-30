from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)

# Load dataset
df = pd.read_csv("poverty_data.csv")

# Train model (NO household_size)
X = df[['income', 'education', 'employment']]
y = df['poverty_risk']

model = LogisticRegression()
model.fit(X, y)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    income = float(data["income"])
    education = float(data["education"])
    employment = float(data["employment"])

    prediction = model.predict_proba([[income, education, employment]])[0][1]
    risk_percent = round(prediction * 100, 2)

    return jsonify({
        "risk": risk_percent,
        "status": "High Poverty Risk" if risk_percent > 50 else "Low Poverty Risk"
    })

if __name__ == "__main__":
    app.run(debug=True)
