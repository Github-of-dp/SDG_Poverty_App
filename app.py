from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

# -----------------------------
# Sample poverty dataset (simplified for demo)
# Columns: income, education, employment, country, household_size, poverty_risk
poverty_data = pd.DataFrame([
    {'income':15000, 'education':5, 'employment':0, 'household_size':1, 'country':'India', 'poverty_risk':1},
    {'income':30000, 'education':10, 'employment':1, 'household_size':2, 'country':'India', 'poverty_risk':0},
    {'income':12000, 'education':6, 'employment':0, 'household_size':1, 'country':'India', 'poverty_risk':1},
    {'income':45000, 'education':12, 'employment':1, 'household_size':3, 'country':'USA', 'poverty_risk':0},
    {'income':20000, 'education':8, 'employment':0, 'household_size':2, 'country':'India', 'poverty_risk':1},
    {'income':50000, 'education':14, 'employment':1, 'household_size':4, 'country':'USA', 'poverty_risk':0},
])

# Country poverty line for normalization (monthly income)
COUNTRY_POVERTY_LINE = {
    'India': 10000,
    'USA': 4000,
    'UK': 3500,
    'Germany': 3300,
    'Brazil': 1200,
    'Nigeria': 500,
}

# Feature B: country-specific help suggestions
HELP_SUGGESTIONS = {
    'India': ['Check govt. welfare programs', 'Skill development courses available'],
    'USA': ['Check SNAP benefits', 'Explore job retraining programs'],
    'UK': ['Visit Universal Credit services', 'Seek local housing assistance'],
    'Germany': ['Check Sozialhilfe benefits', 'Vocational training programs'],
    'Brazil': ['Access Bolsa Família support', 'Local skill workshops'],
    'Nigeria': ['Check N-Power programs', 'Community support initiatives'],
}

# -----------------------------
def calculate_risk(income, education, employment, household_size, country):
    # Normalize income using country poverty line
    poverty_line = COUNTRY_POVERTY_LINE.get(country, 1000)
    normalized_income = income / (household_size * poverty_line)
    
    # Risk calculation formula
    risk = 100 - (normalized_income * 50) - (education * 5) - (employment * 10)
    risk = np.clip(risk, 0, 100)
    
    return round(risk, 1), poverty_line

@app.route('/')
def index():
    countries = list(COUNTRY_POVERTY_LINE.keys())
    return render_template('index.html', countries=countries)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    income = float(data.get('income', 0))
    household_size = float(data.get('household_size', 1))
    education = float(data.get('education', 0))
    employment = int(data.get('employment', 0))
    country = data.get('country', 'India')

    risk, poverty_line = calculate_risk(income, education, employment, household_size, country)
    status = "High Poverty Risk" if risk > 50 else "Low Poverty Risk"
    help_tips = HELP_SUGGESTIONS.get(country, [])
    
    return jsonify({
        'risk': risk,
        'status': status,
        'poverty_line': poverty_line,
        'help_tips': help_tips
    })

if __name__ == '__main__':
    app.run(debug=True)
