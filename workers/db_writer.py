"""
数据库批量写入工作进程
"""
import multiprocessing
import time
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.torrent_service import TorrentService
from database.mysql_client import MySQLClient
from database.redis_client import RedisClient

logger = logging.getLogger(__name__)

class DBWriter:
    """数据库批量写入器"""
    
    @staticmethod
    def worker(write_queue, batch_size=100, batch_timeout=10):
        """
        批量写入工作进程
        
        参数:
            write_queue: multiprocessing.Queue - 写入队列
            batch_size: int - 批量大小
            batch_timeout: float - 批量超时（秒）
        """
        # 初始化数据库连接
        try:
            MySQLClient.initialize()
            RedisClient.initialize()
            logger.info("DB Writer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize DB Writer: {e}")
            return
        
        batch = []
        last_write = time.time()
        
        while True:
            try:
                # 获取任务
                try:
                    task = write_queue.get(timeout=1)
                except Exception:
                    task = None
                
                if task:
                    batch.append(task)
                
                # 判断是否需要批量写入
                should_write = (
                    len(batch) >= batch_size or
                    (batch and time.time() - last_write >= batch_timeout)
                )
                
                if should_write:
                    success_count = 0
                    for item in batch:
                        try:
                            metadata, info_hash, source_ip, event_type = item
                            if TorrentService.save_torrent(metadata, info_hash, source_ip, event_type):
                                success_count += 1
                        except Exception as e:
                            logger.error(f"Failed to save torrent: {e}")
                    
                    if success_count > 0:
                        logger.info(f"Batch write completed: {success_count}/{len(batch)} torrents saved")
                    
                    batch = []
                    last_write = time.time()
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"DB Writer error: {e}")
