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

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        user_data = request.get_json()

        income = float(user_data["income"])
        education = float(user_data["education"])
        employment = int(user_data["employment"])

        prediction = model.predict([[income, education, employment]])[0]
        probability = model.predict_proba([[income, education, employment]])[0][1]

        return jsonify({
            "poverty_risk": int(prediction),
            "probability": round(probability * 100, 1)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
