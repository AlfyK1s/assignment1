import requests
import streamlit as st

st.set_page_config(page_title="Wine Quality Predictor", layout="centered")
st.title("🍷 Оценка качества красного вина")

API_URL = "http://api:8000/predict"

col1, col2 = st.columns(2)
with col1:
    fixed_acidity = st.number_input("Fixed Acidity", 4.0, 16.0, 7.4, 0.1)
    volatile_acidity = st.number_input("Volatile Acidity", 0.1, 2.0, 0.7, 0.01)
    citric_acid = st.number_input("Citric Acid", 0.0, 1.0, 0.0, 0.01)
    residual_sugar = st.number_input("Residual Sugar", 0.5, 15.0, 1.9, 0.1)
    chlorides = st.number_input("Chlorides", 0.01, 0.6, 0.3, 0.1)
    free_sulfur_dioxide = st.number_input("Free SO2", 1.0, 72.0, 11.0, 1.0)
with col2:
    total_sulfur_dioxide = st.number_input("Total SO2", 6.0, 289.0, 34.0, 1.0)
    density = st.number_input("Density", 0.990, 1.004, 0.9978, 0.0001, format="%.4f")
    pH = st.number_input("pH", 2.7, 4.0, 3.51, 0.01)
    sulphates = st.number_input("Sulphates", 0.3, 2.0, 0.56, 0.01)
    alcohol = st.number_input("Alcohol (% vol)", 8.0, 15.0, 9.4, 0.1)

if st.button("Оценить качество вина"):
    payload = {
        "fixed_acidity": fixed_acidity,
        "volatile_acidity": volatile_acidity,
        "citric_acid": citric_acid,
        "residual_sugar": residual_sugar,
        "chlorides": chlorides,
        "free_sulfur_dioxide": free_sulfur_dioxide,
        "total_sulfur_dioxide": total_sulfur_dioxide,
        "density": density,
        "pH": pH,
        "sulphates": sulphates,
        "alcohol": alcohol
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        if response.status_code == 200:
            res = response.json()
            st.success(f"Результат: **{res['label']}**")
            st.metric("Вероятность высокого качества", f"{res['probability_high_quality'] * 100:.1f}%")
        else:
            st.error("Ошибка ответа API")
    except Exception as e:
        st.error(f"Не удалось связаться с API: {e}")