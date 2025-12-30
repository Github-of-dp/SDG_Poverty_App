from flask import Flask, render_template, request
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# Load dataset
df = pd.read_csv("poverty_data.csv")

X = df[['income', 'education', 'employment']]
y = df['poverty_risk']

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train model
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None

    if request.method == "POST":
        income = float(request.form["income"])
        education = float(request.form["education"])
        employment = float(request.form["employment"])

        input_data = scaler.transform([[income, education, employment]])
        result = model.predict(input_data)[0]

        prediction = "At Poverty Risk" if result == 1 else "Not At Risk"

    return render_template("index.html", prediction=prediction)

if __name__ == "__main__":
    app.run()
