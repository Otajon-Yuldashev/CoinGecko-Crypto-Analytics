# CoinGecko-Crypto-Analytics 🪙

An end-to-end data pipeline that fetches live cryptocurrency market data from the CoinGecko public API, processes and loads it into a PostgreSQL database via an Apache Airflow DAG, monitored through PgAdmin, and visualised in a Power BI dashboard — all containerised with Docker Compose. Built as a data engineering portfolio project.

> **Note:** Credentials are local only. Adjust database connection strings and Airflow configurations for your own environment before running.

---

## Architecture Overview

```
CoinGecko Public API (api.coingecko.com)
    /coins/markets · top 100 by market cap · USD
          |
          | HTTP GET · requests
          v
   CryptoAPIClient (Python)
   fetch → process → clean → format
          |
          | Airflow DAG (scheduled)
          v
   PostgreSQL · public.crypto_prices
   id · cryptocurrency · symbol · current_price
   market_cap · volume_24h · change_24h · timestamp
          |
          | PgAdmin (localhost:5050) — query & monitor
          v
   Power BI Dashboard
   market cap share · daily price · daily volume · 24h change
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data Source | CoinGecko Public API v3 |
| Ingestion & Processing | Python (requests, datetime) |
| Orchestration | Apache Airflow 2.7.0 |
| Database | PostgreSQL 13 |
| Monitoring | PgAdmin 4 |
| Containerisation | Docker Compose |
| Visualisation | Power BI |

---

## Dataset

Data is pulled from the CoinGecko `/coins/markets` endpoint — top 100 cryptocurrencies ordered by market cap descending, priced in USD.

**PostgreSQL table: `public.crypto_prices`**

| Column | Type | Description |
|---|---|---|
| id | integer (PK) | Auto-increment primary key |
| cryptocurrency | varchar(100) | Full coin name (e.g. Bitcoin) |
| symbol | varchar(20) | Ticker symbol (e.g. BTC) |
| current_price | numeric(20,8) | Current price in USD |
| market_cap | numeric(30,2) | Total market capitalisation |
| volume_24h | numeric(30,2) | 24-hour trading volume |
| change_24h | numeric(10,4) | 24-hour price change percentage |
| timestamp | timestamp | Record insertion time (no timezone) |

---

## Repository Structure

```
CoinGecko-Crypto-Analytics/
├── dags/
│   └── crypto_dag.py             # Airflow DAG definition
├── crypto_api_client.py          # CoinGecko API client + data processing
├── dashboard/
│   └── Power_BI_visual.png       # Power BI dashboard screenshot
├── pgadmin/
│   └── PgAdmin_view.png          # PgAdmin table view screenshot
├── docker-compose.yml            # Airflow + PostgreSQL + PgAdmin services
├── .gitignore
└── README.md
```

---

## Pipeline Logic

### CryptoAPIClient

**`get_top_cryptos(limit=100)`**  
Hits the CoinGecko `/coins/markets` endpoint with params: `vs_currency=usd`, `order=market_cap_desc`, `per_page=100`. Returns raw JSON list of coin objects. Raises on HTTP errors via `response.raise_for_status()`.

**`process_data(raw_data)`**  
Iterates over raw API response and cleans each record:
- Formats `current_price` as `$X,XXX.XX`
- Formats `market_cap` and `total_volume` with dollar sign and comma separators
- Handles null `price_change_percentage_24h` gracefully — defaults to `"0.00%"`
- Formats non-null price change as signed percentage: `+2.10%` / `-0.01%`
- Uppercases all ticker symbols
- Appends `timestamp` as `datetime.now()`

Returns a list of cleaned dictionaries ready for database insertion.

---

## Airflow DAG

**Schedule:** Configurable (daily recommended)  
**Tasks:** fetch from API → process → insert into PostgreSQL  
**Monitoring:** Airflow UI at `http://localhost:8080` for task status, retries, and run history

The DAG uses `CryptoAPIClient` to fetch and process data, then loads records into `public.crypto_prices`. Each run appends 100 rows with a fresh timestamp, building up historical price data over time.

---

## Docker Compose Setup

Four services orchestrated via `docker-compose.yml`:

| Service | Image | Role | Port |
|---|---|---|---|
| `postgres` | postgres:13 | Primary database — stores `crypto_prices` | 5432 |
| `pgadmin` | dpage/pgadmin4 | Database UI — query and monitor tables | 5050 |
| `airflow-webserver` | apache/airflow:2.7.0-python3.10 | Airflow UI — DAG management | 8080 |
| `airflow-scheduler` | apache/airflow:2.7.0-python3.10 | DAG scheduling and execution | — |

Both Airflow services install `requests` and `psycopg2-binary` on container startup. The `dags/` directory is mounted into both Airflow containers at `/opt/airflow/dags`.

**Default credentials:**

| Service | URL | Login |
|---|---|---|
| Airflow UI | http://localhost:8080 | admin / admin |
| PgAdmin | http://localhost:5050 | admin@admin.com / admin |
| PostgreSQL | localhost:5432 | airflow / airflow |

---

## Power BI Dashboard

![Power BI Dashboard](dashboard/Power_BI_visual.png)

**Data source:** `public.crypto_prices` table (PostgreSQL direct connection)

**Visuals included:**

- **Max Market Cap KPI** — $1,837,619,782,499 (Bitcoin dominant)
- **Symbol Table** — current price + 24h change % per coin (top movers: NIGHT +6847%, HASH +1953%, WETH +1172%)
- **Crypto Daily Price** — bar chart of current price by symbol
- **Market Capital Share** — treemap showing Bitcoin, Ethereum, Tether, XRP, Solana, BNB, USDC dominance
- **Daily Volume by Crypto** — horizontal bar chart (USDT leads at ~$100bn, followed by BTC, ETH, USDC, SOL)

---

## PgAdmin

![PgAdmin View](pgadmin/PgAdmin_view.png)

Table queried via:
```sql
SELECT * FROM public.crypto_prices;
```

100 rows returned per pipeline run. Sample data (2025-12-07 run):

| cryptocurrency | symbol | current_price | market_cap | volume_24h | change_24h |
|---|---|---|---|---|---|
| Bitcoin | BTC | 91352.00 | 1,824,595,664,015 | 31,169,777,174 | +2.01% |
| Ethereum | ETH | 3128.51 | 377,883,252,387 | 18,736,670,230 | +3.06% |
| Tether | USDT | 1.00 | 185,678,657,075 | 54,896,984,842 | -0.01% |
| XRP | XRP | 2.10 | 126,878,603,441 | 2,471,722,875 | +3.58% |
| Solana | SOL | 135.46 | 76,019,012,199 | 3,837,456,659 | +2.30% |

---

## Local Setup

1. **Clone the repo**
```bash
git clone https://github.com/Otajon-Yuldashev/CoinGecko-Crypto-Analytics.git
cd CoinGecko-Crypto-Analytics
```

2. **Start all services**
```bash
docker-compose up
```
First run takes a few minutes — Airflow initialises its metadata database and installs `requests` and `psycopg2-binary` on startup.

3. **Create the crypto_prices table**  
Connect to PgAdmin at `http://localhost:5050` (admin@admin.com / admin), add a server pointing to host `postgres`, port `5432`, then run:
```sql
CREATE TABLE public.crypto_prices (
    id SERIAL PRIMARY KEY,
    cryptocurrency VARCHAR(100),
    symbol VARCHAR(20),
    current_price NUMERIC(20,8),
    market_cap NUMERIC(30,2),
    volume_24h NUMERIC(30,2),
    change_24h NUMERIC(10,4),
    timestamp TIMESTAMP
);
```

4. **Configure Airflow PostgreSQL connection**  
Go to Airflow UI at `http://localhost:8080` → Admin → Connections → Add:
- Conn ID: `postgres_default`
- Conn Type: `Postgres`
- Host: `postgres`
- Schema: `airflow`
- Login: `airflow`
- Password: `airflow`
- Port: `5432`

5. **Trigger the DAG**  
Enable and trigger `crypto_pipeline` in the Airflow UI. Monitor task logs for fetch and insert confirmations.

6. **Connect Power BI**  
Connect Power BI Desktop to your PostgreSQL instance (`localhost:5432`, database `airflow`) and load `public.crypto_prices` to replicate the dashboard.

---

## Notes

- CoinGecko free tier has rate limits — the pipeline fetches once per scheduled run, well within limits
- Each DAG run appends 100 new rows — historical data accumulates over time for trend analysis
- No authentication required for CoinGecko public API
- All credentials are for local development only and not intended for production use
