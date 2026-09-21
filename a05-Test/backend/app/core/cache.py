import redis
import json
from typing import Optional, Any

class RedisCache:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
    
    async def get(self, key: str) -> Optional[Any]:
        value = self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        return self.redis_client.setex(key, expire, json.dumps(value))
    
    async def delete(self, key: str) -> bool:
        return bool(self.redis_client.delete(key))

