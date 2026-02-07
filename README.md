# Customer Churn Prediction 📊

A machine learning web application that predicts whether a telecom customer will churn using Flask and scikit-learn.

## Features ✨

- **ML-Powered Predictions**: Trained logistic regression model with 80%+ accuracy
- **User-Friendly Web Interface**: Simple form-based input for customer data
- **Risk Assessment**: Visual risk levels (Low, Medium, High, Very High)
- **Real-time Results**: Instant churn probability predictions
- **Proper ML Pipeline**: Correct preprocessing pipeline that prevents data leakage

## Quick Start 🚀

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/abdulrehmanshaikhwork/customer-churn-prediction.git
   cd customer-churn-prediction
   ```

2. **Create a virtual environment** (optional but recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Train the model** (if needed)
   ```bash
   python main.py
   ```
   This creates `model.pkl` containing the trained pipeline.

5. **Run the Flask app**
   ```bash
   python app.py
   ```

6. **Open in browser**
   Navigate to `http://localhost:5000` in your web browser.

## How to Use 📝

1. Fill in the customer information form with:
   - **Customer ID**: Unique identifier (optional)
   - **Demographics**: Gender, age (Senior Citizen), partner/dependents status
   - **Services**: Phone, internet, security, backup, device protection, tech support, streaming
   - **Contract**: Type and billing details
   - **Charges**: Monthly charges and tenure

2. Click **"Predict Churn"**

3. View the prediction result:
   - ✓ **Churn Prediction**: Yes/No
   - 📊 **Probability**: Percentage likelihood
   - 🎯 **Risk Level**: Visual indicator of churn risk
   - 📈 **Form Summary**: Review submitted data

## Project Structure 📁

```
.
├── app.py                          # Flask web application
├── main.py                         # Model training script
├── model.pkl                       # Trained ML pipeline (generated)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── templates/
│   ├── index.html                 # Input form page
│   └── predict.html               # Results page
├── WA_Fn-UseC_-Telco-Customer-Churn.csv  # Training data
├── test_customers.csv             # Sample test data
└── test_customers_with_predictions.csv   # Test results
```

## Model Information 🤖

**Algorithm**: Logistic Regression with scikit-learn Pipeline

**Features**:
- 19 customer attributes
- Preprocessing: Missing value imputation, categorical encoding, feature scaling
- Training pipeline ensures consistency between training and inference

**Accuracy**: ~80% on test data

## Key Details 🔑

### What the Model Does
- Analyzes customer characteristics
- Computes churn probability (0-100%)
- Assigns risk level based on probability

### Risk Levels
- 🟢 **Low Risk** (< 30%): Customer unlikely to churn
- 🟡 **Medium Risk** (30-50%): Monitor for satisfaction issues
- 🟠 **High Risk** (50-70%): Proactive retention needed
- 🔴 **Very High Risk** (> 70%): Critical intervention required

## Best Practices 🏆

This project implements proper ML pipeline practices:

✅ **Correct Approach**:
- Single pipeline handles all preprocessing
- Raw data passed to model without manual transformations
- Consistent preprocessing between training and inference

❌ **Avoided**: Double preprocessing that causes data mismatches

## Configuration 🔧

Edit `app.py` for:
- **Host/Port**: Change `port=5000` and `host='localhost'`
- **Debug Mode**: Set `debug=False` for production
- **WSGI Server**: Use Gunicorn/Waitress for production instead of Flask dev server

## Production Deployment 🌐

For production environments:

1. **Use a WSGI server** (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Add HTTPS**: Use nginx or similar reverse proxy

3. **Set environment variables**:
   ```
   FLASK_ENV=production
   FLASK_DEBUG=0
   ```

4. **Database**: Store predictions for analytics

## Troubleshooting 🔧

### "Model not found" Error
```bash
python main.py  # Regenerate the model
```

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Port Already in Use
```bash
# Change port in app.py or use:
python -m flask run --port 8000
```

## Learning Resources 📚

- **ML Preprocessing**: Check `ML_PREPROCESSING_BEST_PRACTICES.md`
- **Before/After Comparison**: See `BEFORE_AFTER_COMPARISON.md`
- **Quick Reference**: See `QUICK_REFERENCE.md`

## Contributing 🤝

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License 📄

MIT License - feel free to use this project for learning and development.

## Contact & Support 💬

- **Author**: Abdul Rehman Shaikh
- **GitHub**: [@abdulrehmanshaikhwork](https://github.com/abdulrehmanshaikhwork)
- **Email**: abdulrehmanshaikhabc@gmail.com

## Acknowledgments 🙏

- Dataset: Telco Customer Churn (Kaggle)
- Built with Flask and scikit-learn
- Inspired by ML best practices and production-ready code patterns

---

**Happy Predicting!** 🎯
