"""
搜索服务
基于 MySQL ngram 全文索引的高性能搜索
"""
import re
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mysql_client import MySQLClient
from database.redis_client import RedisClient

logger = logging.getLogger(__name__)

class SearchService:
    """搜索服务"""
    
    # 排序方式映射
    SORT_MODES = {
        'time': 'created_at DESC',           # 时间倒序（最新）
        'health': 'health_score DESC',       # 健康度倒序
        'hot': 'hot_score DESC',             # 热度倒序
        'size': 'total_size DESC',           # 大小倒序
        'relevance': 'score DESC'            # 相关度倒序（全文搜索评分）
    }
    
    @staticmethod
    def preprocess_keyword(keyword):
        """
        预处理搜索关键词
        
        1. 移除特殊字符
        2. 分词
        3. 构建布尔查询
        
        示例:
            "复仇者联盟4" -> "+复仇者 +联盟 +4"
            "权力的游戏 1080p" -> "+权力 +游戏 +1080p"
        """
        if not keyword:
            return ""
        
        # 移除特殊字符，保留中文、英文、数字、空格
        keyword = re.sub(r'[^\w\s\u4e00-\u9fa5]', ' ', keyword)
        
        # 分割成词
        words = [w.strip() for w in keyword.split() if len(w.strip()) > 0]
        
        # 过滤单字符（除非是数字）
        words = [w for w in words if len(w) > 1 or w.isdigit()]
        
        if not words:
            return keyword  # 如果处理后为空，返回原始关键词
        
        # 构建布尔查询：每个词都必须包含
        return ' '.join([f'+{w}' for w in words])
    
    @staticmethod
    def search(keyword, page=1, sort='time', limit=20, filters=None):
        """
        搜索种子
        
        参数:
            keyword: str - 搜索关键词
            page: int - 页码（从1开始）
            sort: str - 排序方式 (time/health/hot/size/relevance)
            limit: int - 每页数量
            filters: dict - 额外过滤条件 {
                'min_size': int,  # 最小大小（字节）
                'max_size': int,  # 最大大小
                'has_video': bool,
                'has_audio': bool,
                'quality': str,  # 720p/1080p/4K
            }
        
        返回:
            {
                'results': [...],
                'total': int,
                'page': int,
                'total_pages': int
            }
        """
        try:
            # 1. 预处理关键词
            processed_keyword = SearchService.preprocess_keyword(keyword)

            # 如果关键词为空，返回空结果
            if not processed_keyword or not keyword.strip():
                return {
                    'results': [],
                    'total': 0,
                    'page': page,
                    'total_pages': 0,
                    'keyword': keyword,
                    'processed_keyword': processed_keyword
                }

            # 2. 构建查询条件
            where_clauses = ["is_blocked = FALSE"]
            params = []
            
            # 全文搜索条件
            if processed_keyword:
                where_clauses.append("MATCH(name, name_utf8) AGAINST(%s IN BOOLEAN MODE)")
                params.append(processed_keyword)
            
            # 额外过滤条件
            if filters:
                if 'min_size' in filters:
                    where_clauses.append("total_size >= %s")
                    params.append(filters['min_size'])
                
                if 'max_size' in filters:
                    where_clauses.append("total_size <= %s")
                    params.append(filters['max_size'])
                
                if 'has_video' in filters:
                    where_clauses.append("has_video = %s")
                    params.append(filters['has_video'])
                
                if 'has_audio' in filters:
                    where_clauses.append("has_audio = %s")
                    params.append(filters['has_audio'])
                
                if 'quality' in filters:
                    where_clauses.append("quality = %s")
                    params.append(filters['quality'])
            
            where_sql = " AND ".join(where_clauses)
            
            # 3. 获取排序方式
            order_by = SearchService.SORT_MODES.get(sort, SearchService.SORT_MODES['time'])
            
            # 4. 查询总数
            count_sql = f"SELECT COUNT(*) as total FROM torrents WHERE {where_sql}"
            count_result = MySQLClient.fetch_one(count_sql, tuple(params))
            total = count_result['total'] if count_result else 0
            
            # 5. 查询结果
            offset = (page - 1) * limit
            
            # 如果是相关度排序，添加评分字段
            if sort == 'relevance' and processed_keyword:
                select_fields = """
                    id, info_hash, name, total_size, file_count,
                    health_score, hot_score, search_count,
                    has_video, has_audio, quality,
                    last_seen, created_at,
                    MATCH(name, name_utf8) AGAINST(%s IN BOOLEAN MODE) as score
                """
                params_with_score = [processed_keyword] + params + [limit, offset]
            else:
                select_fields = """
                    id, info_hash, name, total_size, file_count,
                    health_score, hot_score, search_count,
                    has_video, has_audio, quality,
                    last_seen, created_at
                """
                params_with_score = params + [limit, offset]
            
            search_sql = f"""
                SELECT {select_fields}
                FROM torrents
                WHERE {where_sql}
                ORDER BY {order_by}
                LIMIT %s OFFSET %s
            """
            
            results = MySQLClient.fetch_all(search_sql, tuple(params_with_score))
            
            # 6. 计算总页数
            total_pages = (total + limit - 1) // limit

            # 7. 更新搜索次数（批量更新）
            if results and keyword:
                try:
                    ids = [r['id'] for r in results]
                    placeholders = ','.join(['%s'] * len(ids))
                    MySQLClient.execute(
                        f"UPDATE torrents SET search_count = search_count + 1 WHERE id IN ({placeholders})",
                        tuple(ids)
                    )
                except Exception as e:
                    logger.error(f"Failed to update search count: {e}")
            
            return {
                'results': results,
                'total': total,
                'page': page,
                'total_pages': total_pages,
                'keyword': keyword,
                'processed_keyword': processed_keyword
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                'results': [],
                'total': 0,
                'page': page,
                'total_pages': 0,
                'error': str(e)
            }
    
    @staticmethod
    def get_torrent_detail(info_hash):
        """
        获取种子详情
        
        参数:
            info_hash: str - 种子哈希
        
        返回:
            {
                'torrent': {...},
                'files': [...]
            }
        """
        try:
            # 查询种子信息
            torrent = MySQLClient.fetch_one(
                """
                SELECT * FROM torrents
                WHERE info_hash = %s AND is_blocked = FALSE
                """,
                (info_hash,)
            )
            
            if not torrent:
                return None
            
            # 查询文件列表
            files = MySQLClient.fetch_all(
                """
                SELECT file_name, file_path, file_size, file_extension
                FROM torrent_files
                WHERE torrent_id = %s
                ORDER BY file_index
                """,
                (torrent['id'],)
            )
            
            # 更新浏览次数
            MySQLClient.execute(
                "UPDATE torrents SET view_count = view_count + 1 WHERE id = %s",
                (torrent['id'],)
            )
            
            return {
                'torrent': torrent,
                'files': files
            }
            
        except Exception as e:
            logger.error(f"Get torrent detail error: {e}")
            return None
    
    @staticmethod
    def get_hot_torrents(limit=20):
        """获取热门种子"""
        try:
            results = MySQLClient.fetch_all(
                """
                SELECT 
                    info_hash, name, total_size, health_score, hot_score
                FROM torrents
                WHERE is_blocked = FALSE
                ORDER BY hot_score DESC, search_count DESC
                LIMIT %s
                """,
                (limit,)
            )
            return results
        except Exception as e:
            logger.error(f"Get hot torrents error: {e}")
            return []
    
    @staticmethod
    def get_recent_torrents(limit=20):
        """获取最新种子"""
        try:
            results = MySQLClient.fetch_all(
                """
                SELECT 
                    info_hash, name, total_size, health_score, created_at
                FROM torrents
                WHERE is_blocked = FALSE
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,)
            )
            return results
        except Exception as e:
            logger.error(f"Get recent torrents error: {e}")
            return []
