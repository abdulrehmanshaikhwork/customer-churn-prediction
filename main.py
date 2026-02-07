import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import StratifiedShuffleSplit, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# Single file contains both: Pipeline (preprocessing) + Classifier (model)
MODEL_FILE = "model.pkl"  # Everything: preprocessing + classifier inside

def build_pipeline(num_attribs, cat_attribs):
    num_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
    ])

    cat_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore", drop="first"))
    ])

    preprocessor = ColumnTransformer([
    ("num", num_pipeline, num_attribs),
    ("cat", cat_pipeline, cat_attribs)
    ])
    
    return preprocessor

if not os.path.exists(MODEL_FILE):
    # Training the model
    churn_data = pd.read_csv("WA_Fn-UseC_-Telco-Customer-Churn.csv")

    # Converting the true numeric columns to numeric
    true_num_cols = ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"]
    for cols in true_num_cols:
        churn_data[cols] = pd.to_numeric(churn_data[cols], errors="coerce")

    # Converting the target column to numeric (only Churn, not features!)
    churn_data["Churn"] = churn_data["Churn"].map({"Yes": 1, "No": 0})

    # ✓ DO NOT convert Partner, Dependents, PhoneService, PaperlessBilling here!
    # Let them stay as "Yes"/"No" strings so Pipeline's OneHotEncoder handles them correctly
    # Pipeline will identify them as categorical and apply proper encoding

    # Seperating the features and labels
    customer_features = churn_data.drop(["Churn", "customerID"], axis=1)
    churn_labels = churn_data["Churn"]

    # Creating the Train and the test set 
    split = StratifiedShuffleSplit(
        n_splits=1,
        test_size=0.2,
        random_state=42
    )
    for train_idx, test_idx in split.split(customer_features, churn_labels):
        train_features = customer_features.iloc[train_idx]
        test_features = customer_features.iloc[test_idx]#.to_csv("test_customers.csv", index=False)

        train_labels = churn_labels.iloc[train_idx]
        test_labels = churn_labels.iloc[test_idx]

    # Seperating the numeric and categorical columns
    num_attribs = train_features.select_dtypes(include=["int64", "float64"]).columns.tolist()
    cat_attribs = train_features.select_dtypes(include=["object"]).columns.tolist()

    preprocessor = build_pipeline(num_attribs, cat_attribs)

    final_model = Pipeline([
    ("preprocessing", preprocessor),
    ("classifier", LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    ))
    ])

    final_model.fit(train_features, train_labels)
    final_preds = final_model.predict(test_features)

    # Save: One file with both pipeline (preprocessing) and classifier inside
    joblib.dump(final_model, MODEL_FILE)  # Complete system: preprocessing + model

    print("Model trained and saved.")

else:
    # INFERENCE PHASE
    # Load: One file containing both pipeline (preprocessing) and classifier
    model = joblib.load(MODEL_FILE)  # Complete system: preprocessing + model

    test_data = pd.read_csv("test_customers.csv")

    churn_predictions = model.predict(test_data)
    churn_probabilities = model.predict_proba(test_data)

    test_data["Churn_Prediction"] = churn_predictions
    test_data["Churn_Probability"] = churn_probabilities[:, 1]

    test_data["Churn_Label"] = test_data["Churn_Prediction"].map({
    1: "Yes",
    0: "No"
    })

    test_data.to_csv(
    "test_customers_with_predictions.csv",
    index=False
    )