# 🏭 Industrial AI Maintenance Dashboard

An end-to-end predictive maintenance system that uses machine learning to predict industrial machine failures and support maintenance decisions.

## 📌 Project Overview

This project uses the **AI4I 2020 Predictive Maintenance Dataset** to develop a machine learning system that estimates the probability of machine failure based on operating conditions.

The project covers the complete workflow from data analysis and model training to deployment and simulated real-time monitoring.

### Main Features

- 📊 Interactive maintenance dashboard
- 🤖 Machine failure prediction using XGBoost
- 📈 Model evaluation and analytics
- ⚙️ Automated maintenance recommendations
- 📡 Simulated real-time machine monitoring
- 🚨 Maintenance alerts and incident tracking
- 🖥️ Streamlit web application

## 🤖 Machine Learning

Several models were evaluated:

- Logistic Regression
- Random Forest
- XGBoost
- Artificial Neural Network (ANN)

**XGBoost** achieved the strongest overall performance and was selected for the final prediction system.

The model uses machine operating conditions including:

- Air temperature
- Process temperature
- Rotational speed
- Torque
- Tool wear
- Machine type

The model produces a **failure probability**, which is then converted into a risk level and maintenance recommendation.

## 📡 Live Monitoring

The application includes a simulated real-time predictive maintenance pipeline using **Apache Kafka**:

```text
Sensor Observations
        ↓
   Apache Kafka
        ↓
   Kafka Consumer
        ↓
    XGBoost Model
        ↓
 Failure Probability
        ↓
    Risk Level
        ↓
Maintenance Recommendation
        ↓
 Predictions / Alerts
        ↓
 Streamlit Dashboard
```

## 🛠️ Technologies

Python · Pandas · NumPy · Scikit-learn · XGBoost · TensorFlow/Keras · Plotly · Streamlit · Apache Kafka · Docker · Jupyter

 ## 📂 Project Structure
```
 industrial-maintenance-project/
├── app/
│   ├── pages/
│   └── utils/
├── data/
│   ├── raw/
│   └── processed/
├── models/
├── notebooks/
├── streaming/
│   ├── producer.py
│   └── consumer.py
├── docker-compose.yml
└── requirements.txt
```

## 🔮 Future Improvements
- Remaining Useful Life (RUL) prediction
- Improved real-time sensor integration
- Maintenance scheduling optimization
- Explainable AI using SHAP
- Database integration
- Cloud deployment
- More advanced anomaly detection

## ⚠️ Note
This is an educational project demonstrating a predictive maintenance workflow. The live monitoring component uses **simulated sensor observations** rather than data from actual industrial machinery.