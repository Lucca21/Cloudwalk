# **Transaction Monitoring System – Documentation**

## **Project Overview**

This project implements a **real-time transaction monitoring system** that detects anomalies in transaction flows using **Isolation Forest**, with a live dashboard to visualize the counts per status. It consists of a FastAPI backend for receiving transactions and a Streamlit dashboard for live visualization.

---

## **Project Structure**

**`project/`**  
`│`  
`├── Data Analysis.ipynb # Python notebook with the TASK “3.1 - Get your hands dirty”)`  
`├── monitor.py          # FastAPI backend handling transaction input and anomaly detection`  
`├── dashboard.py        # Streamlit app showing real-time transaction counts`  
`├── client.py		  # A simple client that simulates new random transactions.`   
`└── README.md          # This documentation`

---

**`Task 3.1 - Get your Hands Dirty`**

**`Data Analysis.ipynb`**

This is a jupyter notebook file where i analyze the  number of sales of POS by hour comparing the same sales per hour from today, yesterday and the average of other days and identify anomalies.

**`Task 3.2 - Solve the problem ( Monitoring system)`**

**`Monitor.py` – Backend API**

### **Purpose**

* Receives transactions via POST requests.

* Aggregates transaction counts by minute.

* Detects anomalies using **Isolation Forest**.

* Provides an endpoint to fetch aggregated counts.

### **Key Libraries**

* `fastapi` – Web framework to create API endpoints.

* `pydantic` – Data validation and serialization.

* `pandas` – Data manipulation and pivoting.

* `sklearn.ensemble.IsolationForest` – Anomaly detection.

* `threading` – To handle concurrent requests safely.

### **Endpoints**

1. **POST `/check`**

Input: JSON object containing:

 `{`  
  `"status": "approved|failed|denied|reversed",`  
  `"timestamp": "YYYY-MM-DDTHH:MM:SS"`  
`)`

If the minute changed:

 `{`  
  `"minute": "2025-07-12T13:45",`  
  `"summary": {"approved": 10, "failed": 2, ...},`  
  `"alert": true|false`  
`}`  
Otherwise:

 `{"message": "Transaction registered"}`

2. **GET `/history_counts`**

   * Returns aggregated counts for all minutes received. ( Used to plot the dashboard)

Output format:

 `[`  
  `{"minute": "2025-07-12T13:45", "summary": {"approved": 10, "failed": 2, ...}},`  
  `...`  
`]`

**`dashboard.py` – Real-Time Visualization**

### **Purpose**

* Continuously fetches new transaction counts from `/history_counts`.

* Plots a **line chart** with each status as a separate line.

* Updates automatically every few seconds.

### **Key Libraries**

* `streamlit` – For interactive dashboard.

* `requests` – To fetch data from the API.

* `pandas` – To structure the data for plotting.

### **Usage**

Run the dashboard with:

 `streamlit run dashboard.py`

* The line chart shows the **number of transactions per status over time**.

* Each line corresponds to a status (failed, denied, reversed, etc.).

* Approved transactions are counted but not passed to the anomaly detection model.

---

## **How to Run the Project** 

1) Create a `requirements.txt` with:  
   `fastapi,uvicorn,pandas,scikit-learn,streamlit and requests`  
2) Then install:  `pip install -r requirements.txt`  
3) **Start the backend API**:  `uvicorn monitor:app --reload`  
4) **Start the Streamlit dashboard**: `streamlit run dashboard.py`  
5) **Send transactions** using the **client.py** script or a tool like `curl`/Postman:`Python client.py`

---

**Used Libraries**

| Library | Purpose |
| :---- | ----- |
| `fastapi` | Build REST API |
| `pydantic` | Validate incoming JSON |
| `pandas` | Data processing & pivoting |
| `sklearn` | Isolation Forest for anomaly detection |
| `threading` | Thread-safe handling of incoming transactions |
| `streamlit` | Real-time dashboard |
| `requests` | API client for sending/fetching data |

---

## **Notes**

* Only **failed, denied, and reversed** transactions are fed into the Isolation Forest model.

* Approved transactions are counted but ignored for anomaly detection.

* The system is designed for **minute-level aggregation**.

* The dashboard auto-refreshes to display new transactions in real-time.

