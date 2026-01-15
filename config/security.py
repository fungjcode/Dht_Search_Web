# ============================================
# 生产环境配置
# ============================================
# 本配置文件支持通过环境变量覆盖配置
# 环境变量命名规则: DHT_配置项名称 (例如: DHT_API_KEY_AUTH)
# ============================================

import os

# 环境变量读取辅助函数
def get_env(key: str, default):
    """从环境变量读取配置，不存在则返回默认值"""
    env_key = f"DHT_{key}"
    return os.environ.get(env_key, default)

# ============================================
# 禁搜词配置
# ============================================

# 违法内容关键词（中国法律 - 需严格遵守）
ILLEGAL_KEYWORDS = [
    # 政治敏感
    '六四', '法轮功', '天安门', '达赖', 'liu si', 'falun gong', 'tiananmen',

    # 暴力恐怖
    '恐怖袭击', '制作炸弹', 'ISIS', '基地组织', 'terrorist', 'bomb making',

    # 色情内容（严格禁止）
    '儿童色情', 'child porn', 'child pornography', 'cp', 'lolita', '幼女',
    '未成年色情', 'teen porn', '微型未成年', 'little children',

    # 毒品相关
    '冰毒', '海洛因', '可卡因', '大麻', 'heroin', 'cocaine', 'meth', 'marijuana',
    '摇头丸', 'K粉', '氯胺酮', 'MDMA', '贩毒', '制毒',

    # 赌博相关
    '网络赌博', '赌博网站', '博彩', 'online gambling', 'casino', 'bet365',
    '亚博体育', '万博体育', '必威体育', '外围彩票',

    # 枪支武器
    '买枪', '购买武器', '黑市枪支', 'buy gun', 'illegal weapon', '枪支交易',
    '自制枪', '仿真枪',

    # 诈骗相关
    '电信诈骗', '杀猪盘', '菠菜', '盘口', '内幕消息', '稳赚不赔',
    '代开发票', '假发票', '增值税发票',

    # 身份证相关
    '身份证买卖', '身份证复制', '代办身份证', '实名认证买卖',
]

# DMCA 版权保护关键词（盗版、破解内容）
DMCA_KEYWORDS = [
    # ===== 主流流媒体平台破解 =====
    # Netflix 生态
    'Netflix crack', 'Netflix 破解', 'Netflix 账号共享', 'Netflix 共享账号',
    'Netflix 永久账号', 'Netflix VIP', 'Netflix 激活码',

    # Disney+ 生态
    'Disney+ crack', 'Disney+ 破解', 'Disney+ 账号', 'Disney+ 共享',

    # HBO 生态
    'HBO Max crack', 'HBO 破解', 'HBO 账号', 'HBO GO crack',

    # Amazon Prime
    'Amazon Prime crack', 'Amazon Prime 破解', 'Prime Video crack',

    # Apple TV/Music
    'Apple TV+ crack', 'Apple Music crack', 'iTunes 破解',

    # Spotify
    'Spotify crack', 'Spotify 破解', 'Spotify Premium crack', 'Spotify 破解版',

    # YouTube
    'YouTube Premium crack', 'YouTube Vanced', 'YouTube 破解',

    # ===== 软件破解 =====
    # Adobe 全家桶
    'Adobe crack', 'Adobe 破解', 'Photoshop crack', 'Photoshop 破解',
    'Premiere crack', 'Premiere 破解', 'After Effects crack', 'AE 破解',
    'Illustrator crack', 'AI 破解', 'InDesign crack', 'ID 破解',
    'Lightroom crack', 'LR 破解', 'Acrobat crack', 'PDF 破解',

    # Microsoft 全家桶
    'Windows crack', 'Windows 破解', 'Office crack', 'Office 破解',
    'Windows 10 crack', 'Windows 11 crack', 'Office 365 crack',
    'Microsoft Office 破解', 'Win10 激活工具', 'Office 激活工具',

    # 专业软件
    'AutoCAD crack', 'AutoCAD 破解', 'Maya crack', 'Maya 破解',
    '3ds Max crack', '3dsmax 破解', 'Cinema 4D crack', 'C4D 破解',
    'SolidWorks crack', 'SW 破解', 'Matlab crack', 'Matlab 破解',
    'LabVIEW crack', 'Keil crack', 'Altium crack', 'PADS crack',

    # 办公工具
    'Photoshop crack', 'WinRAR crack', 'WinRAR 破解', 'IDM crack',
    'Internet Download Manager crack', '格式工厂 破解',

    # ===== 杀毒软件（注意：有些国家允许）=====
    # 这里根据当地法律调整
    # 'Norton crack', 'Kaspersky crack', 'McAfee crack',

]

# 自定义禁搜词（可根据业务需要添加）
CUSTOM_KEYWORDS = [
    # 示例：竞品名称
    # '竞争对手名称',

    # 示例：敏感业务词
    # '特殊服务',

    # 可以根据运营需求持续添加
]

# ============================================
# API 密钥配置
# ============================================

# API 密钥列表（生产环境应该从环境变量或数据库读取）
# 环境变量格式: DHT_API_KEYS_JSON = '{"key1": {"name": "name1", "rate_limit": 60, "enabled": true}}'
def _load_api_keys():
    """从环境变量加载 API 密钥配置"""
    import json
    env_keys = os.environ.get('DHT_API_KEYS_JSON')
    if env_keys:
        try:
            return json.loads(env_keys)
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse DHT_API_KEYS_JSON: {e}")
    return {}

# 默认内置密钥（开发环境使用）
DEFAULT_API_KEYS = {
    'demo_key_12345': {
        'name': '演示密钥',
        'rate_limit': 60,
        'enabled': True
    },
    'frontend_key_67890': {
        'name': '前端密钥',
        'rate_limit': 100,
        'enabled': True
    },
}

API_KEYS = _load_api_keys()
if not API_KEYS:
    # 如果没有环境变量配置，使用默认密钥
    API_KEYS = DEFAULT_API_KEYS

# 是否启用 API 密钥认证（生产环境应设为 True）
ENABLE_API_KEY_AUTH = get_env('API_KEY_AUTH', False)

# 是否允许无密钥访问（仅用于公开 API）
ALLOW_NO_KEY_ACCESS = get_env('ALLOW_NO_KEY_ACCESS', True)

# 无密钥访问的速率限制（每分钟请求数）
NO_KEY_RATE_LIMIT = int(get_env('NO_KEY_RATE_LIMIT', '20'))

# ============================================
# 速率限制配置
# ============================================

# Redis 配置（用于速率限制，可被环境变量覆盖）
RATE_LIMIT_REDIS_HOST = get_env('RATE_LIMIT_REDIS_HOST', 'localhost')
RATE_LIMIT_REDIS_PORT = int(get_env('RATE_LIMIT_REDIS_PORT', '6379'))
RATE_LIMIT_REDIS_DB = int(get_env('RATE_LIMIT_REDIS_DB', '1'))

# 速率限制时间窗口（秒）
RATE_LIMIT_WINDOW = int(get_env('RATE_LIMIT_WINDOW', '60'))  # 1分钟

# ============================================
# 安全配置
# ============================================

# 允许的 Referer 域名（防盗链）
# 环境变量格式: DHT_ALLOWED_REFERERS = 'localhost,127.0.0.1,example.com'
def _load_allowed_referers():
    """从环境变量加载允许的 Referer 列表"""
    env_referers = os.environ.get('DHT_ALLOWED_REFERERS')
    if env_referers:
        return [ref.strip() for ref in env_referers.split(',')]
    return ['localhost', '127.0.0.1', 'example.com']

ALLOWED_REFERERS = _load_allowed_referers()

# 是否启用 Referer 检查
ENABLE_REFERER_CHECK = get_env('ENABLE_REFERER_CHECK', False)

# 黑名单 IP
# 环境变量格式: DHT_BLACKLIST_IPS = '192.168.1.100,10.0.0.50'
def _load_blacklist_ips():
    """从环境变量加载黑名单 IP"""
    env_ips = os.environ.get('DHT_BLACKLIST_IPS')
    if env_ips:
        return [ip.strip() for ip in env_ips.split(',')]
    return []

BLACKLIST_IPS = _load_blacklist_ips()

# 白名单 IP（不受速率限制）
# 环境变量格式: DHT_WHITELIST_IPS = '192.168.1.1,10.0.0.1'
def _load_whitelist_ips():
    """从环境变量加载白名单 IP"""
    env_ips = os.environ.get('DHT_WHITELIST_IPS')
    if env_ips:
        return [ip.strip() for ip in env_ips.split(',')]
    return ['127.0.0.1', 'localhost']

WHITELIST_IPS = _load_whitelist_ips()

# 已知爬虫 User-Agent（可选拦截）
# 环境变量格式: DHT_KNOWN_CRAWLERS = 'bot,crawler,spider,scraper'
KNOWN_CRAWLERS = [crawler.strip() for crawler in os.environ.get('DHT_KNOWN_CRAWLERS', 'bot,crawler,spider,scraper,curl,wget').split(',')]

# 是否拦截爬虫
BLOCK_CRAWLERS = get_env('BLOCK_CRAWLERS', False)
