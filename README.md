# 💰 MochiMoney – My Personal Budget App

![MochiMoney Icon](assets/icon/mochi_icon_1024.png)

Just a lightweight budgeting app I made for myself.  
Built with Streamlit and Docker. Runs locally in a browser.  
No accounts, no cloud — just simple money tracking 💸

## 🚀 How to Run

```bash
docker pull vienai8d/mochi-money
```

Mount a host directory for saving data (e.g. `~/mochi-data`):

```bash
docker run -d \
  -p 8501:8501 \
  -v ~/mochi-data:/app/data \
  --name mochi-money \
  vienai8d/mochi-money
```

Open in your browser:

```
http://localhost:8501
```

> 🗂 All data (CSVs, DBs, etc.) will be saved to `/data` inside the container.
