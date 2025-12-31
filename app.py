from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)

# Load dataset
data = pd.read_csv("poverty_data.csv")

X = data[["income", "education", "employment"]]
y = data["poverty_risk"]

model = LogisticRegression()
model.fit(X, y)

# Home route (THIS FIXES 404)
@app.route("/")
def home():
    return render_template("index.html")

# Prediction API
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    income = data["income"]
    education = data["education"]
    employment = data["employment"]

    prediction = model.predict([[income, education, employment]])[0]
    probability = model.predict_proba([[income, education, employment]])[0][1]

    return jsonify({
        "poverty_risk": int(prediction),
        "probability": round(probability * 100, 2)
    })

if __name__ == "__main__":
    app.run(debug=True)
