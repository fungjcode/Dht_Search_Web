"""
API Security Middleware
Contains API key authentication, rate limiting, and keyword filtering
"""
import time
import re
from typing import Optional, Tuple
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.security import (
    API_KEYS, ENABLE_API_KEY_AUTH, ALLOW_NO_KEY_ACCESS, NO_KEY_RATE_LIMIT,
    ILLEGAL_KEYWORDS, DMCA_KEYWORDS, CUSTOM_KEYWORDS,
    ALLOWED_REFERERS, ENABLE_REFERER_CHECK,
    BLACKLIST_IPS, WHITELIST_IPS, KNOWN_CRAWLERS, BLOCK_CRAWLERS
)
from database.redis_client import RedisClient, REDIS_KEY_PREFIX

class SecurityMiddleware:
    """API Security Middleware"""

    # Redis key prefix for rate limiting (with project namespace)
    RATE_LIMIT_PREFIX = f"{REDIS_KEY_PREFIX}security:rate_limit:"

    @classmethod
    def check_api_key(cls, api_key: Optional[str]) -> Tuple[bool, dict]:
        """
        Check API key

        Returns: (is_valid, key_info)
        """
        if not ENABLE_API_KEY_AUTH:
            return True, {'rate_limit': NO_KEY_RATE_LIMIT}

        if not api_key:
            if ALLOW_NO_KEY_ACCESS:
                return True, {'rate_limit': NO_KEY_RATE_LIMIT}
            return False, {}

        key_info = API_KEYS.get(api_key)
        if not key_info or not key_info.get('enabled'):
            return False, {}

        return True, key_info

    @classmethod
    def check_rate_limit(cls, identifier: str, limit: int) -> Tuple[bool, int]:
        """
        Check rate limit using Redis

        Args:
            identifier: API key or IP address
            limit: Requests per minute

        Returns: (is_allowed, remaining)
        """
        try:
            client = RedisClient.get_client()
            current_time = int(time.time())
            minute_timestamp = current_time // 60
            key = f"{cls.RATE_LIMIT_PREFIX}{identifier}:{minute_timestamp}"

            # Use pipeline for atomic increment and TTL setup
            pipe = client.pipeline()
            pipe.incr(key)
            # Set TTL to 360 seconds (6 minutes) - ensures automatic cleanup
            pipe.expire(key, 360, nx=True)
            results = pipe.execute()

            count = results[0]
            remaining = max(0, limit - count)
            return count <= limit, remaining

        except Exception:
            # If Redis fails, allow request but log the error
            import logging
            logging.getLogger(__name__).warning("Rate limit check failed, allowing request")
            return True, limit
    
    @classmethod
    def _match_keyword(cls, query_lower: str, keyword: str) -> bool:
        """Match keyword with word boundary to prevent false positives"""
        # Escape regex special characters
        escaped_keyword = re.escape(keyword.lower())
        # Use word boundary for English, fallback to simple match for Chinese
        if re.search(r'[a-zA-Z]', keyword):
            # English keyword: match with word boundary
            pattern = rf'\b{escaped_keyword}\b'
            return bool(re.search(pattern, query_lower))
        else:
            # Chinese keyword: use substring match (no word boundaries)
            return escaped_keyword in query_lower

    @classmethod
    def check_banned_keyword(cls, query: str) -> Tuple[bool, Optional[str]]:
        """
        Check banned keywords (from config file)
        Uses word boundary matching to prevent false positives

        Returns: (is_banned, category)
        """
        query_lower = query.lower()

        # Check illegal keywords
        for keyword in ILLEGAL_KEYWORDS:
            if cls._match_keyword(query_lower, keyword):
                return True, 'illegal'

        # Check DMCA keywords
        for keyword in DMCA_KEYWORDS:
            if cls._match_keyword(query_lower, keyword):
                return True, 'dmca'

        # Check custom keywords
        for keyword in CUSTOM_KEYWORDS:
            if cls._match_keyword(query_lower, keyword):
                return True, 'custom'

        return False, None
    
    @classmethod
    def check_ip_blacklist(cls, ip: str) -> bool:
        """检查 IP 是否在黑名单"""
        return ip in BLACKLIST_IPS
    
    @classmethod
    def check_ip_whitelist(cls, ip: str) -> bool:
        """检查 IP 是否在白名单"""
        return ip in WHITELIST_IPS
    
    @classmethod
    def check_referer(cls, referer: Optional[str]) -> bool:
        """检查 Referer"""
        if not ENABLE_REFERER_CHECK:
            return True
        
        if not referer:
            return False
        
        for allowed in ALLOWED_REFERERS:
            if allowed in referer:
                return True
        
        return False
    
    @classmethod
    def check_user_agent(cls, user_agent: Optional[str]) -> bool:
        """检查 User-Agent"""
        if not BLOCK_CRAWLERS or not user_agent:
            return True
        
        user_agent_lower = user_agent.lower()
        for crawler in KNOWN_CRAWLERS:
            if crawler in user_agent_lower:
                return False
        
        return True
    
    @classmethod
    def get_client_ip(cls, request: Request) -> str:
        """获取客户端 IP"""
        # 优先从 X-Forwarded-For 获取（如果使用了反向代理）
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        
        # 从 X-Real-IP 获取
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # 直接从 client 获取
        if request.client:
            return request.client.host
        
        return 'unknown'

def get_error_message(category: str, lang: str = 'zh') -> str:
    """获取错误提示消息"""
    messages = {
        'zh': {
            'illegal': '您搜索的内容可能违反法律法规，已被系统拦截。',
            'dmca': '您搜索的内容涉及版权保护，已被系统拦截。',
            'custom': '您搜索的内容已被系统拦截。',
            'rate_limit': '请求过于频繁，请稍后再试。',
            'invalid_key': 'API 密钥无效或已禁用。',
            'no_key': '缺少 API 密钥。',
            'blacklist': '您的 IP 已被封禁。',
            'referer': '非法来源请求。',
            'crawler': '不允许爬虫访问。',
        },
        'en': {
            'illegal': 'Your search may violate laws and has been blocked.',
            'dmca': 'Your search involves copyrighted content and has been blocked.',
            'custom': 'Your search has been blocked.',
            'rate_limit': 'Too many requests. Please try again later.',
            'invalid_key': 'Invalid or disabled API key.',
            'no_key': 'API key required.',
            'blacklist': 'Your IP has been blocked.',
            'referer': 'Invalid referer.',
            'crawler': 'Crawlers are not allowed.',
        }
    }
    
    return messages.get(lang, messages['zh']).get(category, messages[lang]['custom'])
