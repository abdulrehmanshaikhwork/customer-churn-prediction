# Before vs After: Fixing Manual Preprocessing

## ✗ WRONG: Manual Preprocessing (Your Original Code)

```python
# app.py - INCORRECT APPROACH ❌

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.form.to_dict()
        customer_id = data.pop('customerID', None)
        
        input_df = pd.DataFrame([data])
        
        # ❌ PROBLEM 1: Manual numeric conversion
        numeric_cols = ['SeniorCitizen', 'tenure', 'MonthlyCharges', 'TotalCharges']
        for col in numeric_cols:
            if col in input_df.columns:
                input_df[col] = pd.to_numeric(input_df[col], errors='coerce')
        
        # ❌ PROBLEM 2: Manual Yes/No → 0/1 mapping
        # This CONFLICTS with Pipeline's OneHotEncoder!
        yes_no_cols = ['Partner', 'Dependents', 'PhoneService', 'PaperlessBilling']
        for col in yes_no_cols:
            if col in input_df.columns:
                # Convert "Yes" → 1, "No" → 0
                input_df[col] = input_df[col].map({"Yes": 1, "No": 0})
        
        # ❌ PROBLEM 3: Now preprocessing happens TWICE
        # Once here: "Yes" → 1
        # Again in Pipeline: 1 → [0, 1] (OneHotEncoder expects "Yes"/"No")
        prediction = model.predict(input_df)[0]
        
        # Result: WRONG PREDICTION due to data mismatch!
```

**Why This Is Wrong:**

1. **Training time:** Data goes Raw → Pipeline preprocessing → Model learned
2. **Inference time:** Data goes Raw → Manual preprocessing → Pipeline preprocessing → Different than training!

```
Training:
"Partner": "Yes" 
  ↓
Pipeline.OneHotEncoder
  ↓ 
[1, 0] (trained on this)

Inference:
"Partner": "Yes"
  ↓
Manual: map to 1
  ↓
Pipeline.OneHotEncoder (expects "Yes"/"No", gets 1)
  ↓
[WRONG ENCODING] (not what model learned!)
```

---

## ✓ CORRECT: Using Pipeline for Everything

```python
# app.py - CORRECT APPROACH ✅

@app.route('/predict', methods=['POST'])
def predict():
    """
    Make predictions using the trained Pipeline model.
    
    ✓ CORRECT: Pass RAW DATA to model
    The Pipeline handles all preprocessing internally!
    """
    try:
        # Get form data (raw values)
        data = request.form.to_dict()  # {"gender": "Male", "Partner": "Yes", ...}
        customer_id = data.pop('customerID', None)
        
        # Convert to DataFrame
        input_df = pd.DataFrame([data])
        
        # ✓ ONLY validate column presence, not values!
        missing_columns = [col for col in EXPECTED_COLUMNS 
                          if col not in input_df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns: {', '.join(missing_columns)}")
        
        # Select columns in correct order
        input_df = input_df[EXPECTED_COLUMNS]
        
        # ✓ Pass RAW data directly!
        # Pipeline handles EVERYTHING:
        # - pd.to_numeric() for numeric columns ← Pipeline does it!
        # - OneHotEncoding for "Yes"/"No" ← Pipeline does it!
        # - Imputing missing values ← Pipeline does it!
        # - StandardScaling ← Pipeline does it!
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]
        
        return render_template('predict.html',
                             churn='Yes' if prediction == 1 else 'No',
                             probability=f"{probability*100:.2f}%",
                             customer_id=customer_id,
                             data=data,
                             success=True)
```

**Why This Is Correct:**

```
Training:
"Partner": "Yes" 
  ↓
Pipeline.OneHotEncoder
  ↓ 
[1, 0] → Logistic Regression (learned on this)

Inference:
"Partner": "Yes"
  ↓
Pipeline.OneHotEncoder (same as training!)
  ↓
[1, 0] → Logistic Regression (same encoding!)
  ↓
✓ CORRECT PREDICTION!
```

---

## What the Pipeline Actually Does

Inside your `model.pkl` (the entire Pipeline):

```python
Pipeline([
    ('preprocessing', ColumnTransformer([
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ]), ['tenure', 'MonthlyCharges', 'TotalCharges', 'SeniorCitizen']),
        
        ('cat', Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', drop='first'))
        ]), ['gender', 'Partner', 'Dependents', 'PhoneService', ...])
    ])),
    
    ('classifier', LogisticRegression(max_iter=1000, class_weight='balanced'))
])
```

When you call `model.predict(raw_data)`:
1. ColumnTransformer routes data to appropriate pipelines
2. Numeric columns: Imputed → Scaled
3. Categorical columns: Imputed → OneHotEncoded
4. Logistic Regression makes prediction

**You DON'T need to do any of this manually!**

---

## Real Data Flow Comparison

### ✗ WRONG APPROACH (Original)
```
Input Form: "Partner: Yes"
  ↓
DataFrame: "Partner": "Yes"
  ↓
MANUAL: input_df['Partner'] = input_df['Partner'].map({"Yes": 1})
  ↓
DataFrame: "Partner": 1
  ↓
model.predict() 
  ↓
PIPELINE OneHotEncoder receives 1 (not "Yes"!)
  ↓
Wrong encoding
  ↓
Wrong prediction ❌
```

### ✓ CORRECT APPROACH
```
Input Form: "Partner: Yes"
  ↓
DataFrame: "Partner": "Yes"
  ↓
model.predict()
  ↓
PIPELINE OneHotEncoder receives "Yes"
  ↓
Correct encoding
  ↓
Correct prediction ✓
```

---

## Data Validation: Right vs Wrong

### ✗ Wrong: Validating individual values
```python
# Don't do this:
if input_df['tenure'].notna().all():
    input_df['tenure'] = pd.to_numeric(input_df['tenure'])
    
if input_df['Partner'].isin(['Yes', 'No']).all():
    input_df['Partner'] = input_df['Partner'].map({"Yes": 1, "No": 0})
```

### ✓ Correct: Validating structure only
```python
# Do this:
EXPECTED_COLUMNS = ['tenure', 'Partner', 'gender', ...]

missing = [col for col in EXPECTED_COLUMNS if col not in input_df.columns]
if missing:
    raise ValueError(f"Missing: {missing}")

# Pipeline handles value validation internally!
```

---

## Key Takeaways

| Aspect | ✗ Wrong | ✓ Correct |
|--------|--------|----------|
| **Where preprocessing happens** | Flask app + Pipeline | Only Pipeline |
| **Data passed to model** | Preprocessed | Raw |
| **Manual pd.to_numeric()** | ❌ Yes | ✓ No |
| **Manual Yes/No→1/0** | ❌ Yes | ✓ No |
| **Manual scaling** | ❌ Yes | ✓ No |
| **Train-inference match** | ❌ Mismatch | ✓ Perfect match |
| **Code maintainability** | ❌ Two places to update | ✓ One place (Pipeline) |
| **Bugs** | ❌ High risk (double preprocessing) | ✓ Low risk |

---

## Testing the Fix

### Before (Wrong - Would print something like)
```
Partner input: "Yes"
After manual map: 1
OneHotEncoder input: 1
Result: Wrong prediction
```

### After (Correct)
```
Partner input: "Yes"
Directly to Pipeline
OneHotEncoder input: "Yes" (correct!)
Result: Correct prediction
```

---

## Files Updated

1. **app.py** - Fixed! Removed all manual preprocessing
2. **app_corrected.py** - Reference implementation with comments
3. **ML_PREPROCESSING_BEST_PRACTICES.md** - Detailed explanation

## Next: Production Deployment

For production, use a proper WSGI server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Never use Flask's development server in production!
