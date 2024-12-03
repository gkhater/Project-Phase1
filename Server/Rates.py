import requests
import time

class ExchangeRateCache:
    def __init__(self, ttl=3600):
        self.cache = {}  # To store the exchange rates
        self.ttl = ttl   # Time-to-live in seconds

    def get_rate(self, base, target):
        # Create a unique key for the cache
        key = (base.upper(), target.upper())
        
        # Check if the key is in the cache and the data is still valid
        if key in self.cache:
            rate, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:  # Check if within TTL
                print(f"RATE: {rate}")
                return rate
        
        # If not in cache or expired, fetch from API
        rate = self.fetch_rate(base, target)
        if rate is not None:
            self.cache[key] = (rate, time.time())  # Update cache
        
        print(f"RATE: {rate}")
        return rate

    def fetch_rate(self, base, target):
        base = base.upper()
        target = target.upper()

        if base == target:
            return 1  # Same currency

        url = f"https://api.frankfurter.app/latest?from={base}&to={target}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            return data['rates'].get(target)
        else:
            raise Exception(f"Failed to fetch exchange rate from {base} to {target}: {response.status_code}")


cache = ExchangeRateCache()

def convert(base, target): 
    return float(cache.get_rate(base, target))
