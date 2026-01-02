from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# ---------------- DATA + MODEL ----------------
data = pd.read_csv("poverty_data.csv")

X = data[["income", "education", "employment"]]
y = data["poverty_risk"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = LogisticRegression()
model.fit(X_scaled, y)

# ---------------- COUNTRY NORMALIZATION ----------------
COUNTRY_INCOME_INDEX = {
    "India": 0.4,
    "USA": 1.0,
    "UK": 0.9,
    "UAE": 1.1,
    "Nigeria": 0.3,
    "Brazil": 0.6
}

GLOBAL_AVG_INDEX = 1.0

# ---------------- HELP SUGGESTIONS ----------------
HELP_SUGGESTIONS = {
    "India": "Explore government welfare schemes, skill development programs, and local NGOs.",
    "USA": "Look into SNAP benefits, job reskilling programs, and community support services.",
    "UK": "Check Universal Credit support and employment training programs.",
    "UAE": "Explore workforce upskilling initiatives and social support entities.",
    "Nigeria": "Seek NGO assistance, microfinance programs, and vocational training.",
    "Brazil": "Look into Bolsa Família programs and employment support services."
}

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    income = float(request.form["income"])
    education = float(request.form["education"])
    employment = int(request.form["employment"])
    country = request.form["country"]

    index = COUNTRY_INCOME_INDEX.get(country, 1.0)
    normalized_income = income / index

    features = scaler.transform([[normalized_income, education, employment]])
    probability = model.predict_proba(features)[0][1]
    risk_percent = round(probability * 100, 2)

    # Risk label
    if risk_percent < 35:
        level = "Low"
        color = "green"
    elif risk_percent < 65:
        level = "Medium"
        color = "orange"
    else:
        level = "High"
        color = "red"

    # Global comparison
    comparison = (
        "Below global average" if index < GLOBAL_AVG_INDEX else
        "Near global average" if index == GLOBAL_AVG_INDEX else
        "Above global average"
    )

    help_text = HELP_SUGGESTIONS.get(country, "Seek local community and educational support.")

    return jsonify({
        "risk": risk_percent,
        "level": level,
        "color": color,
        "comparison": comparison,
        "help": help_text
    })

if __name__ == "__main__":
    app.run()
