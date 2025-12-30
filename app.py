from flask import Flask, render_template, request
import pandas as pd
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)

CSV_FILE = "poverty_data.csv"

# Load dataset
df = pd.read_csv(CSV_FILE)

# Check if household_size exists, else add default 1
if 'household_size' not in df.columns:
    df['household_size'] = 1

# Prepare features and target
X = df[['income', 'education', 'employment', 'household_size']]
y = df['poverty_risk']

# Train model
model = LogisticRegression(max_iter=500)
model.fit(X, y)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    # Get form data
    income = float(request.form['income'])
    education = float(request.form['education'])
    employment = int(request.form['employment'])
    household_size = int(request.form['household_size'])

    # Make prediction
    prediction = model.predict([[income, education, employment, household_size]])[0]
    risk = "at Poverty Risk" if prediction == 1 else "not at Poverty Risk"

    # Save new data to CSV
    new_row = pd.DataFrame([[income, education, employment, household_size, prediction]],
                           columns=['income','education','employment','household_size','poverty_risk'])
    new_row.to_csv(CSV_FILE, mode='a', header=False, index=False)

    return render_template("index.html", result=f"Household is {risk}")

if __name__ == "__main__":
    app.run(debug=True)
