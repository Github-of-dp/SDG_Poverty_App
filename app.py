from flask import Flask, render_template, request
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# Load dataset
df = pd.read_csv("poverty_data.csv")

# Features and target
X = df[['income', 'education', 'employment', 'household_size']]
y = df['poverty_risk']

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train Logistic Regression model
model = LogisticRegression(max_iter=1000)
model.fit(X_scaled, y)

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    probability = None
    poverty_line = 20000  # Example official poverty line
    source = "World Bank $2.15/day (2025)"

    if request.method == "POST":
        income = float(request.form["income"])
        education = float(request.form["education"])
        employment = float(request.form["employment"])
        household_size = float(request.form["household_size"])

        input_data = scaler.transform([[income, education, employment, household_size]])
        result_prob = model.predict_proba(input_data)[0][1]
        result = model.predict(input_data)[0]

        # Display risk % and safe wording
        probability = round(result_prob * 100, 2)
        prediction = "Below poverty line" if result == 1 else "Above poverty line"

    return render_template(
        "index.html",
        prediction=prediction,
        probability=probability,
        poverty_line=poverty_line,
        source=source
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
