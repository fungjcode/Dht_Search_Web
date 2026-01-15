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
# 启动所有服务
pm2 start ecosystem.config.js

# 保存进程列表以便重启
pm2 save

# 设置开机自启（需要 root/管理员权限）
pm2 startup
pm2 save
```

### 5. 服务脚本

项目提供了便捷的服务管理脚本：

**Windows：**
```bash
# 启动所有服务
start_services.bat

# 定时清理（任务计划程序）
scheduled_cleanup.bat
```

**Linux/macOS：**
```bash
# 启动所有服务
./start_services.sh

# 定时清理（cron）
crontab -e
# 添加：0 2 * * 0 /path/to/scheduled_cleanup.sh
```

**PM2 常用命令：**
```bash
pm2 status          # 查看所有进程
pm2 logs            # 查看所有日志
pm2 logs dht-crawler --lines 100  # 查看特定服务日志
pm2 restart all     # 重启所有服务
pm2 restart dht-api # 重启特定服务
pm2 stop all        # 停止所有服务
pm2 monit           # 实时监控面板
pm2 flush           # 清空所有日志
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

系统会自动清理 2 年前的旧数据，无需手动操作。

### 健康检查

```bash
pm2 monit  # 实时监控面板
pm2 status # 查看所有服务状态
```

### 后台管理 CLI 工具

项目提供了命令行管理工具，用于管理种子和处理 DMCA 投诉。

**使用方法：**

```bash
python admin_cli.py <命令> [参数]
```

**可用命令：**

| 命令 | 说明 | 示例 |
|------|------|------|
| `block <hash> <reason>` | 屏蔽种子 | `python admin_cli.py block abc123 dmca` |
| `unblock <hash>` | 解除屏蔽 | `python admin_cli.py unblock abc123` |
| `search <关键词>` | 搜索种子 | `python admin_cli.py search 电影` |
| `complaints list [状态]` | 查看投诉列表 | `python admin_cli.py complaints list pending` |
| `complaints approve <id>` | 批准投诉 | `python admin_cli.py complaints approve 1` |
| `complaints reject <id>` | 拒绝投诉 | `python admin_cli.py complaints reject 1` |
| `stats` | 显示数据库统计 | `python admin_cli.py stats` |

**屏蔽原因：**
- `dmca` - DMCA 版权投诉
- `copyright` - 版权侵权
- `illegal` - 非法内容
- `spam` - 垃圾信息
- `other` - 其他原因

**示例输出：**
```
$ python admin_cli.py stats

📊 数据库统计信息

==================================================
种子总数:     1,234,567
已屏蔽:       12,345
健康种子:     987,654
平均健康度:   75.32

投诉总数:     567
待处理:       89
已批准:       456
已拒绝:       22
==================================================
```

## 开源协议

MIT License