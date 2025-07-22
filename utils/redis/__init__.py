from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool
from utils.config import config

pool = ConnectionPool(host=config.redis_host, port=config.redis_port, max_connections=64)

async def getRedisClient():
    """
    Create and return a Redis client instance.
    """
    redis = Redis(
        connection_pool=pool,
        db=0,
        decode_responses=True
    )
    try:
        yield redis
    finally:
        await redis.close()