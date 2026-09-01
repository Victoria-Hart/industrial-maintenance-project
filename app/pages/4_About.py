import streamlit as st

st.title("About")

st.markdown("""
## Project Overview

This application demonstrates an end-to-end machine learning workflow for
predictive maintenance using the **AI4I 2020 Predictive Maintenance Dataset**.

The goal is to estimate the probability that an industrial machine will fail
based on its operating conditions, allowing potential maintenance needs to be
identified before unexpected downtime occurs.

The project combines data preprocessing, exploratory data analysis, machine
learning, failure prediction, maintenance recommendations, and an interactive
web interface built with Streamlit.
""")

st.divider()

st.markdown("""
## Dataset

The project uses the **AI4I 2020 Predictive Maintenance Dataset**, which
contains simulated industrial machine operating data.

Each machine includes measurements such as:

- Air temperature
- Process temperature
- Rotational speed
- Torque
- Tool wear
- Product type

The target variable is whether the machine experienced a failure.
""")

st.divider()

st.markdown("""
## Machine Learning Pipeline

1. Data preprocessing and cleaning
2. Exploratory data analysis
3. Feature engineering
4. Train/test split
5. Model training
6. Model evaluation
7. Failure probability prediction
8. Risk classification
9. Maintenance recommendation generation
""")

st.divider()

st.markdown("""
## Live Monitoring

The **Live Machine Monitoring** page demonstrates a real-time predictive
maintenance workflow.

Sensor readings are streamed through **Apache Kafka** and processed by an
**XGBoost** machine learning model. The model generates a failure probability
for each incoming machine reading.

Based on the predicted probability, machines are assigned a risk level and
maintenance recommendations are generated automatically.

The monitoring interface provides:

- Real-time machine predictions
- Failure probability and risk classification
- Active maintenance alerts
- Sensor readings captured when an alert is detected
- Maintenance notes for individual incidents
- Incident status management
- Recent prediction history
- Demo pause/restart controls
""")

st.divider()

st.markdown("""
## Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Apache Kafka
- Docker
- Plotly
- Streamlit
""")

st.divider()

st.markdown("""
## Application Features

- Dashboard with machine risk overview
- Failure probability prediction
- Interactive analytics and visualizations
- Automated maintenance recommendations
- Real-time sensor data streaming
- Automated maintenance alerts
- Incident tracking and maintenance notes
- Live monitoring dashboard
""")

st.divider()

st.markdown("""
## Future Improvements

Possible future enhancements include:

- Predicting remaining useful life (RUL)
- Maintenance scheduling optimization
- Cost estimation
- More advanced real-world sensor integration
- Cloud deployment and API integration
""")