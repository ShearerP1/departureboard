import time

class Cache:

    _cache = {}

    def get(self, station_id):
        now = time.time()
        record = self._cache.get(station_id)
        if record and record.get("expires_at") > now:
            return record.get("data")

        return None

    
    def set(self, station_id, data, ttl):
        now = time.time()
        expires_at = now + ttl

        self._cache[station_id] = {
            "expires_at": expires_at,
            "data": data
        }



