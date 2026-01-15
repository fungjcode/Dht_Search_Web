# DHT Search - 开源种子搜索引擎

[English](README.md) | 简体中文

基于 DHT 网络的完整分布式种子搜索引擎系统，包含 DHT 爬虫、RESTful API 和现代化 Web 界面。

![DHT Search](screenshot/index.png)

## 功能特性

- **DHT 爬虫** - 多进程架构，支持高并发磁力链接采集
- **REST API** - 基于 FastAPI 的搜索、种子详情、DMCA 投诉接口
- **Web 界面** - 现代 Next.js 界面，支持中英文双语
- **全文搜索** - 利用 MySQL 8 Ngram 解析器实现中英文搜索，无需第三方分词库
- **高性能** - Redis 缓存 + MySQL 8 优化，应对大规模数据搜索和写入
- **智能排序** - 按时间、健康度、热度、大小、相关度排序
- **自动清理** - 自动清理 2 年前的旧数据，确保数据库质量
- **DMCA 合规** - 完整的版权投诉处理系统
- **进程守护** - 基于 PM2 的 7x24 小时稳定运行

## 技术栈

### 后端

| 技术 | 用途 |
|------|------|
| Python 3.10+ | 开发语言 |
| FastAPI | Web 框架 |
| aiohttp | 异步 HTTP 客户端 |
| MySQL 8.0 | 主数据库 |
| Redis 6.0+ | 缓存和速率限制 |

### 前端

| 技术 | 用途 |
|------|------|
| Next.js 14 | React 框架 |
| React 18 | UI 库 |
| TypeScript 5 | 类型安全 |
| Tailwind CSS 3 | 样式框架 |
| i18next | 国际化 |

## 截图展示

查看 [`screenshot/`](screenshot/) 目录获取更多截图：

- `index.png` - 首页搜索入口和热门标签
- `search.png` - 搜索结果页多维度排序和筛选
- `info.png` - 种子详情页文件列表和相关信息

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis 6.0+

### 1. 数据库初始化

```bash
mysql -u root -p -e "CREATE DATABASE dht_crawler CHARACTER SET utf8mb4;"
mysql -u root -p dht_crawler < database/schema.sql
mysql -u root -p dht_crawler < database/admin_schema.sql
```

配置 MySQL 全文搜索（`my.cnf` 或 `my.ini`）：

```ini
[mysqld]
ngram_token_size=2
```

### 2. 后端安装

```bash
pip install -r requirements_db.txt
pip install -r requirements_api.txt
```

### 3. 前端安装

```bash
cd frontend
npm install
```

### 4. 启动服务

**开发模式：**

```bash
# 终端 1 - DHT 爬虫
python main.py

# 终端 2 - API 服务
cd api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 终端 3 - 前端
npm run dev
```

**生产模式（PM2）：**

```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## 项目结构

```
dht_dk/
├── api/                # FastAPI 后端
├── config/             # 系统配置
├── database/           # 数据库脚本和客户端
├── screenshot/         # 项目截图
├── frontend/           # Next.js 前端
├── services/           # 核心业务逻辑
├── workers/            # 后台任务
├── main.py             # DHT 爬虫入口
├── ecosystem.config.js # PM2 配置
└── README.md           # 英文说明
```

## 配置说明

### 环境变量

复制 `.env.example` 为 `.env` 并修改：

```bash
cp .env.example .env
```

主要配置项：

```bash
# 数据库
DHT_MYSQL_HOST=localhost
DHT_MYSQL_PASSWORD=your_password

# Redis
DHT_REDIS_HOST=localhost

# API 安全
DHT_API_KEY_AUTH=False
```

### 前端配置

修改 `frontend/config/site.ts`：

```typescript
export const siteConfig = {
    name: 'DHT Search',
    url: 'https://your-domain.com',
    contact: {
        email: 'admin@your-domain.com',
        github: 'https://github.com/yourusername/dht-search',
    },
}
```

## 安全特性

- **禁搜词过滤** - 自动过滤违法和违规内容
- **DMCA 投诉处理** - 完整的版权投诉流程
- **API 速率限制** - 基于 Redis 的访问控制
- **Referer 防盗链** - 可配置的白名单机制

## 维护与监控

### 日志位置

```
logs/
├── crawler-error.log
├── crawler-out.log
├── api-error.log
├── api-out.log
├── frontend-error.log
└── frontend-out.log
```

### 数据清理

自动清理 2 年前的旧数据：

```bash
python cleanup_old_data.py --dry-run  # 模拟运行
python cleanup_old_data.py            # 实际清理
```

### 健康检查

```bash
python health_check.py                # 单次检查
python health_check.py --loop         # 循环监控
```

## 开源协议

MIT License