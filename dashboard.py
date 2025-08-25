# dashboard.py
import streamlit as st
import requests
import pandas as pd
import time

API_URL = "http://127.0.0.1:8000/history_counts"

st.set_page_config(page_title="Monitor de Transações", layout="wide")
st.title("📊 Monitoramento de Transações em Tempo Real")

placeholder = st.empty()

# Looping
while True:
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()

            if data:
                # transforma a resposta em dataframe
                records = []
                for d in data:
                    row = {"minute": d["minute"], **d["summary"]}
                    records.append(row)

                df = pd.DataFrame(records).sort_values("minute")

                # desenha gráfico
                with placeholder.container():
                    st.line_chart(df.set_index("minute"))
    except Exception as e:
        st.error(f"Error fetching data: {e}")

    time.sleep(2)
