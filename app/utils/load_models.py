from pathlib import Path
import joblib
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[2]

@st.cache_resource
def load_xgboost():
    model_path = BASE_DIR / "models" / "xgboost.pkl"
    return joblib.load(model_path)

@st.cache_data
def load_feature_importance():
    return pd.read_csv(
        BASE_DIR / "models" / "feature_importance.csv"
    )