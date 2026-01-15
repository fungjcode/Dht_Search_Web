"""
数据库建表脚本
MySQL 8.0+
"""

-- 创建数据库
CREATE DATABASE IF NOT EXISTS dht_crawler DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE dht_crawler;

-- 种子主表
CREATE TABLE IF NOT EXISTS torrents (
    -- 主键和唯一标识
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    info_hash CHAR(40) UNIQUE NOT NULL COMMENT 'SHA1 哈希',
    
    -- 基础信息
    name VARCHAR(500) NOT NULL COMMENT '种子名称',
    name_utf8 VARCHAR(500) COMMENT 'UTF-8 解码名称',
    total_size BIGINT NOT NULL COMMENT '总大小（字节）',
    file_count INT DEFAULT 1 COMMENT '文件数量',
    is_single_file BOOLEAN DEFAULT TRUE COMMENT '是否单文件',
    
    -- 分片信息
    piece_length INT COMMENT '分片大小',
    piece_count INT COMMENT '分片数量',
    
    -- 可选元数据
    is_private BOOLEAN DEFAULT FALSE COMMENT '是否私有种子',
    
    -- DHT 发现信息
    first_seen DATETIME NOT NULL COMMENT '首次发现时间',
    last_seen DATETIME NOT NULL COMMENT '最后发现时间',
    announce_count INT DEFAULT 1 COMMENT '被 announce 次数',
    source_ips JSON COMMENT '来源 IP 列表',
    
    -- 健康度评分
    health_score DECIMAL(5,2) DEFAULT 0 COMMENT '健康度评分 0-100',
    
    -- 热度统计
    search_count INT DEFAULT 0 COMMENT '搜索次数',
    download_count INT DEFAULT 0 COMMENT '下载次数',
    view_count INT DEFAULT 0 COMMENT '浏览次数',
    hot_score DECIMAL(10,2) DEFAULT 0 COMMENT '热度评分',
    
    -- 分类和标签
    category VARCHAR(50) COMMENT '分类',
    sub_category VARCHAR(50) COMMENT '子分类',
    tags JSON COMMENT '标签数组',
    language VARCHAR(10) COMMENT '语言代码',
    
    -- 内容分析
    has_video BOOLEAN DEFAULT FALSE COMMENT '包含视频',
    has_audio BOOLEAN DEFAULT FALSE COMMENT '包含音频',
    has_image BOOLEAN DEFAULT FALSE COMMENT '包含图片',
    has_document BOOLEAN DEFAULT FALSE COMMENT '包含文档',
    has_software BOOLEAN DEFAULT FALSE COMMENT '包含软件',
    
    -- 质量标记
    quality VARCHAR(20) COMMENT '质量（720p/1080p/4K）',
    codec VARCHAR(50) COMMENT '编码格式',
    
    -- 状态标记
    is_verified BOOLEAN DEFAULT FALSE COMMENT '是否人工验证',
    is_blocked BOOLEAN DEFAULT FALSE COMMENT '是否屏蔽',
    block_reason VARCHAR(200) COMMENT '屏蔽原因',
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引
    INDEX idx_info_hash (info_hash),
    INDEX idx_health_score (health_score DESC),
    INDEX idx_hot_score (hot_score DESC),
    INDEX idx_last_seen (last_seen DESC),
    INDEX idx_category (category, sub_category),
    INDEX idx_name (name(100)),
    FULLTEXT INDEX ft_name (name, name_utf8) WITH PARSER ngram
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='种子主表';

-- 文件列表表
CREATE TABLE IF NOT EXISTS torrent_files (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    torrent_id CHAR(36) NOT NULL COMMENT '种子 ID',
    
    -- 文件信息
    file_path VARCHAR(1000) NOT NULL COMMENT '完整路径',
    file_name VARCHAR(500) NOT NULL COMMENT '文件名',
    file_size BIGINT NOT NULL COMMENT '文件大小',
    file_index INT NOT NULL COMMENT '文件索引',
    
    -- 文件类型
    file_extension VARCHAR(20) COMMENT '文件扩展名',
    mime_type VARCHAR(100) COMMENT 'MIME 类型',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    FOREIGN KEY (torrent_id) REFERENCES torrents(id) ON DELETE CASCADE,
    INDEX idx_torrent_id (torrent_id),
    INDEX idx_extension (file_extension)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件列表表';

-- 搜索关键词表
CREATE TABLE IF NOT EXISTS search_keywords (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    keyword VARCHAR(200) NOT NULL COMMENT '关键词',
    search_count INT DEFAULT 1 COMMENT '搜索次数',
    last_searched DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '最后搜索时间',
    
    UNIQUE KEY uk_keyword (keyword),
    INDEX idx_search_count (search_count DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='搜索关键词表';

-- 种子-关键词关联表
CREATE TABLE IF NOT EXISTS torrent_keywords (
    torrent_id CHAR(36) NOT NULL COMMENT '种子 ID',
    keyword_id CHAR(36) NOT NULL COMMENT '关键词 ID',
    
    PRIMARY KEY (torrent_id, keyword_id),
    FOREIGN KEY (torrent_id) REFERENCES torrents(id) ON DELETE CASCADE,
    FOREIGN KEY (keyword_id) REFERENCES search_keywords(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='种子-关键词关联表';
