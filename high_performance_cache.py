import time
from cachetools import TTLCache

class HighPerformanceCacheEngine:
    """Sub-5ms In-Memory Caching & Database Offloading Engine."""

    def __init__(self):
        self.tenant_cache = TTLCache(maxsize=1000, ttl=120)
        self.catalog_cache = TTLCache(maxsize=1000, ttl=120)
        self.response_cache = TTLCache(maxsize=2000, ttl=60)

    def get_cached_tenant(self, instance_name: str):
        return self.tenant_cache.get(instance_name)

    def set_cached_tenant(self, instance_name: str, tenant_data: dict):
        self.tenant_cache[instance_name] = tenant_data

    def get_cached_catalog(self, tenant_id: str):
        return self.catalog_cache.get(tenant_id)

    def set_cached_catalog(self, tenant_id: str, catalog_text: str):
        self.catalog_cache[tenant_id] = catalog_text

hp_cache = HighPerformanceCacheEngine()
