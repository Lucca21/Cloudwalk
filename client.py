# Importing libs
import requests
from datetime import datetime
import random
import time
import pandas as pd

url = "http://127.0.0.1:8000/check"
url_csv1 = "https://raw.githubusercontent.com/everton-cw/monitoring_test/main/transactions.csv"

# Loading file
df = pd.read_csv(url_csv1)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Listing statuses.
df['status'] = df['status'].str.lower()
statuses = df['status'].unique().tolist()


# Random transaction
def gerar_transacao():
    status = random.choice(statuses)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    return {"status": status, "timestamp": timestamp}


# Looping
while True:
    transacao = gerar_transacao()

    try:
        resp = requests.post(url, json=transacao)
        if resp.status_code == 200:
            data = resp.json()
            ## If returns 'summary', the minute has changed.
            if "summary" in data:
                print(f"⚠️ ALERT minute {data['minute']}: {data['summary']} --> alert={data['alert']}")
            else:
                print(f"✅ Transaction registered: {transacao}")
        else:
            print("Error:", resp.status_code)
    except Exception as e:
        print("Error:", e)

    time.sleep(2)  # 2 transactions per second