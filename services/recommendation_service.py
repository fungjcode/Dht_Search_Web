"""
推荐服务
基于种子名称相似度和分类的推荐算法
"""
import re
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mysql_client import MySQLClient

logger = logging.getLogger(__name__)

class RecommendationService:
    """推荐服务"""
    
    @staticmethod
    def extract_keywords(name):
        """从种子名称中提取关键词"""
        # 移除特殊字符和数字
        name = re.sub(r'[^\w\s\u4e00-\u9fa5]', ' ', name)
        name = re.sub(r'\d+', ' ', name)
        
        # 分词
        words = [w.strip() for w in name.split() if len(w.strip()) > 1]
        return words[:5]  # 取前5个关键词
    
    @staticmethod
    def get_recommendations(info_hash, limit=10, keyword=None):
        """
        获取推荐种子（猜你喜欢）

        策略：
        1. 如果有搜索词keyword，使用搜索词搜索相关种子
        2. 否则基于当前种子的关键词搜索相似种子
        3. 同类型种子（视频/音频等）
        4. 相似大小范围
        5. 排除当前种子
        6. 按健康度排序
        """
        try:
            # 如果有搜索词，直接用搜索词搜索
            if keyword and keyword.strip():
                return RecommendationService.search_by_keyword(keyword, info_hash, limit)

            # 获取当前种子信息
            current = MySQLClient.fetch_one(
                """
                SELECT name, total_size, has_video, has_audio,
                       has_document, has_software, category
                FROM torrents
                WHERE info_hash = %s
                """,
                (info_hash,)
            )

            if not current:
                return []

            # 提取关键词
            keywords = RecommendationService.extract_keywords(current['name'])

            if not keywords:
                # 如果没有关键词，返回同类型的热门种子
                return RecommendationService.get_similar_by_type(current, limit)

            # 构建关键词搜索
            keyword_query = ' '.join([f'+{w}' for w in keywords])

            # 查询相似种子
            results = MySQLClient.fetch_all(
                """
                SELECT
                    info_hash, name, total_size, health_score,
                    has_video, has_audio, created_at
                FROM torrents
                WHERE MATCH(name, name_utf8) AGAINST(%s IN BOOLEAN MODE)
                AND info_hash != %s
                AND is_blocked = FALSE
                ORDER BY health_score DESC
                LIMIT %s
                """,
                (keyword_query, info_hash, limit)
            )

            # 如果结果不足，补充同类型种子
            if len(results) < limit:
                additional = RecommendationService.get_similar_by_type(
                    current,
                    limit - len(results),
                    exclude_hashes=[r['info_hash'] for r in results] + [info_hash]
                )
                results.extend(additional)

            return results

        except Exception as e:
            logger.error(f"Get recommendations error: {e}")
            return []

    @staticmethod
    def search_by_keyword(keyword, exclude_hash=None, limit=10):
        """
        基于搜索词搜索相关种子
        """
        try:
            # 清理搜索词
            keyword = re.sub(r'[^\w\s\u4e00-\u9fa5]', ' ', keyword).strip()
            if not keyword:
                return []

            # 构建搜索查询
            keyword_query = ' '.join([f'+{w}' for w in keyword.split()[:5]])

            params = [keyword_query, limit]
            exclude_sql = ""
            if exclude_hash:
                exclude_sql = "AND info_hash != %s"
                params = [keyword_query, exclude_hash, limit]

            results = MySQLClient.fetch_all(
                f"""
                SELECT
                    info_hash, name, total_size, health_score,
                    has_video, has_audio, created_at
                FROM torrents
                WHERE MATCH(name, name_utf8) AGAINST(%s IN BOOLEAN MODE)
                AND is_blocked = FALSE
                {exclude_sql}
                ORDER BY health_score DESC, hot_score DESC
                LIMIT %s
                """,
                tuple(params)
            )

            return results
        except Exception as e:
            logger.error(f"Search by keyword error: {e}")
            return []
    
    @staticmethod
    def get_similar_by_type(current, limit=10, exclude_hashes=None):
        """根据类型获取相似种子"""
        try:
            exclude_hashes = exclude_hashes or []
            
            # 构建类型条件
            type_conditions = []
            if current.get('has_video'):
                type_conditions.append("has_video = TRUE")
            if current.get('has_audio'):
                type_conditions.append("has_audio = TRUE")
            if current.get('has_document'):
                type_conditions.append("has_document = TRUE")
            if current.get('has_software'):
                type_conditions.append("has_software = TRUE")
            
            if not type_conditions:
                type_conditions = ["1=1"]  # 默认条件
            
            type_sql = " OR ".join(type_conditions)
            
            # 大小范围（±50%）
            min_size = int(current['total_size'] * 0.5)
            max_size = int(current['total_size'] * 1.5)
            
            # 排除已有的哈希
            exclude_sql = ""
            params = [min_size, max_size, limit]
            if exclude_hashes:
                placeholders = ','.join(['%s'] * len(exclude_hashes))
                exclude_sql = f"AND info_hash NOT IN ({placeholders})"
                params = [min_size, max_size] + exclude_hashes + [limit]
            
            sql = f"""
                SELECT 
                    info_hash, name, total_size, health_score,
                    has_video, has_audio, created_at
                FROM torrents
                WHERE ({type_sql})
                AND total_size BETWEEN %s AND %s
                AND is_blocked = FALSE
                {exclude_sql}
                ORDER BY health_score DESC, hot_score DESC
                LIMIT %s
            """
            
            results = MySQLClient.fetch_all(sql, tuple(params))
            return results
            
        except Exception as e:
            logger.error(f"Get similar by type error: {e}")
            return []
