from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

# Regional Configs: Weights [Edu, Inc, Fam, Acc], Intercept, and Currency
country_data = {
    "UAE": {
        "weight": [-0.2, -0.0005, 0.4, -0.5], 
        "intercept": 2.5, # Higher intercept means higher base risk
        "currency": "AED",
        "tips": "Explore the Nafis program for career growth in the private sector."
    },
    "Global": {
        "weight": [-0.15, -0.001, 0.6, -0.4], 
        "intercept": 3.0,
        "currency": "USD",
        "tips": "Focus on vocational training and community support networks."
    },
    "India": {
        "weight": [-0.1, -0.002, 0.5, -0.3], 
        "intercept": 3.5,
        "currency": "INR",
        "tips": "Look into digital literacy and urban livelihood missions."
    },
    "USA": {
        "weight": [-0.3, -0.0002, 0.3, -0.8], 
        "intercept": 1.5,
        "currency": "USD",
        "tips": "Utilize state-level social safety nets and educational grants."
    }
}

@app.route('/')
def index():
    return render_template('index.html', countries=country_data)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    c_type = data.get('country', 'Global')
    config = country_data.get(c_type, country_data['Global'])
    
    # Inputs
    edu = float(data['edu'])
    inc = float(data['inc'])
    fam = float(data['family'])
    acc = float(data['access'])
    
    # --- FIXED LOGIC ---
    # z = intercept + (w1*edu) + (w2*inc) + (w3*fam) + (w4*acc)
    w = config['weight']
    z = config['intercept'] + (w[0]*edu) + (w[1]*inc) + (w[2]*fam) + (w[3]*acc)
    
    # Sigmoid Function
    prob = 1 / (1 + np.exp(-z))
    
    # Safety Check: If income is 0, the risk cannot be low.
    if inc < 100:
        prob = max(prob, 0.85) # Minimum 85% risk if income is near zero

    return jsonify({
        'prob': int(round(prob * 100)),
        'advice': config['tips'],
        'currency': config['currency']
    })

if __name__ == '__main__':
    app.run(debug=True)
