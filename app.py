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

# ---------------- COUNTRY INCOME & CURRENCY ----------------
COUNTRY_INCOME_INDEX = {
    "India": 15000,   # average monthly poverty line in INR
    "USA": 1200,      # USD
    "UK": 900,        # GBP
    "UAE": 4500,      # AED
    "Nigeria": 150000, # NGN
    "Brazil": 500     # BRL
}

CURRENCY_CONVERSION = {
    "India": 1,      # INR → INR
    "USA": 82,       # USD → INR
    "UK": 100,       # GBP → INR
    "UAE": 22,       # AED → INR
    "Nigeria": 0.18, # NGN → INR
    "Brazil": 16     # BRL → INR
}

GLOBAL_AVG_INDEX = 1.0  # For comparison bar

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
    # Get user input
    income = float(request.form["income"])
    education = float(request.form["education"])
    employment = int(request.form["employment"])
    country = request.form["country"]

    # ---------------- Convert income to base currency (INR) ----------------
    conversion_rate = CURRENCY_CONVERSION.get(country, 1)
    income_in_base = income * conversion_rate

    # ---------------- Country-normalized income ----------------
    country_poverty_line = COUNTRY_INCOME_INDEX.get(country, 15000)
    normalized_income = income_in_base / country_poverty_line  # <1 → below poverty line, >1 → above

    # ---------------- Feature vector for model ----------------
    features = scaler.transform([[normalized_income * 15000, education, employment]])  # rescale to training scale
    probability = model.predict_proba(features)[0][1]
    risk_percent = round(probability * 100, 2)

    # ---------------- Rule-based boost for very low incomes ----------------
    if normalized_income < 0.2:   # income <20% of poverty line
        risk_percent = max(risk_percent, 90)
    elif normalized_income < 0.5: # income <50% of poverty line
        risk_percent = max(risk_percent, 70)
    elif normalized_income < 0.8: # income <80% of poverty line
        risk_percent = max(risk_percent, 50)

    # Risk label & color
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
        "Below global average" if normalized_income < GLOBAL_AVG_INDEX else
        "Near global average" if normalized_income == GLOBAL_AVG_INDEX else
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
