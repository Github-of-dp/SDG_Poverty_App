from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

# Logic weights tailored for the UAE context
# Weights: [Education, Income, Family, Access]
country_data = {
    "Global": {"weight": [-0.5, -0.002, 0.8, -1.2], "intercept": 2.0, "tips": "Focus on education and community resources."},
    "UAE": {
        "weight": [-0.9, -0.0003, 0.5, -2.0], 
        "intercept": 1.5, 
        "tips": "Explore the Nafis program for career growth and local entrepreneurship grants."
    },
    "India": {"weight": [-0.7, -0.008, 0.9, -1.5], "intercept": 2.5, "tips": "Explore digital literacy programs and urban job portals."},
    "USA": {"weight": [-1.2, -0.0005, 0.4, -3.0], "intercept": 1.0, "tips": "Utilize community college paths and internet subsidy programs."}
}

@app.route('/')
def index():
    return render_template('index.html', countries=country_data.keys())

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    c_type = data.get('country', 'Global')
    config = country_data.get(c_type, country_data['Global'])
    
    # Inputs from sliders
    inputs = np.array([float(data['edu']), float(data['income']), float(data['family']), float(data['access'])])
    
    # Logistic Regression Calculation (Sigmoid Function)
    z = config['intercept'] + np.dot(inputs, config['weight'])
    prob = 1 / (1 + np.exp(-z))
    
    # Personalized Advice based on UAE context
    advice = config['tips']
    if c_type == "UAE" and float(data['edu']) < 12:
        advice = "💡 Tip: Higher education is a key driver for career stability in the UAE's private sector."
    elif float(data['access']) == 0:
        advice = "🌐 Tip: Digital inclusion is essential for accessing government e-services and remote work."

    return jsonify({
        'prob': round(prob * 100),
        'advice': advice
    })

if __name__ == '__main__':
    app.run(debug=True)
