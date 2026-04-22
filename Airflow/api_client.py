import requests
from datetime import datetime

class CryptoAPIClient:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"

    def get_top_cryptos(self, limit=100):
        url = f"{self.base_url}/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': limit,
            'page': 1,
            'sparkline': 'false'
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            print(f"📊 Retrieved {len(data)} cryptocurrencies")
            return data
        except Exception as e:
            print(f"❌ API Error: {e}")
            return []

    def process_data(self, raw_data):
        cleaned = []
        for coin in raw_data:
            price_change = coin.get('price_change_percentage_24h')
            if price_change is None:
                change_str = "0.00%"
            else:
                change_str = f"{float(price_change):+.2f}%"
            
            cleaned.append({
                'name': coin['name'],
                'symbol': coin['symbol'].upper(),
                'price': f"${float(coin['current_price']):,.2f}",
                'market_cap': f"${float(coin['market_cap']):,.0f}",
                'volume': f"${float(coin['total_volume']):,.0f}",
                'change_24h': change_str,
                'timestamp': datetime.now()
            })
        print(f"✅ Processed {len(cleaned)} records")
        return cleaned
