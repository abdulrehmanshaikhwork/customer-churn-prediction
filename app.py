from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
import traceback

app = Flask(__name__)

# Load the trained model (includes preprocessing pipeline)
model = joblib.load("model.pkl")

# Expected columns for validation only (not for preprocessing)
# The Pipeline inside model.pkl handles all preprocessing!
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
    
    ✓ CORRECT APPROACH:
    The model.pkl already includes preprocessing (imputing, encoding, scaling).
    We pass RAW DATA directly - NO manual preprocessing!
    
    ✗ WRONG (what was here before):
    Manual pd.to_numeric(), mapping Yes/No→1/0, etc. caused preprocessing twice
    and mismatches between training and inference.
    """
    try:
        # Get form data (raw values as strings)
        data = request.form.to_dict()
        customer_id = data.pop('customerID', None)
        
        # Create DataFrame with raw data - NOTHING MORE!
        input_df = pd.DataFrame([data])
        
        # Validate structure (check columns exist, not validate values)
        missing_columns = [col for col in EXPECTED_COLUMNS if col not in input_df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Select only expected columns in correct order
        input_df = input_df[EXPECTED_COLUMNS]
        
        # ✓ CORRECT: Pass raw data directly to model
        # The Pipeline inside model.pkl handles ALL preprocessing:
        # - Converts numeric columns (SeniorCitizen, tenure, MonthlyCharges, TotalCharges)
        # - Encodes categorical variables (Partner "Yes"→1, "No"→0 via OneHotEncoder)
        # - Handles missing values (SimpleImputer)
        # - Scales numeric features (StandardScaler)
        # - Makes prediction (LogisticRegression)
        # ALL in one call, consistent with training!
        
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]
        
        churn_label = "Yes" if prediction == 1 else "No"
        prob_percentage = probability * 100
        
        # Determine risk level based on probability
        if prob_percentage < 30:
            risk_level = "low"
            risk_message = "VERY LOW RISK"
        elif prob_percentage < 50:
            risk_level = "medium"
            risk_message = "MEDIUM RISK"
        elif prob_percentage < 70:
            risk_level = "high"
            risk_message = "HIGH RISK"
        else:
            risk_level = "very-high"
            risk_message = "VERY HIGH RISK"
        
        return render_template('predict.html', 
                             churn=churn_label,
                             probability=f"{prob_percentage:.2f}%",
                             prob_percentage=prob_percentage,
                             risk_level=risk_level,
                             risk_message=risk_message,
                             customer_id=customer_id,
                             data=data,
                             success=True)
    
    except ValueError as e:
        # Missing or invalid input structure
        return render_template('predict.html',
                             error=f"Input Error: {str(e)}",
                             data={},
                             success=False)
    
    except Exception as e:
        # Model or prediction errors
        app.logger.error(f"Prediction failed: {traceback.format_exc()}")
        return render_template('predict.html',
                             error=f"Error: {str(e)}",
                             data={},
                             success=False)

if __name__ == '__main__':
    # In production, use a proper WSGI server (gunicorn, waitress, etc.)
    # NOT Flask's development server!
    app.run(debug=True, port=5000)
