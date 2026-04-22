from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


from api_client import CryptoAPIClient
from database import DatabaseManager

def run_crypto_pipeline():
    client = CryptoAPIClient()
    
    raw = client.get_top_cryptos()
    clean = client.process_data(raw) 

    db = DatabaseManager()
    db.truncate_historical_data()
    db.save_crypto_data(clean)

    print(f"\n{'='*60}")
    print(f"CRYPTO PIPELINE RESULTS - {len(clean)} COINS")
    print('='*60)

    for coin in clean:
        print(f"{coin['name']} | {coin['symbol']} | {coin['price']} | {coin['market_cap']}  | {coin['volume']} | {coin['change_24h']} | {coin['timestamp']}")
    
    print(f"\n✅ Saved {len(clean)} coins to database")
    print('='*60)
    
    return f"Success: {len(clean)} coins processed"

with DAG(
    'crypto_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule='0 0 * * *',
    catchup=False
) as dag:
    
    task1 = PythonOperator(
        task_id='fetch_and_process',
        python_callable=run_crypto_pipeline
    )
