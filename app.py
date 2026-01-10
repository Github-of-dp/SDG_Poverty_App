from flask import Flask, render_template, request, jsonify
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

app = Flask(__name__)

# --- STEP 1: MOCK MODEL (For development) ---
# In production, you'd load your trained model: joblib.load('model.pkl')
# Let's create a pipeline that mirrors real SDG-1 indicators
def create_trained_model():
    # Example features: [Education, Income, Household_Size, Access_to_Water]
    X_train = np.array([
        [0, 100, 8, 0], [12, 1000, 4, 1], [16, 3000, 2, 1], 
        [4, 200, 6, 0], [20, 5000, 1, 1], [8, 400, 5, 0]
    ])
    y_train = np.array([1, 1, 0, 1, 0, 1]) # 1 = Risk, 0 = Secure
    
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('logreg', LogisticRegression())
    ])
    pipeline.fit(X_train, y_train)
    return pipeline

model = create_trained_model()
feature_names = ['Education Level', 'Monthly Income', 'Family Size', 'Water/Tech Access']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        # Extract features from JSON request
        user_input = np.array([[
            float(data['education']),
            float(data['income']),
            float(data['family']),
            float(data['access'])
        ]])
        
        # Get Probability
        prob = model.predict_proba(user_input)[0][1]
        
        # Get Weights (Coefficients) to explain "WHY"
        # We multiply user input by coefficients to see what contributed most
        weights = model.named_steps['logreg'].coef_[0]
        contributions = {feature_names[i]: float(weights[i]) for i in range(len(feature_names))}
        
        return jsonify({
            'probability': round(prob * 100, 1),
            'risk_level': "High" if prob > 0.5 else "Low",
            'contributions': contributions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
