"""
Redis Connection Pool Management
"""
import redis
from redis import ConnectionPool
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB, REDIS_POOL_SIZE
)

logger = logging.getLogger(__name__)

# Redis key prefix for namespace isolation
REDIS_KEY_PREFIX = "dhtsearch:"

class RedisClient:
    _pool = None
    _client = None
    
    @classmethod
    def initialize(cls):
        """初始化 Redis 连接池"""
        if cls._pool is None:
            try:
                cls._pool = ConnectionPool(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    password=REDIS_PASSWORD,
                    db=REDIS_DB,
                    max_connections=REDIS_POOL_SIZE,
                    decode_responses=False  # 保持字节模式
                )
                cls._client = redis.Redis(connection_pool=cls._pool)
                # 测试连接
                cls._client.ping()
                logger.info(f"Redis connection pool initialized: {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
            except Exception as e:
                logger.error(f"Failed to initialize Redis pool: {e}")
                raise
    
    @classmethod
    def get_client(cls):
        """获取 Redis 客户端"""
        if cls._client is None:
            cls.initialize()
        return cls._client
    
    @classmethod
    def exists_hash(cls, info_hash):
        """Check if hash exists"""
        client = cls.get_client()
        key = f"{REDIS_KEY_PREFIX}dht:hash:{info_hash}"
        return client.exists(key)

    @classmethod
    def set_hash(cls, info_hash, ttl=604800):
        """Set hash with 7-day TTL"""
        client = cls.get_client()
        key = f"{REDIS_KEY_PREFIX}dht:hash:{info_hash}"
        client.setex(key, ttl, 1)

    @classmethod
    def add_hot_torrent(cls, torrent_id, hot_score):
        """Add to hot torrent list"""
        client = cls.get_client()
        key = f"{REDIS_KEY_PREFIX}dht:hot:torrents"
        client.zadd(key, {torrent_id: hot_score})
        # Keep only top 100
        client.zremrangebyrank(key, 0, -101)

    @classmethod
    def add_recent_torrent(cls, torrent_id):
        """Add to recent torrent list"""
        client = cls.get_client()
        key = f"{REDIS_KEY_PREFIX}dht:recent:torrents"
        client.lpush(key, torrent_id)
        # Keep only first 1000
        client.ltrim(key, 0, 999)
