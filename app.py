from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)

# Dataset
data = pd.read_csv("poverty_data.csv")
X = data[["income", "education", "employment"]]
y = data["poverty_risk"]

model = LogisticRegression()
model.fit(X, y)

# Country normalization factors (educational)
COUNTRY_FACTORS = {
    "India": 0.35,
    "USA": 1.0,
    "UK": 0.9,
    "UAE": 0.8,
    "Nigeria": 0.25
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    income = float(data["income"])
    education = float(data["education"])
    employment = int(data["employment"])
    country = data["country"]

    factor = COUNTRY_FACTORS.get(country, 1.0)
    normalized_income = income / factor

    pred = model.predict([[normalized_income, education, employment]])[0]
    prob = model.predict_proba([[normalized_income, education, employment]])[0][1]

    return jsonify({
        "risk": int(pred),
        "probability": round(prob * 100, 1),
        "normalized_income": round(normalized_income, 2)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
