"""
后台管理 CLI 工具
用于管理种子状态、处理 DMCA 投诉等

使用方法:
    python admin_cli.py block <info_hash> <reason>     # 屏蔽种子
    python admin_cli.py unblock <info_hash>             # 解除屏蔽
    python admin_cli.py search <keyword>                # 搜索种子
    python admin_cli.py complaints list                 # 查看投诉列表
    python admin_cli.py complaints approve <id>         # 批准投诉
    python admin_cli.py complaints reject <id>          # 拒绝投诉
    python admin_cli.py stats                           # 查看统计信息
"""
import sys
import os
import uuid
from datetime import datetime
import hashlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.mysql_client import MySQLClient

class AdminCLI:
    """后台管理命令行工具"""
    
    def __init__(self):
        MySQLClient.initialize()
    
    def block_torrent(self, info_hash, reason='dmca', note=''):
        """屏蔽种子"""
        try:
            # 检查种子是否存在
            torrent = MySQLClient.fetch_one(
                "SELECT id, name FROM torrents WHERE info_hash = %s",
                (info_hash,)
            )
            
            if not torrent:
                print(f"❌ 未找到种子: {info_hash}")
                return False
            
            # 更新屏蔽状态
            MySQLClient.execute(
                """
                UPDATE torrents 
                SET is_blocked = TRUE, block_reason = %s
                WHERE info_hash = %s
                """,
                (reason, info_hash)
            )
            
            print(f"✅ 种子已屏蔽: {torrent['name']}")
            print(f"   Hash: {info_hash}")
            print(f"   原因: {reason}")
            return True
            
        except Exception as e:
            print(f"❌ 屏蔽失败: {e}")
            return False
    
    def unblock_torrent(self, info_hash):
        """解除屏蔽"""
        try:
            result = MySQLClient.execute(
                """
                UPDATE torrents 
                SET is_blocked = FALSE, block_reason = NULL
                WHERE info_hash = %s
                """,
                (info_hash,)
            )
            
            if result > 0:
                print(f"✅ 已解除屏蔽: {info_hash}")
                return True
            else:
                print(f"❌ 未找到种子: {info_hash}")
                return False
                
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            return False
    
    def search_torrents(self, keyword, limit=20):
        """搜索种子"""
        try:
            # 验证并清理关键词
            import re
            # 只允许中文、英文、数字、空格、下划线
            clean_keyword = re.sub(r'[^\w\s\u4e00-\u9fa5]', '', keyword).strip()
            if not clean_keyword:
                print(f"❌ 无效的搜索关键词")
                return

            results = MySQLClient.fetch_all(
                """
                SELECT
                    info_hash,
                    name,
                    ROUND(total_size / 1024 / 1024 / 1024, 2) AS size_gb,
                    health_score,
                    is_blocked,
                    block_reason,
                    last_seen
                FROM torrents
                WHERE name LIKE %s
                ORDER BY health_score DESC
                LIMIT %s
                """,
                (f'%{clean_keyword}%', limit)
            )
            
            if not results:
                print(f"❌ 未找到包含 '{keyword}' 的种子")
                return
            
            print(f"\n🔍 搜索结果 (共 {len(results)} 条):\n")
            print(f"{'Hash':<42} {'名称':<40} {'大小':<10} {'健康度':<8} {'状态'}")
            print("=" * 120)
            
            for r in results:
                status = f"🚫 {r['block_reason']}" if r['is_blocked'] else "✅ 正常"
                print(f"{r['info_hash']:<42} {r['name'][:38]:<40} {r['size_gb']:<10.2f} {r['health_score']:<8.1f} {status}")
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
    
    def list_complaints(self, status='pending', limit=20):
        """查看投诉列表"""
        try:
            results = MySQLClient.fetch_all(
                """
                SELECT 
                    c.id,
                    c.info_hash,
                    t.name AS torrent_name,
                    c.complainant_name,
                    c.complainant_email,
                    c.complaint_reason,
                    c.status,
                    c.created_at
                FROM dmca_complaints c
                LEFT JOIN torrents t ON c.torrent_id = t.id
                WHERE c.status = %s
                ORDER BY c.created_at DESC
                LIMIT %s
                """,
                (status, limit)
            )
            
            if not results:
                print(f"❌ 没有 {status} 状态的投诉")
                return
            
            print(f"\n📋 投诉列表 ({status}) - 共 {len(results)} 条:\n")
            
            for i, r in enumerate(results, 1):
                print(f"{i}. ID: {r['id']}")
                print(f"   种子: {r['torrent_name'] or '未知'}")
                print(f"   Hash: {r['info_hash']}")
                print(f"   投诉人: {r['complainant_name']} ({r['complainant_email']})")
                print(f"   原因: {r['complaint_reason'][:100]}...")
                print(f"   时间: {r['created_at']}")
                print()
            
        except Exception as e:
            print(f"❌ 查询失败: {e}")
    
    def approve_complaint(self, complaint_id, admin_note=''):
        """批准投诉（自动屏蔽种子）"""
        try:
            # 获取投诉信息
            complaint = MySQLClient.fetch_one(
                "SELECT torrent_id, info_hash FROM dmca_complaints WHERE id = %s",
                (complaint_id,)
            )
            
            if not complaint:
                print(f"❌ 未找到投诉: {complaint_id}")
                return False
            
            # 屏蔽种子
            if complaint['info_hash']:
                self.block_torrent(complaint['info_hash'], 'dmca', admin_note)
            
            # 更新投诉状态
            MySQLClient.execute(
                """
                UPDATE dmca_complaints
                SET status = 'approved', processed_at = NOW(), admin_note = %s
                WHERE id = %s
                """,
                (admin_note, complaint_id)
            )
            
            print(f"✅ 投诉已批准: {complaint_id}")
            return True
            
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            return False
    
    def reject_complaint(self, complaint_id, admin_note=''):
        """拒绝投诉"""
        try:
            result = MySQLClient.execute(
                """
                UPDATE dmca_complaints
                SET status = 'rejected', processed_at = NOW(), admin_note = %s
                WHERE id = %s
                """,
                (admin_note, complaint_id)
            )
            
            if result > 0:
                print(f"✅ 投诉已拒绝: {complaint_id}")
                return True
            else:
                print(f"❌ 未找到投诉: {complaint_id}")
                return False
                
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            return False
    
    def show_stats(self):
        """显示统计信息"""
        try:
            # 种子统计
            stats = MySQLClient.fetch_one(
                """
                SELECT 
                    COUNT(*) AS total,
                    SUM(CASE WHEN is_blocked THEN 1 ELSE 0 END) AS blocked,
                    SUM(CASE WHEN health_score >= 50 THEN 1 ELSE 0 END) AS healthy,
                    ROUND(AVG(health_score), 2) AS avg_health
                FROM torrents
                """
            )
            
            # 投诉统计
            complaints = MySQLClient.fetch_one(
                """
                SELECT 
                    COUNT(*) AS total,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending,
                    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) AS approved,
                    SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) AS rejected
                FROM dmca_complaints
                """
            )
            
            print("\n📊 数据库统计信息\n")
            print("=" * 50)
            print(f"种子总数:     {stats['total']:,}")
            print(f"已屏蔽:       {stats['blocked']:,}")
            print(f"健康种子:     {stats['healthy']:,}")
            print(f"平均健康度:   {stats['avg_health']:.2f}")
            print()
            print(f"投诉总数:     {complaints['total']:,}")
            print(f"待处理:       {complaints['pending']:,}")
            print(f"已批准:       {complaints['approved']:,}")
            print(f"已拒绝:       {complaints['rejected']:,}")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ 查询失败: {e}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cli = AdminCLI()
    command = sys.argv[1].lower()
    
    if command == 'block':
        if len(sys.argv) < 4:
            print("用法: python admin_cli.py block <info_hash> <reason>")
            sys.exit(1)
        info_hash = sys.argv[2]
        reason = sys.argv[3]
        # 验证 reason 参数
        valid_reasons = {'dmca', 'copyright', 'illegal', 'spam', 'other'}
        if reason not in valid_reasons:
            print(f"❌ 无效的 reason 参数，可选值: {', '.join(valid_reasons)}")
            sys.exit(1)
        note = sys.argv[4] if len(sys.argv) > 4 else ''
        cli.block_torrent(info_hash, reason, note)
    
    elif command == 'unblock':
        if len(sys.argv) < 3:
            print("用法: python admin_cli.py unblock <info_hash>")
            sys.exit(1)
        info_hash = sys.argv[2]
        cli.unblock_torrent(info_hash)
    
    elif command == 'search':
        if len(sys.argv) < 3:
            print("用法: python admin_cli.py search <keyword>")
            sys.exit(1)
        keyword = sys.argv[2]
        cli.search_torrents(keyword)
    
    elif command == 'complaints':
        if len(sys.argv) < 3:
            print("用法: python admin_cli.py complaints <list|approve|reject>")
            sys.exit(1)
        
        sub_cmd = sys.argv[2].lower()
        if sub_cmd == 'list':
            status = sys.argv[3] if len(sys.argv) > 3 else 'pending'
            cli.list_complaints(status)
        elif sub_cmd == 'approve':
            if len(sys.argv) < 4:
                print("用法: python admin_cli.py complaints approve <complaint_id>")
                sys.exit(1)
            complaint_id = sys.argv[3]
            note = sys.argv[4] if len(sys.argv) > 4 else ''
            cli.approve_complaint(complaint_id, note)
        elif sub_cmd == 'reject':
            if len(sys.argv) < 4:
                print("用法: python admin_cli.py complaints reject <complaint_id>")
                sys.exit(1)
            complaint_id = sys.argv[3]
            note = sys.argv[4] if len(sys.argv) > 4 else ''
            cli.reject_complaint(complaint_id, note)
    
    elif command == 'stats':
        cli.show_stats()
    
    else:
        print(f"❌ 未知命令: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == '__main__':
    main()
