import os
import joblib
import pandas as pd
import shap
import mysql.connector
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = joblib.load(os.path.join(BASE_DIR, "model.pkl"))
columns = joblib.load(os.path.join(BASE_DIR, "columns.pkl"))

explainer = None

# MySQL Connection
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ankit5421",
        database="churniq"
    )

@app.get("/")
def home():
    return {"message": "AI Decision API Running"}

@app.post("/predict")
def predict(data: dict):
    print("Received data:",data)
    global explainer

    input_df = pd.DataFrame([data])

    for col in columns:
        if col not in input_df:
            input_df[col] = 0

    input_df = input_df[columns]

    prediction = model.predict(input_df)[0]
    prob = model.predict_proba(input_df)[0][1]

    try:
    
        explainer = shap.TreeExplainer(model)
        shap_array = explainer.shap_values(input_df)

        import numpy as np

        # It's a numpy ndarray
        arr = np.array(shap_array)
        

        if arr.ndim == 3:
            # shape: (1, 16,2) → sample 0 , all features,class 1
            values = arr[0,:,1].tolist()

        elif arr.ndim == 2:
            # shape: (1, n_features)
            values = arr[0].tolist()
        elif arr.ndim == 1:
            # shape: (n_features,)
            values = arr.tolist()
        else:
            values = arr.flatten().tolist()

        explanation = dict(zip(columns, values))
        top_factors = {
            k: round(float(v), 3)
            for k, v in sorted(
                explanation.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:5]
        }
    except Exception as e:
        print("SHAP error:", e)
        top_factors = {}
    
    
        
        contract_type = "Unknown"
    for key in data:
        if key.startswith("Contract_"):
            if data[key] == 1:
                contract_type = key.replace("Contract_", "")

    tech_support = "Unknown"
    for key in data:
        if key.startswith("TechSupport_"):
            if data[key] == 1:
                tech_support = key.replace("TechSupport_", "")



 # Save to MySQL
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions 
            (tenure, monthly_charges, contract_type,
            tech_support, prediction, probability,
            top_factors, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get("tenure"),
            data.get("MonthlyCharges"),
            contract_type,
            tech_support,
            "Churn" if prediction == 1 else "No Churn",
            round(float(prob * 100), 2),
            str(top_factors),
            datetime.now()
        ))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("DB Error:", e)

    return {
        "prediction": "Churn" if prediction == 1 else "No Churn",
        "probability": round(float(prob * 100), 2),
        "top_factors": top_factors
    }

@app.get("/history")
def get_history():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM predictions 
            ORDER BY id DESC 
            LIMIT 20
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"history": rows}
    except Exception as e:
        return {"error": str(e)}