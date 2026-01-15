module.exports = {
    apps: [
        {
            name: "dht-crawler",
            script: "main.py",
            interpreter: "python",
            cwd: "./",
            instances: 1,
            autorestart: true,
            max_memory_restart: "800M",
            error_file: "logs/crawler-error.log",
            out_file: "NUL",
            log_date_format: "YYYY-MM-DD HH:mm:ss",
            merge_logs: true,
            env: {
                PYTHONPATH: ".",
                // 生产环境建议启用 API 密钥认证
                DHT_API_KEY_AUTH: "False",
                // 安全设置
                DHT_ENABLE_REFERER_CHECK: "False",
                DHT_BLOCK_CRAWLERS: "False"
            }
        },
        {
            name: "dht-api",
            script: "python",
            args: "-m uvicorn api.main:app --host 0.0.0.0 --port 8000",
            cwd: "./",
            instances: 1,
            autorestart: true,
            max_memory_restart: "1G",
            error_file: "logs/api-error.log",
            out_file: "logs/api-out.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss",
            merge_logs: true,
            env: {
                PYTHONPATH: ".",
                // 生产环境建议启用 API 密钥认证
                DHT_API_KEY_AUTH: "False",
                // 安全设置
                DHT_ENABLE_REFERER_CHECK: "False"
            }
        },
        {
            name: "dht-frontend",
            script: "npm",
            args: "run start -- -p 3000",
            cwd: "./frontend",
            instances: 1,
            autorestart: true,
            max_memory_restart: "1G",
            error_file: "../logs/frontend-error.log",
            out_file: "../logs/frontend-out.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss",
            merge_logs: true,
            env: {
                NODE_ENV: "production",
                PORT: 3000
            }
        }
    ]
}
