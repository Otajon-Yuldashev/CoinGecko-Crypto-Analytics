import psycopg2

class DatabaseManager:
    def __init__(self):
        self.conn_params = {
            'host': 'postgres',
            'database': 'airflow',
            'user': 'airflow',
            'password': 'airflow',
            'port': '5432'
        }
        self.create_table_if_not_exists()  
    
    def create_table_if_not_exists(self):
        """Create crypto_prices table if it doesn't exist"""
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crypto_prices (
                    id SERIAL PRIMARY KEY,
                    cryptocurrency VARCHAR(100),
                    symbol VARCHAR(20),
                    current_price DECIMAL(20, 8),
                    market_cap DECIMAL(30, 2),
                    volume_24h DECIMAL(30, 2),
                    change_24h DECIMAL(10, 4),
                    timestamp TIMESTAMP
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Created/verified crypto_prices table")
        except Exception as e:
            print(f"❌ Table creation error: {e}")
    
    def save_crypto_data(self, data):
        conn = psycopg2.connect(**self.conn_params)
        cursor = conn.cursor()
        
        for coin in data:
            price = float(coin['price'].replace('$', '').replace(',', ''))
            market_cap = float(coin['market_cap'].replace('$', '').replace(',', ''))
            volume = float(coin['volume'].replace('$', '').replace(',', ''))
            change = float(coin['change_24h'].replace('%', '').replace('+', ''))
            
            cursor.execute("""
                INSERT INTO crypto_prices 
                (cryptocurrency, symbol, current_price, market_cap, volume_24h, change_24h, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                coin['name'],
                coin['symbol'],
                price,
                market_cap,
                volume,
                change,
                coin['timestamp']
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Saved {len(data)} records to database")
    
    def truncate_historical_data(self):
        conn = psycopg2.connect(**self.conn_params)
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE crypto_prices RESTART IDENTITY;")
        conn.commit()
        cursor.close()
        conn.close()
        print("🗑  Truncated table (deleted all rows)")
