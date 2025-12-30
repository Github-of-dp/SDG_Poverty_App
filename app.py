from flask import Flask, render_template, request
import pandas as pd
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)
CSV_FILE = "poverty_data.csv"

# Load CSV and train model
df = pd.read_csv(CSV_FILE)
if 'household_size' not in df.columns:
    df['household_size'] = 1

X = df[['income', 'education', 'employment', 'household_size']]
y = df['poverty_risk']
model = LogisticRegression(max_iter=500)
model.fit(X, y)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    income = float(request.form['income'])
    household_size = float(request.form['household_size'])
    education = float(request.form['education'])
    employment = int(request.form['employment'])

    prob = model.predict_proba([[income, education, employment, household_size]])[0][1] * 100
    status = "High Poverty Risk" if prob > 50 else "Low Poverty Risk"

    # Append new data to CSV
    new_row = pd.DataFrame([[income, education, employment, household_size, int(prob > 50)]],
                           columns=['income','education','employment','household_size','poverty_risk'])
    new_row.to_csv(CSV_FILE, mode='a', header=False, index=False)

    return {"status": status, "probability": round(prob, 1)}
    
if __name__ == "__main__":
    app.run(debug=True)
