from flask import Flask, render_template, request, jsonify
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

app = Flask(__name__)

# Mock Data for different regions to make it dynamic
country_stats = {
    "Global": {"baseline": 1.0, "desc": "Global Average Statistics"},
    "Nigeria": {"baseline": 1.8, "desc": "High dependency ratio region"},
    "India": {"baseline": 1.4, "desc": "Rapidly urbanizing economy"},
    "Brazil": {"baseline": 1.2, "desc": "Moderate income inequality focus"},
    "USA": {"baseline": 0.5, "desc": "High-cost urban poverty context"}
}

def create_model():
    # Training with slightly different weights for a more reactive feel
    X = np.array([[0, 100, 8, 0], [12, 1000, 4, 1], [16, 3000, 2, 1], [2, 50, 10, 0]])
    y = np.array([1, 1, 0, 1])
    pipeline = Pipeline([('scaler', StandardScaler()), ('logreg', LogisticRegression())])
    pipeline.fit(X, y)
    return pipeline

model = create_model()

@app.route('/')
def index():
    return render_template('index.html', countries=country_stats)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    country = data.get('country', 'Global')
    multiplier = country_stats.get(country, country_stats['Global'])['baseline']
    
    user_input = np.array([[
        float(data['education']),
        float(data['income']),
        float(data['family']),
        float(data['access'])
    ]])
    
    # Calculate base probability and adjust by country baseline
    base_prob = model.predict_proba(user_input)[0][1]
    adjusted_prob = min(0.99, base_prob * multiplier) 

    return jsonify({
        'probability': round(adjusted_prob * 100, 1),
        'impacts': list(model.named_steps['logreg'].coef_[0])
    })

if __name__ == '__main__':
    app.run(debug=True)
