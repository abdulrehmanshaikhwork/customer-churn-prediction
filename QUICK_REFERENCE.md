# Quick Reference: ML Preprocessing Rules

## One Golden Rule
**Pass RAW data to model. Let Pipeline handle everything.**

---

## Checklist: Am I Doing This Correctly?

- [ ] **Saving Model:** `joblib.dump(final_model, "model.pkl")` (entire Pipeline, not just classifier)
- [ ] **Loading Model:** `model = joblib.load("model.pkl")`
- [ ] **Input Data:** Raw format (strings, original values, no conversion)
- [ ] **Data Validation:** Only check columns exist, NOT convert values
- [ ] **Preprocessing:** Zero manual preprocessing in Flask
- [ ] **Prediction:** `model.predict(input_df)` directly on raw data
- [ ] **No Manual:** pd.to_numeric(), .map(), StandardScaler(), OneHotEncoder()

---

## What Each Layer Does

### Training (main.py)
```python
Pipeline([
    ('preprocessing', ColumnTransformer([...])),  # ← Learns from data
    ('classifier', LogisticRegression())
]).fit(raw_data, labels)  # ← Raw data goes in
```

### Inference (app.py)
```python
model.predict(raw_data)  # ← Raw data goes in
# Pipeline automatically:
# 1. Identifies numeric/categorical columns
# 2. Applies learned transformations
# 3. Returns prediction
```

---

## Common Mistakes & Fixes

### ✗ Mistake 1: Manual pd.to_numeric()
```python
# WRONG:
input_df['tenure'] = pd.to_numeric(input_df['tenure'])
prediction = model.predict(input_df)

# RIGHT:
prediction = model.predict(input_df)  # Pipeline does it
```

### ✗ Mistake 2: Manual Yes/No mapping
```python
# WRONG:
input_df['Partner'] = input_df['Partner'].map({"Yes": 1, "No": 0})
prediction = model.predict(input_df)

# RIGHT:
prediction = model.predict(input_df)  # Pipeline's OneHotEncoder does it
```

### ✗ Mistake 3: Manual scaling
```python
# WRONG:
from sklearn.preprocessing import StandardScaler
input_df = StandardScaler().fit_transform(input_df)
prediction = model.predict(input_df)

# RIGHT:
prediction = model.predict(input_df)  # Pipeline's scaler does it
```

### ✗ Mistake 4: Saving Without Preprocessing
```python
# WRONG:
joblib.dump(classifier_only, "model.pkl")

# RIGHT:
joblib.dump(complete_pipeline, "model.pkl")
```

---

## Quick Code Template

```python
from flask import Flask, render_template, request
import pandas as pd
import joblib

app = Flask(__name__)
model = joblib.load("model.pkl")  # Entire Pipeline

EXPECTED_COLUMNS = [
    'gender', 'Partner', 'tenure', 'MonthlyCharges',
    # ... all other columns
]

@app.route('/predict', methods=['POST'])
def predict():
    # 1. Get data
    data = request.form.to_dict()
    
    # 2. Create DataFrame
    input_df = pd.DataFrame([data])
    
    # 3. Validate structure only
    missing = [col for col in EXPECTED_COLUMNS if col not in input_df.columns]
    if missing:
        return {'error': f'Missing: {missing}'}
    
    # 4. Select correct columns
    input_df = input_df[EXPECTED_COLUMNS]
    
    # 5. Predict (Pipeline handles all preprocessing)
    prediction = model.predict(input_df)[0]
    
    return {'prediction': prediction}
```

---

## Data Flow: Correct vs Incorrect

### ✗ INCORRECT (Your Original Code)
```
Form Input
    ↓
"Partner": "Yes"
    ↓
MANUAL: pd.to_numeric(), map(), etc.
    ↓
Preprocessed Data
    ↓
PIPELINE: Preprocesses AGAIN
    ↓
WRONG OUTPUT ❌
```

### ✓ CORRECT (Fixed Code)
```
Form Input
    ↓
"Partner": "Yes"
    ↓
RAW DATA (no manual preprocessing)
    ↓
PIPELINE: Preprocess once
    ↓
CORRECT OUTPUT ✓
```

---

## Why This Matters

| Scenario | If You Manually Preprocess | If You Use Pipeline |
|----------|---------------------------|-------------------|
| Training-inference match | ❌ Mismatch | ✓ Perfect match |
| OneHotEncoder | ❌ Wrong encoding | ✓ Correct |
| StandardScaler | ❌ Wrong scaling | ✓ Correct |
| Missing values | ❌ Handled twice | ✓ Handled once |
| Error handling | ❌ Silent failures | ✓ Clear errors |
| Maintenance | ❌ Update 2+ places | ✓ Update 1 place |
| Production ready | ❌ Buggy | ✓ Reliable |

---

## Testing Your Fix

### Test 1: Simple Prediction
```python
# Form input
data = {
    'customerID': 'TEST-001',
    'gender': 'Male',
    'Partner': 'Yes',
    'tenure': '12',
    'MonthlyCharges': '65.5',
    # ... other fields
}

# Should work without errors
prediction = model.predict(pd.DataFrame([{k:v for k,v in data.items() if k != 'customerID'}]))
```

### Test 2: Different Data Types
```python
# All these should work identically
test_cases = [
    {'tenure': '12', 'MonthlyCharges': '65.5'},      # Strings
    {'tenure': 12, 'MonthlyCharges': 65.5},          # Numbers
    {'tenure': '12.0', 'MonthlyCharges': '65.50'},   # Float strings
]

# All should produce same prediction (Pipeline handles conversion)
```

---

## Common Questions

**Q: Should I scale data before model.predict()?**
A: No. Pipeline's StandardScaler does it.

**Q: Should I convert "Yes" to 1?**
A: No. Pipeline's OneHotEncoder does it.

**Q: What if input has invalid data?**
A: Pipeline handles it (Imputer fills missing, transformer handles rest).

**Q: Why am I getting different results from training?**
A: You're preprocessing differently (manually vs Pipeline).

**Q: Can I use model.predict() without loading full Pipeline?**
A: Only if model.pkl contains the entire Pipeline. Check what you saved!

**Q: What if someone sends data in different order?**
A: Use `input_df[EXPECTED_COLUMNS]` to ensure correct order.

**Q: Should I validate individual field values?**
A: No. Only validate that columns exist.

---

## Production Deployment Checklist

- [ ] Saved entire Pipeline (preprocessing + model)
- [ ] No manual preprocessing in inference code
- [ ] Input validation checks only for missing columns
- [ ] Appropriate error handling
- [ ] Using production WSGI server (gunicorn, not Flask dev server)
- [ ] Model versioning strategy
- [ ] Logging for debugging
- [ ] Documentation of expected input format
- [ ] Testing with edge cases (missing values, invalid types, etc.)

---

## Files You Should Read

1. **SUMMARY.md** - Complete explanation with examples
2. **ML_PREPROCESSING_BEST_PRACTICES.md** - Detailed breakdown
3. **BEFORE_AFTER_COMPARISON.md** - Visual comparison
4. **app.py** - Your corrected Flask code
5. **app_corrected.py** - Reference implementation with detailed comments

---

## Most Important Takeaway

**Your Pipeline already handles preprocessing. Don't do it twice.**

Pass raw data → Pipeline handles everything → Get prediction.

That's it! 🎉
