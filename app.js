import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
const API_URL = "http://127.0.0.1:8000/predict";

export default function App() {
  const [tenure, setTenure] = useState("");
  const [monthly, setMonthly] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const predict = async () => {
    setLoading(true);
    setResult(null);

    try {
      const res = await axios.post(API_URL, {
        tenure: Number(tenure),
        MonthlyCharges: Number(monthly)
      });
      setResult(res.data);
    } catch (err) {
      alert("Backend error");
    }

    setLoading(false);
  };

  return (
    <div style={styles.container}>
      <motion.div
  style={styles.card}
  initial={{ opacity: 0, y: 40 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
>    </motion.div>
        <h1>AI Decision Intelligence</h1>
        <p>Predict customer churn with explainable AI</p>

        <input
          style={styles.input}
          placeholder="Tenure"
          onChange={(e) => setTenure(e.target.value)}
        />

        <input
          style={styles.input}
          placeholder="Monthly Charges"
          onChange={(e) => setMonthly(e.target.value)}
        />

        <button style={styles.button} onClick={predict}>
          {loading ? "Predicting..." : "Predict"}
        </button>

        {result && (
          <div style={styles.result}>
            <h2 style={{
              color: result.prediction === "Churn" ? "red" : "green"
            }}>
              {result.prediction}
            </h2>

            <p>Confidence: {result.probability}%</p>

            <h3>Top Factors</h3>
            {Object.entries(result.top_factors).map(([k, v]) => (
              <div key={k} style={styles.factor}>
                <span>{k}</span>
                <span>{v.toFixed(3)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
  );
}

const styles = {
  container: {
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "linear-gradient(135deg, #667eea, #764ba2)"
  },
  card: {
  width: "360px",
  padding: "30px",
  background: "white",
  borderRadius: "16px",
  boxShadow: "0 20px 40px rgba(0,0,0,0.2)",
  textAlign: "center"
},
  input: {
    width: "100%",
    padding: "10px",
    margin: "8px 0",
    borderRadius: "6px",
    border: "1px solid #ccc"
  },
  button: {
    width: "100%",
    padding: "10px",
    background: "black",
    color: "white",
    border: "none",
    borderRadius: "6px",
    marginTop: "10px",
    cursor: "pointer"
  },
  result: {
    marginTop: "20px",
    background: "#f0f0f0",
    padding: "10px",
    borderRadius: "8px"
  },
  factor: {
    display: "flex",
    justifyContent: "space-between",
    fontSize: "14px",
    borderBottom: "1px solid #ddd"
  }
};