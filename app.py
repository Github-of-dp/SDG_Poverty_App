from flask import Flask, render_template, request
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# Load dataset
df = pd.read_csv("poverty_data.csv")

X = df.drop("poverty_risk", axis=1)
y = df["poverty_risk"]

# Scale data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_scaled, y)

@app.route("/", methods=["GET", "POST"])
def index():
    prediction_text = ""

    if request.method == "POST":
        income = float(request.form["income"])
        education = int(request.form["education"])
        employed = int(request.form["employed"])
        family_size = int(request.form["family_size"])
        facilities = int(request.form["facilities"])

        user_data = pd.DataFrame(
            [[income, education, employed, family_size, facilities]],
            columns=["income", "education", "employed", "family_size", "facilities"]
        )

        user_scaled = scaler.transform(user_data)
        prediction = model.predict(user_scaled)

        if prediction[0] == 1:
            prediction_text = "⚠️ Household is at Poverty Risk"
        else:
            prediction_text = "✅ Household is NOT at Poverty Risk"

    return render_template("index.html", result=prediction_text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)