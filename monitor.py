## Importing libs
from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel
from sklearn.ensemble import IsolationForest
import threading
import pandas as pd

app = FastAPI()
lock = threading.Lock()

# -----------------------------
# 1️⃣ Treinamento do modelo com CSV real
# -----------------------------
url_csv1 = "https://raw.githubusercontent.com/everton-cw/monitoring_test/main/transactions.csv"
df = pd.read_csv(url_csv1)

# Converte coluna HORA em datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Lista todos os status, exceto "approved", para treino do modelo
status_cols = [s.lower() for s in df['status'].unique() if s.lower() != "approved"]

# Pivotar para ter uma linha por minuto e colunas por status (somente status relevantes)
df_summary = df.pivot_table(
    index='timestamp',
    columns='status',
    values='count',
    fill_value=0
)

# Filtra apenas os status relevantes para o modelo
df_summary = df_summary[[s for s in df_summary.columns if s.lower() in status_cols]]
df_summary.columns = [c.lower() for c in df_summary.columns]

# Criando Isolation Forest para detectar anomalias
X = df_summary.values
model_isolation = IsolationForest(random_state=42)
model_isolation.fit(X)

# -----------------------------
# 2️⃣ Modelo de input do endpoint
# -----------------------------
class Transaction(BaseModel):
    status: str
    timestamp: str

# -----------------------------
# 3️⃣ Variáveis globais para contagem por minuto
# -----------------------------
minuto_atual = None
contador_minuto = {}

# -----------------------------
# 4️⃣ Endpoint POST
# -----------------------------
@app.post("/check")
def check_transaction(transaction: Transaction):
    global minuto_atual, contador_minuto

    ts = datetime.fromisoformat(transaction.timestamp)
    minuto = ts.strftime("%Y-%m-%dT%H:%M")
    status_lower = transaction.status.lower()

    # Inicializa o contador para todos os status (inclusive approved)
    with lock:
        if minuto not in contador_minuto:
            contador_minuto[minuto] = {s.lower(): 0 for s in df['status'].unique()}

        # Incrementa o contador
        contador_minuto[minuto][status_lower] += 1

        # Se mudou de minuto, processa o resumo do minuto anterior
        if minuto_atual is not None and minuto != minuto_atual:
            # Cria resumo apenas com status que entram no modelo
            resumo_modelo = {s: contador_minuto[minuto_atual].get(s, 0) for s in status_cols}
            X_minuto = [[int(resumo_modelo[s]) for s in status_cols]]

            # Checa se é anomalia
            alert = bool(model_isolation.predict(X_minuto)[0] == -1)

            resposta = {
                "minute": minuto_atual,
                "summary": contador_minuto[minuto_atual],  # resumo completo, incluindo approved
                "alert": alert
            }

            minuto_atual = minuto
            return resposta
        else:
            minuto_atual = minuto
            return {"message": "Transação registrada"}


# -----------------------------
# 5️⃣ Endpoint GET para histórico (CSV + novos dados)
# -----------------------------
@app.get("/history_counts")
def get_history_counts():
    """
    Retorna apenas os dados novos recebidos via API (contador_minuto).
    """
    historico = []

    # Parte única: dados novos recebidos via API
    for minuto, resumo in contador_minuto.items():
        historico.append({
            "minute": minuto,
            "summary": resumo
        })

    # Ordena por minuto
    historico = sorted(historico, key=lambda x: x["minute"])
    return historico
