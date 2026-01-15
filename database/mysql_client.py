"""
MySQL 连接池管理
"""
import pymysql
from dbutils.pooled_db import PooledDB
from contextlib import contextmanager
import logging
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD,
    MYSQL_DATABASE, MYSQL_CHARSET, MYSQL_POOL_SIZE, MYSQL_MAX_OVERFLOW
)

logger = logging.getLogger(__name__)

class MySQLClient:
    _pool = None
    
    @classmethod
    def initialize(cls):
        """初始化连接池"""
        if cls._pool is None:
            try:
                cls._pool = PooledDB(
                    creator=pymysql,
                    maxconnections=MYSQL_POOL_SIZE + MYSQL_MAX_OVERFLOW,
                    mincached=2,
                    maxcached=MYSQL_POOL_SIZE,
                    maxshared=0,
                    blocking=True,
                    maxusage=None,
                    setsession=[],
                    ping=1,
                    host=MYSQL_HOST,
                    port=MYSQL_PORT,
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD,
                    database=MYSQL_DATABASE,
                    charset=MYSQL_CHARSET,
                    cursorclass=pymysql.cursors.DictCursor
                )
                logger.info(f"MySQL connection pool initialized: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")
            except Exception as e:
                logger.error(f"Failed to initialize MySQL pool: {e}")
                raise
    
    @classmethod
    @contextmanager
    def get_connection(cls):
        """获取数据库连接（上下文管理器）"""
        if cls._pool is None:
            cls.initialize()
        
        conn = cls._pool.connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    @classmethod
    def execute(cls, sql, params=None):
        """执行 SQL 语句"""
        with cls.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                return cursor.rowcount
    
    @classmethod
    def execute_many(cls, sql, params_list):
        """批量执行 SQL"""
        with cls.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(sql, params_list)
                return cursor.rowcount
    
    @classmethod
    def fetch_one(cls, sql, params=None):
        """查询单条记录"""
        with cls.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                return cursor.fetchone()
    
    @classmethod
    def fetch_all(cls, sql, params=None):
        """查询多条记录"""
        with cls.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                return cursor.fetchall()
