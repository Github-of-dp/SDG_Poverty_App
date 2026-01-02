from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

# Sample dataset for demo (replace with real dataset if available)
poverty_data = pd.DataFrame({
    'country': ['India', 'USA', 'India', 'USA', 'India', 'USA'],
    'income': [15000, 3000, 12000, 4500, 20000, 5000],
    'education': [5, 10, 6, 12, 8, 14],
    'employment': [0, 1, 0, 1, 0, 1],
    'household_size': [4, 1, 3, 1, 5, 2],
    'poverty_risk': [1, 0, 1, 0, 1, 0]
})

# Country-specific poverty line (monthly USD)
poverty_lines = {
    'India': 150,  # USD/month
    'USA': 1200
}

# Country-specific help suggestions
help_suggestions = {
    'India': "Check government welfare schemes and local NGOs supporting low-income households.",
    'USA': "Check SNAP, Medicaid, and other local support programs."
}

# Global average income for comparison (USD/month)
global_avg_income = {
    'India': 500,
    'USA': 4000
}

@app.route('/')
def index():
    countries = list(poverty_lines.keys())
    return render_template('index.html', countries=countries)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    country = data['country']
    income = float(data['income'])
    household = int(data['household_size'])
    education = int(data['education'])
    employment = int(data['employment'])

    # Normalize income with country poverty line
    poverty_line = poverty_lines.get(country, 500)
    global_income = global_avg_income.get(country, 1000)

    # Risk formula
    base_risk = 100 - ((income / (household * poverty_line)) * 50)  # weight 50%
    edu_risk = max(0, 30 - (education * 1.5))  # higher education lowers risk
    emp_risk = 0 if employment else 15

    risk = base_risk + edu_risk + emp_risk
    risk = np.clip(risk, 0, 100)

    # Global comparison
    if income >= global_income:
        global_msg = "Your income is above the global average for your country."
    else:
        global_msg = "Your income is below the global average for your country."

    help_text = help_suggestions.get(country, "")

    return jsonify({
        'risk': round(risk, 1),
        'poverty_line': poverty_line,
        'global_msg': global_msg,
        'help_text': help_text
    })

if __name__ == '__main__':
    app.run(debug=True)
