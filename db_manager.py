"""
数据库管理工具
用于初始化、重置、备份和迁移数据库

使用方法:
    python db_manager.py init          # 初始化数据库
    python db_manager.py reset         # 重置数据库（删除所有数据）
    python db_manager.py drop          # 删除数据库
    python db_manager.py migrate       # 迁移数据库（更新表结构）
    python db_manager.py backup        # 备份数据库
    python db_manager.py test          # 测试数据库连接
"""
import sys
import os
import pymysql
import redis
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import (
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD,
    MYSQL_DATABASE, MYSQL_CHARSET,
    REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB
)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.mysql_config = {
            'host': MYSQL_HOST,
            'port': MYSQL_PORT,
            'user': MYSQL_USER,
            'password': MYSQL_PASSWORD,
            'charset': MYSQL_CHARSET
        }
    
    def get_connection(self, use_db=True):
        """获取 MySQL 连接"""
        config = self.mysql_config.copy()
        if use_db:
            config['database'] = MYSQL_DATABASE
        return pymysql.connect(**config)
    
    def test_mysql(self):
        """测试 MySQL 连接"""
        try:
            conn = self.get_connection(use_db=False)
            with conn.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
            conn.close()
            print(f"✅ MySQL 连接成功! 版本: {version}")
            return True
        except Exception as e:
            print(f"❌ MySQL 连接失败: {e}")
            return False
    
    def test_redis(self):
        """测试 Redis 连接"""
        try:
            client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=REDIS_DB
            )
            client.ping()
            info = client.info('server')
            print(f"✅ Redis 连接成功! 版本: {info['redis_version']}")
            return True
        except Exception as e:
            print(f"❌ Redis 连接失败: {e}")
            return False
    
    def create_database(self):
        """创建数据库"""
        try:
            conn = self.get_connection(use_db=False)
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"✅ 数据库 '{MYSQL_DATABASE}' 创建成功")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ 创建数据库失败: {e}")
            return False
    
    def drop_database(self):
        """删除数据库"""
        confirm = input(f"⚠️  确认删除数据库 '{MYSQL_DATABASE}'? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ 操作已取消")
            return False
        
        try:
            conn = self.get_connection(use_db=False)
            with conn.cursor() as cursor:
                cursor.execute(f"DROP DATABASE IF EXISTS {MYSQL_DATABASE}")
                print(f"✅ 数据库 '{MYSQL_DATABASE}' 已删除")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ 删除数据库失败: {e}")
            return False
    
    def execute_sql_file(self, filepath):
        """执行 SQL 文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # 分割 SQL 语句
            statements = []
            current = []
            for line in sql_content.split('\n'):
                line = line.strip()
                if not line or line.startswith('--'):
                    continue
                current.append(line)
                if line.endswith(';'):
                    statements.append(' '.join(current))
                    current = []
            
            conn = self.get_connection()
            with conn.cursor() as cursor:
                for stmt in statements:
                    if stmt.strip():
                        try:
                            cursor.execute(stmt)
                        except Exception as e:
                            print(f"⚠️  SQL 执行警告: {e}")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ 执行 SQL 文件失败: {e}")
            return False
    
    def init_database(self):
        """初始化数据库"""
        print("=" * 50)
        print("开始初始化数据库...")
        print("=" * 50)
        
        # 1. 创建数据库
        if not self.create_database():
            return False
        
        # 2. 执行建表脚本
        schema_file = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
        if not os.path.exists(schema_file):
            print(f"❌ 找不到建表脚本: {schema_file}")
            return False
        
        print(f"📄 执行建表脚本: {schema_file}")
        if not self.execute_sql_file(schema_file):
            return False
        
        print("✅ 数据库初始化完成!")
        print("\n📊 数据库表结构:")
        self.show_tables()
        return True
    
    def reset_database(self):
        """重置数据库（清空所有数据）"""
        confirm = input(f"⚠️  确认清空数据库 '{MYSQL_DATABASE}' 的所有数据? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ 操作已取消")
            return False
        
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                # 禁用外键检查
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                
                # 获取所有表
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                # 清空所有表
                for (table,) in tables:
                    cursor.execute(f"TRUNCATE TABLE {table}")
                    print(f"✅ 清空表: {table}")
                
                # 启用外键检查
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            conn.commit()
            conn.close()
            print("✅ 数据库重置完成!")
            return True
        except Exception as e:
            print(f"❌ 重置数据库失败: {e}")
            return False
    
    def show_tables(self):
        """显示所有表"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                for (table,) in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"  - {table}: {count} 条记录")
            conn.close()
        except Exception as e:
            print(f"❌ 查询表失败: {e}")
    
    def backup_database(self):
        """备份数据库"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"backup_{MYSQL_DATABASE}_{timestamp}.sql"
        
        try:
            import subprocess
            cmd = f"mysqldump -h{MYSQL_HOST} -P{MYSQL_PORT} -u{MYSQL_USER} -p{MYSQL_PASSWORD} {MYSQL_DATABASE} > {backup_file}"
            subprocess.run(cmd, shell=True, check=True)
            print(f"✅ 数据库备份成功: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ 备份失败: {e}")
            print("💡 提示: 请确保系统已安装 mysqldump 工具")
            return False
    
    def migrate_database(self):
        """迁移数据库（更新表结构）"""
        print("=" * 50)
        print("开始数据库迁移...")
        print("=" * 50)
        
        # 执行迁移脚本
        migrate_file = os.path.join(os.path.dirname(__file__), 'database', 'migrations.sql')
        
        if not os.path.exists(migrate_file):
            print(f"⚠️  未找到迁移脚本: {migrate_file}")
            print("💡 如果需要迁移，请创建 database/migrations.sql 文件")
            return False
        
        print(f"📄 执行迁移脚本: {migrate_file}")
        if not self.execute_sql_file(migrate_file):
            return False
        
        print("✅ 数据库迁移完成!")
        return True

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    manager = DatabaseManager()
    
    if command == 'test':
        print("🔍 测试数据库连接...\n")
        mysql_ok = manager.test_mysql()
        redis_ok = manager.test_redis()
        if mysql_ok and redis_ok:
            print("\n✅ 所有数据库连接正常!")
        else:
            print("\n❌ 部分数据库连接失败，请检查配置")
            sys.exit(1)
    
    elif command == 'init':
        manager.init_database()
    
    elif command == 'reset':
        manager.reset_database()
    
    elif command == 'drop':
        manager.drop_database()
    
    elif command == 'migrate':
        manager.migrate_database()
    
    elif command == 'backup':
        manager.backup_database()
    
    elif command == 'tables':
        print(f"\n📊 数据库 '{MYSQL_DATABASE}' 表结构:\n")
        manager.show_tables()
    
    else:
        print(f"❌ 未知命令: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == '__main__':
    main()
