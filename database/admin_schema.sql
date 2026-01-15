-- 后台管理相关表结构
-- 添加到 schema.sql 或作为迁移脚本执行

USE dht_crawler;

-- 管理员表
CREATE TABLE IF NOT EXISTS admins (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    email VARCHAR(100) COMMENT '邮箱',
    role VARCHAR(20) DEFAULT 'admin' COMMENT '角色（admin/moderator）',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    last_login DATETIME COMMENT '最后登录时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='管理员表';

-- DMCA 投诉表
CREATE TABLE IF NOT EXISTS dmca_complaints (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    torrent_id CHAR(36) COMMENT '种子 ID',
    info_hash CHAR(40) COMMENT 'Info Hash',
    
    -- 投诉信息
    complainant_name VARCHAR(200) NOT NULL COMMENT '投诉人姓名',
    complainant_email VARCHAR(200) NOT NULL COMMENT '投诉人邮箱',
    complainant_company VARCHAR(200) COMMENT '投诉公司',
    complaint_reason TEXT NOT NULL COMMENT '投诉原因',
    copyright_proof TEXT COMMENT '版权证明',
    
    -- 处理状态
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态（pending/reviewing/approved/rejected）',
    admin_id CHAR(36) COMMENT '处理管理员 ID',
    admin_note TEXT COMMENT '管理员备注',
    processed_at DATETIME COMMENT '处理时间',
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '投诉时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    FOREIGN KEY (torrent_id) REFERENCES torrents(id) ON DELETE SET NULL,
    FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE SET NULL,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='DMCA 投诉表';

-- 操作日志表
CREATE TABLE IF NOT EXISTS admin_logs (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    admin_id CHAR(36) NOT NULL COMMENT '管理员 ID',
    action VARCHAR(50) NOT NULL COMMENT '操作类型',
    target_type VARCHAR(50) COMMENT '目标类型（torrent/complaint）',
    target_id CHAR(36) COMMENT '目标 ID',
    details JSON COMMENT '操作详情',
    ip_address VARCHAR(50) COMMENT 'IP 地址',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    
    FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE CASCADE,
    INDEX idx_admin_id (admin_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='管理员操作日志表';

-- 种子状态枚举值说明
-- torrents.is_blocked: 是否被屏蔽
-- torrents.block_reason: 屏蔽原因
-- 可能的值：
--   'dmca' - DMCA 投诉
--   'illegal' - 非法内容
--   'spam' - 垃圾信息
--   'duplicate' - 重复内容
--   'other' - 其他原因
