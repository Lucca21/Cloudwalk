## Importing libs
from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel
from sklearn.ensemble import IsolationForest
import threading
import pandas as pd

app = FastAPI()
lock = threading.Lock()

## Loading file

url_csv1 = "https://raw.githubusercontent.com/everton-cw/monitoring_test/main/transactions.csv"
df = pd.read_csv(url_csv1)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Listing statuses that will be used to train the model.
status_cols = [s.lower() for s in df['status'].unique() if s.lower() != "approved"]

# Summarizing data with only the relevant statuses.
df_summary = df.pivot_table(
    index='timestamp',
    columns='status',
    values='count',
    fill_value=0
)
df_summary = df_summary[[s for s in df_summary.columns if s.lower() in status_cols]]
df_summary.columns = [c.lower() for c in df_summary.columns]

# Creating the Isolation Forest model
X = df_summary.values
model_isolation = IsolationForest(random_state=42)
model_isolation.fit(X)

# Formating the endpoint input
class Transaction(BaseModel):
    status: str
    timestamp: str

# Global variables
minuto_atual = None
contador_minuto = {}

# -----------------------------
# Endpoint POST
# -----------------------------
@app.post("/check")
def check_transaction(transaction: Transaction):
    global minuto_atual, contador_minuto

    ts = datetime.fromisoformat(transaction.timestamp)
    minuto = ts.strftime("%Y-%m-%dT%H:%M")
    status_lower = transaction.status.lower()

    # Inicializing the counter
    with lock:
        if minuto not in contador_minuto:
            contador_minuto[minuto] = {s.lower(): 0 for s in df['status'].unique()}

        # Incrementing the counter
        contador_minuto[minuto][status_lower] += 1

        # If the minute has changed, process the summary of the previous minute
        if minuto_atual is not None and minuto != minuto_atual:
            # Creating summary
            resumo_modelo = {s: contador_minuto[minuto_atual].get(s, 0) for s in status_cols}
            X_minuto = [[int(resumo_modelo[s]) for s in status_cols]]

            # Check anomaly
            alert = bool(model_isolation.predict(X_minuto)[0] == -1)

            resposta = {
                "minute": minuto_atual,
                "summary": contador_minuto[minuto_atual],
                "alert": alert
            }

            minuto_atual = minuto
            return resposta
        else:
            minuto_atual = minuto
            return {"message": "Transaction registered"}


# -----------------------------
# Endpoint GET to return new data from the API (Used to plot the dashboard)
# -----------------------------
@app.get("/history_counts")
def get_history_counts():
    historico = []

    # New data recived with the APII
    for minuto, resumo in contador_minuto.items():
        historico.append({
            "minute": minuto,
            "summary": resumo
        })

    # Order by minute
    historico = sorted(historico, key=lambda x: x["minute"])
    return historico

