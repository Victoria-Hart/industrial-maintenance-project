from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[2]


@st.cache_data
def load_dataset():
    return pd.read_csv(
        BASE_DIR / "data" / "processed" / "ai4i2020_processed.csv"
    )