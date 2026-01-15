"""
种子业务逻辑服务
"""
import uuid
from datetime import datetime, timedelta
import json
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mysql_client import MySQLClient
from database.redis_client import RedisClient
from services.health_calculator import HealthCalculator

logger = logging.getLogger(__name__)

# 数据保留天数（2年）
DATA_RETENTION_DAYS = 730

class TorrentService:
    """种子业务逻辑"""
    
    @staticmethod
    def decode_name(bs):
        """解码种子名称"""
        if not bs: return ""
        if isinstance(bs, str): return bs
        for enc in ['utf-8', 'gbk', 'big5', 'shift-jis']:
            try: return bs.decode(enc)
            except: continue
        return bs.decode('utf-8', 'replace')
    
    @staticmethod
    def analyze_files(files_data):
        """分析文件类型"""
        video_exts = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
        audio_exts = {'.mp3', '.flac', '.wav', '.aac', '.ogg', '.m4a', '.wma'}
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
        doc_exts = {'.pdf', '.doc', '.docx', '.txt', '.epub', '.mobi'}
        software_exts = {'.exe', '.dmg', '.apk', '.deb', '.rpm', '.msi'}
        
        has_video = has_audio = has_image = has_doc = has_software = False
        
        for file_info in files_data:
            path = file_info.get('path', [])
            if isinstance(path, list) and path:
                filename = path[-1] if isinstance(path[-1], str) else path[-1].decode('utf-8', 'replace')
            else:
                filename = str(path)
            
            ext = os.path.splitext(filename.lower())[1]
            if ext in video_exts: has_video = True
            if ext in audio_exts: has_audio = True
            if ext in image_exts: has_image = True
            if ext in doc_exts: has_doc = True
            if ext in software_exts: has_software = True
        
        return has_video, has_audio, has_image, has_doc, has_software
    
    @staticmethod
    def save_torrent(metadata, info_hash, source_ip, event_type):
        """
        保存种子到数据库

        参数:
            metadata: dict - 种子元数据
            info_hash: str - 40位十六进制哈希
            source_ip: str - 来源 IP
            event_type: str - 事件类型

        返回:
            bool: 是否成功保存
        """
        try:
            # 1. Redis 去重检查
            if RedisClient.exists_hash(info_hash):
                logger.debug(f"Hash already exists: {info_hash}")
                return False

            # 2. 检查种子创建时间（超过2年的不保存）
            creation_date_ts = metadata.get(b'creation date', None)
            if creation_date_ts:
                try:
                    # creation date 是 Unix 时间戳
                    creation_date = datetime.fromtimestamp(creation_date_ts)
                    cutoff_date = datetime.now() - timedelta(days=DATA_RETENTION_DAYS)
                    if creation_date < cutoff_date:
                        logger.debug(f"Torrent created before cutoff ({creation_date.date()}), skipping: {info_hash}")
                        return False
                except (ValueError, TypeError) as e:
                    logger.debug(f"Invalid creation date: {e}, skipping check")

            # 3. 解析元数据
            name = TorrentService.decode_name(metadata.get(b'name', b'unknown'))
            is_single_file = b'length' in metadata
            
            if is_single_file:
                total_size = metadata.get(b'length', 0)
                file_count = 1
                files_data = []
            else:
                files = metadata.get(b'files', [])
                total_size = sum(f.get(b'length', 0) for f in files)
                file_count = len(files)
                files_data = files
            
            piece_length = metadata.get(b'piece length', 0)
            pieces = metadata.get(b'pieces', b'')
            piece_count = len(pieces) // 20 if pieces else 0
            is_private = metadata.get(b'private', 0) == 1
            
            # 3. 计算健康度
            now = datetime.now()
            health_data = {
                'first_seen': now,
                'last_seen': now,
                'announce_count': 1,
                'file_count': file_count,
                'total_size': total_size
            }
            health_score = HealthCalculator.calculate(health_data)
            
            # 4. 健康度过滤
            if not HealthCalculator.should_store(health_score):
                logger.debug(f"Low health score ({health_score}), skipping: {info_hash}")
                return False
            
            # 5. 文件类型分析
            has_video, has_audio, has_image, has_doc, has_software = TorrentService.analyze_files(files_data)
            
            # 6. 生成 UUID
            torrent_id = str(uuid.uuid4())
            
            # 7. 插入主表
            sql = """
            INSERT INTO torrents (
                id, info_hash, name, name_utf8, total_size, file_count, is_single_file,
                piece_length, piece_count, is_private,
                first_seen, last_seen, announce_count, source_ips,
                health_score,
                has_video, has_audio, has_image, has_document, has_software
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s,
                %s, %s, %s, %s, %s
            )
            """
            
            params = (
                torrent_id, info_hash, name, name, total_size, file_count, is_single_file,
                piece_length, piece_count, is_private,
                now, now, 1, json.dumps([source_ip]),
                health_score,
                has_video, has_audio, has_image, has_doc, has_software
            )
            
            MySQLClient.execute(sql, params)
            
            # 8. 插入文件列表
            if files_data:
                file_records = []
                for idx, file_info in enumerate(files_data):
                    path_list = file_info.get(b'path', [])
                    if isinstance(path_list, list):
                        file_path = '/'.join(TorrentService.decode_name(p) for p in path_list)
                        file_name = TorrentService.decode_name(path_list[-1]) if path_list else 'unknown'
                    else:
                        file_path = TorrentService.decode_name(path_list)
                        file_name = file_path
                    
                    file_size = file_info.get(b'length', 0)
                    file_ext = os.path.splitext(file_name.lower())[1]
                    
                    file_records.append((
                        str(uuid.uuid4()), torrent_id, file_path, file_name,
                        file_size, idx, file_ext
                    ))
                
                if file_records:
                    file_sql = """
                    INSERT INTO torrent_files (
                        id, torrent_id, file_path, file_name, file_size, file_index, file_extension
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    MySQLClient.execute_many(file_sql, file_records)
            
            # 9. Redis 缓存
            RedisClient.set_hash(info_hash)
            RedisClient.add_recent_torrent(torrent_id)
            
            logger.info(f"Saved torrent: {name} ({info_hash})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save torrent {info_hash}: {e}")
            return False
