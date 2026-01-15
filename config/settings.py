# 配置文件
# 生产环境支持通过环境变量覆盖配置
# 环境变量命名规则: DHT_配置项名称 (例如: DHT_MYSQL_HOST)

import os

def get_env(key: str, default):
    """从环境变量读取配置，不存在则返回默认值"""
    env_key = f"DHT_{key}"
    return os.environ.get(env_key, default)

# ============================================
# MySQL 配置
# ============================================
MYSQL_HOST = get_env('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(get_env('MYSQL_PORT', '3306'))
MYSQL_USER = get_env('MYSQL_USER', 'dht_crawler')
MYSQL_PASSWORD = get_env('MYSQL_PASSWORD', '')
MYSQL_DATABASE = get_env('MYSQL_DATABASE', 'dht_crawler')
MYSQL_CHARSET = get_env('MYSQL_CHARSET', 'utf8mb4')
MYSQL_POOL_SIZE = int(get_env('MYSQL_POOL_SIZE', '20'))
MYSQL_MAX_OVERFLOW = int(get_env('MYSQL_MAX_OVERFLOW', '30'))

# ============================================
# Redis 配置
# ============================================
REDIS_HOST = get_env('REDIS_HOST', 'localhost')
REDIS_PORT = int(get_env('REDIS_PORT', '6379'))
REDIS_PASSWORD = get_env('REDIS_PASSWORD', None)
if REDIS_PASSWORD == '' or REDIS_PASSWORD == 'None':
    REDIS_PASSWORD = None
REDIS_DB = int(get_env('REDIS_DB', '0'))
REDIS_POOL_SIZE = int(get_env('REDIS_POOL_SIZE', '50'))

# ============================================
# DHT 爬虫配置
# ============================================
DHT_SERVERS = int(get_env('DHT_SERVERS', '4'))
MAX_NODE_QSIZE = int(get_env('MAX_NODE_QSIZE', '500'))
METADATA_WORKERS = int(get_env('METADATA_WORKERS', '400'))
METADATA_TIMEOUT = int(get_env('METADATA_TIMEOUT', '6'))

# ============================================
# 数据库写入配置
# ============================================
DB_BATCH_SIZE = int(get_env('DB_BATCH_SIZE', '100'))
DB_BATCH_TIMEOUT = int(get_env('DB_BATCH_TIMEOUT', '10'))
DB_WRITER_WORKERS = int(get_env('DB_WRITER_WORKERS', '4'))

# ============================================
# 数据过滤配置
# ============================================
MAX_TORRENT_AGE_DAYS = int(get_env('MAX_TORRENT_AGE_DAYS', '730'))
MIN_HEALTH_SCORE = int(get_env('MIN_HEALTH_SCORE', '5'))

# ============================================
# Redis 缓存配置
# ============================================
CACHE_HASH_TTL = int(get_env('CACHE_HASH_TTL', '604800'))
CACHE_HOT_TORRENTS_SIZE = int(get_env('CACHE_HOT_TORRENTS_SIZE', '100'))
