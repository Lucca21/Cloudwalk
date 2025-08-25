import requests
from datetime import datetime
import random
import time
import pandas as pd

url = "http://127.0.0.1:8000/check"
url_csv1 = "https://raw.githubusercontent.com/everton-cw/monitoring_test/main/transactions.csv"

df = pd.read_csv(url_csv1)

# Converte coluna HORA em datetime.
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Lista os status possíveis
df['status'] = df['status'].str.lower()
statuses = df['status'].unique().tolist()


# Função para gerar transação aleatória
def gerar_transacao():
    status = random.choice(statuses)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    return {"status": status, "timestamp": timestamp}


# Loop contínuo de envio
while True:
    transacao = gerar_transacao()

    try:
        resp = requests.post(url, json=transacao)
        if resp.status_code == 200:
            data = resp.json()
            # Se o minuto fechou e o modelo retornou alerta
            if "summary" in data:
                print(f"⚠️ ALERTA minuto {data['minute']}: {data['summary']} --> alert={data['alert']}")
            else:
                print(f"✅ Transação registrada: {transacao}")
        else:
            print("Erro ao chamar API:", resp.status_code)
    except Exception as e:
        print("Erro ao chamar API:", e)

    # Espera um pouco antes de enviar a próxima transação
    time.sleep(2)  # 2 transações por segundo