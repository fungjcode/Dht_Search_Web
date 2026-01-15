"""
健康度计算算法
基于种子创建时间，一次计算，入库后不再更新
"""
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class HealthCalculator:
    """种子健康度计算器"""

    @staticmethod
    def calculate(torrent_data):
        """
        计算种子健康度评分 (0-100)
        仅基于 first_seen（入库时间），入库后不再更新

        参数:
            torrent_data: dict {
                'first_seen': datetime,  # 入库时间
            }

        返回:
            float: 健康度评分 0-100，超过2年返回 0
        """
        try:
            now = datetime.now()
            first_seen = torrent_data.get('first_seen', now)

            # 计算距今天数
            age_days = (now - first_seen).days

            # 超过2年不存储
            if age_days > 730:
                return 0

            # 基于时间的评分（0-100）
            if age_days <= 7:
                return 100.0      # 0-7天：100分
            elif age_days <= 30:
                return 80.0       # 7-30天：80分
            elif age_days <= 90:
                return 60.0       # 30-90天：60分
            elif age_days <= 365:
                return 40.0       # 90-365天：40分
            else:  # 365-730天
                return 20.0

        except Exception as e:
            logger.error(f"Health calculation error: {e}")
            return 0.0

    @staticmethod
    def should_store(health_score, min_score=5):
        """判断是否应该存储（健康度过滤）"""
        return health_score >= min_score
