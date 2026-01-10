from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

# Logic weights tailored for the UAE context
country_data = {
    "UAE": {
        "weight": [-0.9, -0.0003, 0.5, -2.0], 
        "intercept": 1.5, 
        "tips": "Explore the Nafis program for career growth and local entrepreneurship grants."
    },
    "Global": {
        "weight": [-0.5, -0.002, 0.8, -1.2], 
        "intercept": 2.0, 
        "tips": "Focus on education and community resources."
    },
    "India": {
        "weight": [-0.7, -0.008, 0.9, -1.5], 
        "intercept": 2.5, 
        "tips": "Explore digital literacy programs and urban job portals."
    },
    "USA": {
        "weight": [-1.2, -0.0005, 0.4, -3.0], 
        "intercept": 1.0, 
        "tips": "Utilize community college paths and internet subsidy programs."
    }
}

@app.route('/')
def index():
    # FIXED: Sending the whole dictionary, not just the keys
    return render_template('index.html', countries=country_data)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    c_type = data.get('country', 'Global')
    config = country_data.get(c_type, country_data['Global'])
    
    inputs = np.array([float(data['edu']), float(data['inc']), float(data['family']), float(data['access'])])
    
    z = config['intercept'] + np.dot(inputs, config['weight'])
    prob = 1 / (1 + np.exp(-z))
    
    advice = config['tips']
    if c_type == "UAE" and float(data['edu']) < 12:
        advice = "💡 Tip: Higher education is a key driver for career stability in the UAE."

    return jsonify({
        'prob': int(round(prob * 100)),
        'advice': advice
    })

if __name__ == '__main__':
    app.run(debug=True)
