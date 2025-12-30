from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)

# Load dataset
data = pd.read_csv("poverty_data.csv")

X = data[['income', 'education', 'employment']]
y = data['poverty_risk']

model = LogisticRegression()
model.fit(X, y)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    income = float(data['income'])
    education = float(data['education'])
    employment = float(data['employment'])

    prob = model.predict_proba([[income, education, employment]])[0][1]
    risk_percent = round(prob * 100, 2)

    status = "High Poverty Risk" if risk_percent > 50 else "Low Poverty Risk"

    return jsonify({
        "risk": risk_percent,
        "status": status
    })

@app.route('/budget', methods=['POST'])
def budget():
    data = request.json
    income = float(data['income'])
    expenses = float(data['expenses'])

    remaining = income - expenses
    suggestion = "Good savings habit 👍" if remaining > income * 0.2 else "Try reducing expenses"

    return jsonify({
        "remaining": remaining,
        "suggestion": suggestion
    })

@app.route('/trends')
def trends():
    return jsonify({
        "income": data['income'].tolist(),
        "risk": data['poverty_risk'].tolist()
    })

@app.route('/recommendations', methods=['POST'])
def recommendations():
    risk = float(request.json['risk'])

    if risk > 70:
        tips = [
            "Apply for government welfare schemes",
            "Focus on skill-based education",
            "Reduce non-essential expenses"
        ]
    else:
        tips = [
            "Maintain consistent savings",
            "Invest in education or upskilling",
            "Track expenses monthly"
        ]

    return jsonify({"tips": tips})

if __name__ == "__main__":
    app.run(debug=True)
