from flask import Flask, render_template, request
import pandas as pd
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)
CSV_FILE = "poverty_data.csv"

# Load CSV and prepare model
df = pd.read_csv(CSV_FILE)
if 'household_size' not in df.columns:
    df['household_size'] = 1  # default if missing

X = df[['income', 'education', 'employment', 'household_size']]
y = df['poverty_risk']

model = LogisticRegression(max_iter=500)
model.fit(X, y)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", risk_status=None, risk_prob=None)

@app.route("/predict", methods=["POST"])
def predict():
    # Get form data
    income = float(request.form['income'])
    household_size = int(request.form['household_size'])
    education = float(request.form['education'])
    employment = int(request.form['employment'])

    # Predict probability
    prob = model.predict_proba([[income, education, employment, household_size]])[0][1] * 100
    status = "High Poverty Risk" if prob > 50 else "Low Poverty Risk"

    # Append new data to CSV
    new_row = pd.DataFrame([[income, education, employment, household_size, int(prob > 50)]],
                           columns=['income','education','employment','household_size','poverty_risk'])
    new_row.to_csv(CSV_FILE, mode='a', header=False, index=False)

    return render_template("index.html", risk_status=status, risk_prob=f"{prob:.1f}%")

if __name__ == "__main__":
    app.run(debug=True)
