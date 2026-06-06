import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load dataset
df = pd.read_csv(os.path.join(BASE_DIR, "churn.csv"))

# Drop only if exists
if "customerID" in df.columns:
    df = df.drop("customerID", axis=1)

# Clean
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df = df.dropna()

# Encode categorical variables
df = pd.get_dummies(df)

# Split features & target
X = df.drop("Churn_Yes", axis=1)
y = df["Churn_Yes"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save model + columns
joblib.dump(model, os.path.join(BASE_DIR, "model.pkl"))
joblib.dump(X.columns.tolist(), os.path.join(BASE_DIR, "columns.pkl"))

print("✅ Model trained & saved successfully")