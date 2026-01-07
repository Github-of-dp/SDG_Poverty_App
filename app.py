from flask import Flask, render_template, request, jsonify
from sklearn.linear_model import LogisticRegression
import numpy as np

app = Flask(__name__)

# --------------------------------------------------
# COUNTRY POVERTY LINES (ANNUAL, LOCAL CURRENCY)
# --------------------------------------------------
POVERTY_LINE = {
    "India": 10000,
    "USA": 15000,
    "UK": 14000,
    "UAE": 16000,
    "Nigeria": 1200,
    "Brazil": 4000
}

HELP_SUGGESTIONS = {
    "India": "Explore government welfare schemes, skill development programs, and local NGOs.",
    "USA": "Look into SNAP benefits, job reskilling programs, and community support services.",
    "UK": "Check Universal Credit support and employment training programs.",
    "UAE": "Explore workforce upskilling initiatives and social support entities.",
    "Nigeria": "Seek NGO assistance, microfinance programs, and vocational training.",
    "Brazil": "Look into Bolsa Família programs and employment support services."
}

# --------------------------------------------------
# SIMPLE LOGISTIC REGRESSION (SECONDARY AI LAYER)
# --------------------------------------------------
# Trained on logical synthetic patterns
X_train = np.array([
    [0, 0, 0],
    [2000, 5, 0],
    [5000, 8, 0],
    [8000, 10, 1],
    [10000, 12, 1],
    [15000, 15, 1],
    [25000, 18, 1]
])

y_train = np.array([1, 1, 1, 0, 0, 0, 0])

model = LogisticRegression()
model.fit(X_train, y_train)

# --------------------------------------------------
# ROUTES
# --------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    income = float(request.form["income"])
    income = max(0, income)  # no negative income
    education = float(request.form["education"])
    employment = int(request.form["employment"])
    country = request.form["country"]

    poverty_line = POVERTY_LINE.get(country, 10000)

    # --------------------------------------------------
    # LAYER 1: ECONOMIC REALITY (PRIMARY)
    # --------------------------------------------------
    if income == 0:
        base_risk = 95

    elif income < poverty_line:
        deficit_ratio = (poverty_line - income) / poverty_line
        base_risk = 70 + (deficit_ratio * 25)  # 70–95%

    else:
        surplus_ratio = (income - poverty_line) / poverty_line
        base_risk = max(10, 35 - surplus_ratio * 20)  # 10–35%

    # --------------------------------------------------
    # LAYER 2: ML ADJUSTMENT (SECONDARY)
    # --------------------------------------------------
    ai_prob = model.predict_proba([[income, education, employment]])[0][1]
    ai_adjustment = (ai_prob - 0.5) * 20  # mild influence

    risk = base_risk + ai_adjustment

    # --------------------------------------------------
    # LAYER 3: EDUCATION & EMPLOYMENT SAFETY LIMITS
    # --------------------------------------------------
    if income < poverty_line:
        risk = max(risk, 60)   # cannot be "low" if below poverty line

    risk -= education * 0.6
    risk -= employment * 8

    # Final clamp
    risk = min(100, max(5, risk))
    risk = round(risk, 2)

    # --------------------------------------------------
    # OUTPUT METADATA
    # --------------------------------------------------
    if risk < 35:
        level = "Low"
        color = "green"
    elif risk < 65:
        level = "Medium"
        color = "orange"
    else:
        level = "High"
        color = "red"

    comparison = (
        "Below national poverty threshold"
        if income < poverty_line
        else "Above national poverty threshold"
    )

    help_text = HELP_SUGGESTIONS.get(
        country,
        "Seek local government and community support programs."
    )

    return jsonify({
        "risk": risk,
        "level": level,
        "color": color,
        "comparison": comparison,
        "help": help_text
    })

if __name__ == "__main__":
    app.run(debug=True)
