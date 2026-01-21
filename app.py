from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

# --- AI MODEL CONFIGURATION ---
# These are the "Weights" (W) and "Bias" (B) for our Logistic Regression.
# In a real app, these come from training on a dataset like the World Bank MPI.
W = np.array([-0.0004, -0.35, 0.75]) # [Income, Education, Dependency]
B = 2.0 

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    
    # 1. Feature Extraction (X)
    income = float(data['income'])
    edu = float(data['education'])
    # Structural load = Household members per worker
    dep = float(data['h_size']) / max(1, float(data['workers']))
    
    X = np.array([income, edu, dep])
    
    # 2. Logistic Regression Calculation: z = (W * X) + B
    z = np.dot(W, X) + B
    probability = sigmoid(z)
    risk_percent = round(probability * 100, 1)
    
    # 3. Decision Logic
    classification = "Vulnerable" if probability > 0.5 else "Resilient"
    
    # AI Analysis: Find the highest risk contributor
    impacts = W * X
    factors = ["Income Gap", "Education Gap", "Structural Load"]
    primary_driver = factors[np.argmax(impacts)]

    return jsonify({
        "risk": risk_percent,
        "class": classification,
        "insight": f"AI Diagnostic: {primary_driver} is the strongest predictor of vulnerability in this profile.",
        "weights": {"Income": W[0], "Edu": W[1], "Dep": W[2]}
    })

if __name__ == "__main__":
    app.run(debug=True)