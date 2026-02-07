from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
import traceback

app = Flask(__name__)

# Load the trained model (includes preprocessing pipeline)
model = joblib.load("model.pkl")

# Expected columns (for validation only, not preprocessing)
EXPECTED_COLUMNS = [
    'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'tenure',
    'PhoneService', 'MultipleLines', 'InternetService', 'OnlineSecurity',
    'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV',
    'StreamingMovies', 'Contract', 'PaperlessBilling', 'PaymentMethod',
    'MonthlyCharges', 'TotalCharges'
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Make predictions using the trained Pipeline model.
    
    The model.pkl already includes preprocessing (imputing, encoding, scaling).
    We pass RAW DATA directly - no manual preprocessing!
    """
    try:
        # Get form data
        data = request.form.to_dict()
        customer_id = data.pop('customerID', None)
        
        # ✓ CORRECT: Create DataFrame with raw data
        input_df = pd.DataFrame([data])
        
        # ✓ Validate input structure (not values - Pipeline handles that)
        missing_columns = [col for col in EXPECTED_COLUMNS if col not in input_df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Select only expected columns in correct order
        input_df = input_df[EXPECTED_COLUMNS]
        
        # ✓ CORRECT: Pass raw data directly to model
        # The Pipeline inside model.pkl handles all preprocessing:
        # - ColumnTransformer applies appropriate transformations
        # - SimpleImputer handles missing values
        # - OneHotEncoder handles categorical variables
        # - StandardScaler handles numeric scaling
        # - LogisticRegression makes the prediction
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]
        
        churn_label = "Yes" if prediction == 1 else "No"
        
        return render_template('predict.html', 
                             churn=churn_label,
                             probability=f"{probability*100:.2f}%",
                             customer_id=customer_id,
                             data=data,
                             success=True)
    
    except ValueError as e:
        # Missing or invalid columns
        return render_template('predict.html',
                             error=f"Input Error: {str(e)}",
                             data={},
                             success=False)
    
    except Exception as e:
        # Other errors (model loading, prediction, etc.)
        error_msg = f"Prediction Error: {str(e)}"
        app.logger.error(f"Prediction failed: {traceback.format_exc()}")
        return render_template('predict.html',
                             error=error_msg,
                             data={},
                             success=False)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    API endpoint for programmatic predictions (returns JSON).
    Same preprocessing logic - Pipeline handles everything.
    """
    try:
        json_data = request.get_json()
        customer_id = json_data.pop('customerID', None)
        
        input_df = pd.DataFrame([json_data])
        
        # Validate columns
        missing_columns = [col for col in EXPECTED_COLUMNS if col not in input_df.columns]
        if missing_columns:
            return jsonify({
                'error': f"Missing columns: {', '.join(missing_columns)}",
                'success': False
            }), 400
        
        input_df = input_df[EXPECTED_COLUMNS]
        
        # Predict
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]
        
        return jsonify({
            'success': True,
            'customer_id': customer_id,
            'churn_prediction': 'Yes' if prediction == 1 else 'No',
            'churn_probability': float(probability),
            'confidence': f"{probability*100:.2f}%"
        })
    
    except Exception as e:
        app.logger.error(f"API prediction failed: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

if __name__ == '__main__':
    # In production, use a proper WSGI server (gunicorn, waitress, etc.)
    # Not Flask's development server!
    app.run(debug=True, port=5000)
