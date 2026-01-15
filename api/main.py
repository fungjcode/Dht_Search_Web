"""
FastAPI 后端 API
提供搜索、详情、DMCA 等接口
"""
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.search_service import SearchService
from database.mysql_client import MySQLClient
import uuid

logger = logging.getLogger(__name__)

# 初始化 FastAPI
app = FastAPI(
    title="DHT Search API",
    description="DHT 种子搜索引擎 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://example.com",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
@app.on_event("startup")
async def startup():
    MySQLClient.initialize()

# Pydantic 模型
class SearchResponse(BaseModel):
    results: List[dict]
    total: int
    page: int
    total_pages: int
    keyword: str

class TorrentDetail(BaseModel):
    torrent: dict
    files: List[dict]

class DMCAComplaint(BaseModel):
    info_hash: str
    complainant_name: str
    complainant_email: EmailStr
    complainant_company: Optional[str] = None
    complaint_reason: str
    copyright_proof: Optional[str] = None

# API 路由
@app.get("/")
async def root():
    return {
        "message": "DHT Search API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/search", response_model=SearchResponse)
async def search(
    request: Request,
    q: str = Query(..., description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    sort: str = Query("time", description="排序方式: time/health/hot/size/relevance"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    min_size: Optional[int] = Query(None, description="最小大小（字节）"),
    max_size: Optional[int] = Query(None, description="最大大小（字节）"),
    has_video: Optional[bool] = Query(None, description="包含视频"),
    has_audio: Optional[bool] = Query(None, description="包含音频"),
    api_key: Optional[str] = Query(None, description="API 密钥"),
):
    """搜索种子"""
    try:
        from services.security_middleware import SecurityMiddleware, get_error_message
        
        # 1. 获取客户端 IP
        client_ip = SecurityMiddleware.get_client_ip(request)
        
        # 2. 检查 IP 黑名单
        if SecurityMiddleware.check_ip_blacklist(client_ip):
            raise HTTPException(status_code=403, detail=get_error_message('blacklist'))
        
        # 3. 检查 User-Agent（可选）
        user_agent = request.headers.get('User-Agent')
        if not SecurityMiddleware.check_user_agent(user_agent):
            raise HTTPException(status_code=403, detail=get_error_message('crawler'))
        
        # 4. 检查 Referer（可选）
        referer = request.headers.get('Referer')
        if not SecurityMiddleware.check_referer(referer):
            raise HTTPException(status_code=403, detail=get_error_message('referer'))
        
        # 5. 检查 API 密钥
        is_valid_key, key_info = SecurityMiddleware.check_api_key(api_key)
        if not is_valid_key:
            raise HTTPException(
                status_code=401,
                detail=get_error_message('invalid_key' if api_key else 'no_key')
            )
        
        # 6. 检查速率限制（白名单 IP 跳过）
        if not SecurityMiddleware.check_ip_whitelist(client_ip):
            rate_limit = key_info.get('rate_limit', 20)
            identifier = api_key if api_key else client_ip
            
            is_allowed, remaining = SecurityMiddleware.check_rate_limit(identifier, rate_limit)
            if not is_allowed:
                raise HTTPException(
                    status_code=429,
                    detail=get_error_message('rate_limit'),
                    headers={'X-RateLimit-Remaining': '0'}
                )
        
        # 7. 检查禁搜词
        is_banned, category = SecurityMiddleware.check_banned_keyword(q)
        if is_banned:
            raise HTTPException(
                status_code=403,
                detail={
                    'error': 'banned_keyword',
                    'message': get_error_message(category, 'zh'),
                    'category': category
                }
            )
        
        # 8. 执行搜索
        filters = {}
        if min_size: filters['min_size'] = min_size
        if max_size: filters['max_size'] = max_size
        if has_video is not None: filters['has_video'] = has_video
        if has_audio is not None: filters['has_audio'] = has_audio
        
        result = SearchService.search(q, page, sort, limit, filters)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/torrent/{info_hash}", response_model=TorrentDetail)
async def get_torrent(info_hash: str):
    """获取种子详情"""
    try:
        # 验证 info_hash 格式
        import re
        if not re.match(r'^[a-fA-F0-9]{40}$', info_hash):
            raise HTTPException(status_code=400, detail="Invalid info_hash format")

        result = SearchService.get_torrent_detail(info_hash)
        if not result:
            raise HTTPException(status_code=404, detail="Torrent not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Torrent detail API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/hot")
async def get_hot_torrents(limit: int = Query(20, ge=1, le=100)):
    """获取热门种子"""
    try:
        results = SearchService.get_hot_torrents(limit)
        return {"results": results}
    except Exception as e:
        logger.error(f"Hot torrents API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/recent")
async def get_recent_torrents(limit: int = Query(20, ge=1, le=100)):
    """获取最新种子"""
    try:
        results = SearchService.get_recent_torrents(limit)
        return {"results": results}
    except Exception as e:
        logger.error(f"Recent torrents API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/dmca")
async def submit_dmca(complaint: DMCAComplaint):
    """提交 DMCA 投诉"""
    try:
        # 验证 info_hash 格式
        import re
        if not re.match(r'^[a-fA-F0-9]{40}$', complaint.info_hash):
            raise HTTPException(status_code=400, detail="Invalid info_hash format")

        # 插入投诉记录
        complaint_id = str(uuid.uuid4())

        # 查询种子 ID
        torrent = MySQLClient.fetch_one(
            "SELECT id FROM torrents WHERE info_hash = %s",
            (complaint.info_hash,)
        )

        torrent_id = torrent['id'] if torrent else None

        MySQLClient.execute(
            """
            INSERT INTO dmca_complaints (
                id, torrent_id, info_hash,
                complainant_name, complainant_email, complainant_company,
                complaint_reason, copyright_proof
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                complaint_id, torrent_id, complaint.info_hash,
                complaint.complainant_name, complaint.complainant_email,
                complaint.complainant_company, complaint.complaint_reason,
                complaint.copyright_proof
            )
        )

        return {
            "success": True,
            "message": "DMCA complaint submitted successfully",
            "complaint_id": complaint_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DMCA API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/stats")
async def get_stats():
    """获取统计信息"""
    try:
        stats = MySQLClient.fetch_one(
            """
            SELECT
                COUNT(*) as total_torrents,
                SUM(CASE WHEN is_blocked THEN 1 ELSE 0 END) as blocked_torrents,
                ROUND(AVG(health_score), 2) as avg_health_score
            FROM torrents
            """
        )
        return stats
    except Exception as e:
        logger.error(f"Stats API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/recommendations/{info_hash}")
async def get_recommendations(
    info_hash: str,
    limit: int = Query(10, ge=1, le=20),
    keyword: str = Query(None, description="搜索关键词，用于基于搜索词推荐")
):
    """获取推荐种子（猜你喜欢）"""
    try:
        # 验证 info_hash 格式
        import re
        if not re.match(r'^[a-fA-F0-9]{40}$', info_hash):
            raise HTTPException(status_code=400, detail="Invalid info_hash format")

        from services.recommendation_service import RecommendationService
        results = RecommendationService.get_recommendations(info_hash, limit, keyword)
        return {"results": results}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recommendations API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
