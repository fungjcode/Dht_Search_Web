import multiprocessing
import threading
import time
import signal
import sys
import logging
import queue
from dht_server import DHTServer
from metadata_client import MetadataFetcher

# style Configuration
DHT_SERVERS = 8  # Fewer but more powerful servers
MAX_NODE_QSIZE = 500  # Per server
METADATA_WORKERS = 400
METADATA_TIMEOUT = 6
MAX_QUEUE_SIZE = 10000 
BLACKLIST_DURATION_SEC = 180
PRINT_INTERVAL_SEC = 5

# Global counters
fetch_stats = {"att": 0, "conn": 0, "hs": 0, "ok": 0, "fail": 0}
stats_lock = threading.Lock()
ip_blacklist = {}  # {ip: (timestamp, fail_count)}
blacklist_lock = threading.Lock()

stop_event = threading.Event()

def is_valid_ip(ip):
    """Filter out private/invalid IPs"""
    if ip.startswith('127.') or ip.startswith('0.') or ip.startswith('192.168.'):
        return False
    if ip.startswith('10.') or ip.startswith('172.'):
        return False
    return True

def decode_name(bs):
    if not bs: return ""
    for enc in ['utf-8', 'gbk', 'big5']:
        try: return bs.decode(enc)
        except: continue
    return bs.decode('utf-8', 'replace')

def metadata_worker(meta_queue, db_queue, logger):
    global fetch_stats, ip_blacklist
    while not stop_event.is_set():
        try:
            try:
                task_data = meta_queue.get(timeout=1)
                if task_data is None: break
                _, task = task_data
            except queue.Empty: continue
            
            info_hash, ip, port = task
            
            if not is_valid_ip(ip):
                continue
            
            now = time.time()
            with blacklist_lock:
                if ip in ip_blacklist:
                    ban_time, fail_count = ip_blacklist[ip]
                    ban_duration = min(BLACKLIST_DURATION_SEC * fail_count, 1800)
                    if now - ban_time < ban_duration:
                        continue
                    else:
                        del ip_blacklist[ip]

            with stats_lock: fetch_stats["att"] += 1
            try:
                fetcher = MetadataFetcher(info_hash, (ip, port), timeout=METADATA_TIMEOUT)
                if fetcher.connect():
                    with stats_lock: fetch_stats["conn"] += 1
                    if fetcher.handshake():
                        with stats_lock: fetch_stats["hs"] += 1
                        metadata = fetcher.get_metadata()
                        if metadata:
                            with stats_lock: fetch_stats["ok"] += 1
                            # 提交到数据库队列
                            try:
                                info_hex = info_hash.hex()
                                name = decode_name(metadata.get(b'name', b'unknown'))
                                size = 0
                                if b'files' in metadata:
                                    size = sum(f.get(b'length', 0) for f in metadata[b'files'])
                                else:
                                    size = metadata.get(b'length', 0)
                                sz_str = f"{size/(1024**3):.2f}GB" if size > 1024**3 else f"{size/(1024**2):.2f}MB"
                                print(f" [+] Found: {name} ({sz_str}) | Hash: {info_hex}")
                                
                                # 提交到数据库写入队列
                                db_queue.put((metadata, info_hex, ip, b"metadata"))
                            except Exception as e:
                                logger.error(f"Queue submission error: {e}")
                        else:
                            with stats_lock: fetch_stats["fail"] += 1
                            with blacklist_lock:
                                if ip in ip_blacklist:
                                    _, fail_count = ip_blacklist[ip]
                                    ip_blacklist[ip] = (now, fail_count + 1)
                                else:
                                    ip_blacklist[ip] = (now, 1)
                    else:
                        with stats_lock: fetch_stats["fail"] += 1
                        with blacklist_lock:
                            if ip in ip_blacklist:
                                _, fail_count = ip_blacklist[ip]
                                ip_blacklist[ip] = (now, fail_count + 1)
                            else:
                                ip_blacklist[ip] = (now, 1)
                    fetcher.close()
                else:
                    with stats_lock: fetch_stats["fail"] += 1
                    with blacklist_lock:
                        if ip in ip_blacklist:
                            _, fail_count = ip_blacklist[ip]
                            ip_blacklist[ip] = (now, fail_count + 1)
                        else:
                            ip_blacklist[ip] = (now, 1)
            except Exception as e:
                logger.error(f"Metadata fetch error for {info_hash.hex() if info_hash else 'unknown'}: {e}")
                with stats_lock: fetch_stats["fail"] += 1
                with blacklist_lock:
                    if ip in ip_blacklist:
                        _, fail_count = ip_blacklist[ip]
                        ip_blacklist[ip] = (now, fail_count + 1)
                    else:
                        ip_blacklist[ip] = (now, 1)
            finally:
                meta_queue.task_done()
        except Exception as e:
            logger.debug(f"Worker loop error: {e}")

def main():
    logging.basicConfig(level=logging.ERROR, format='%(message)s')
    logger = logging.getLogger("Main")
    info_queue = multiprocessing.Queue(maxsize=MAX_QUEUE_SIZE)
    db_queue = multiprocessing.Queue(maxsize=5000)  # 数据库写入队列
    meta_queue = queue.PriorityQueue(maxsize=MAX_QUEUE_SIZE)
    
    # 启动数据库写入进程
    from workers.db_writer import DBWriter
    from config.settings import DB_WRITER_WORKERS, DB_BATCH_SIZE, DB_BATCH_TIMEOUT
    
    db_writers = []
    for _ in range(DB_WRITER_WORKERS):
        p = multiprocessing.Process(target=DBWriter.worker, args=(db_queue, DB_BATCH_SIZE, DB_BATCH_TIMEOUT))
        p.daemon = True
        p.start()
        db_writers.append(p)
    
    # 启动元数据工作线程
    for _ in range(METADATA_WORKERS):
        threading.Thread(target=metadata_worker, args=(meta_queue, db_queue, logger), daemon=True).start()
    
    # Start DHT servers with dedicated find_node threads
    dht_processes = []
    for i in range(DHT_SERVERS):
        p = multiprocessing.Process(target=run_dht_server, args=(info_queue, MAX_NODE_QSIZE))
        p.start()
        dht_processes.append(p)
    
    print(f"--- Crawler Started ({DHT_SERVERS} Servers, {METADATA_WORKERS} Workers) ---")
    
    def handle_signal(sig, frame):
        import os
        for p in dht_processes: p.terminate()
        os._exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    
    processed_tasks = set()
    last_print = 0.0

    while not stop_event.is_set():
        now = time.time()
        try: event = info_queue.get(timeout=0.5)
        except queue.Empty: event = None
        
        if event:
            try:
                ev_t, info_h, src, port = event
                if not info_h: continue
                
                # Smart port selection
                if ev_t == b"announce_peer":
                    prio = 1
                    target_port = port if port and port > 0 else 6881
                elif ev_t == b"peer_value":
                    prio = 2
                    target_port = port if port and port > 0 else src[1] if src[1] > 0 else 6881
                else:  # get_peers
                    prio = 3
                    target_port = src[1] if src[1] > 0 else 6881
                
                task_key = (info_h, src[0])
                if task_key not in processed_tasks:
                    processed_tasks.add(task_key)
                    meta_queue.put((prio, (info_h, src[0], target_port)), block=False)
                    if len(processed_tasks) > 50000: processed_tasks.clear()
            except Exception as e:
                logger.debug(f"Event processing error: {e}")

        if now - last_print >= PRINT_INTERVAL_SEC:
            with stats_lock: s = fetch_stats.copy()
            with blacklist_lock:
                to_del = []
                for ip, (ban_time, fail_count) in list(ip_blacklist.items()):
                    ban_duration = min(BLACKLIST_DURATION_SEC * fail_count, 1800)
                    if now - ban_time > ban_duration:
                        to_del.append(ip)
                for ip in to_del: del ip_blacklist[ip]
                bl_size = len(ip_blacklist)
            print(f"STAT: Q={meta_queue.qsize()} | BL={bl_size} | Att={s['att']} | Conn={s['conn']} | HS={s['hs']} | OK={s['ok']}", end='\r')
            last_print = now

def run_dht_server(info_queue, max_node_qsize):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    logging.getLogger("DHTServer").setLevel(logging.ERROR)
    
    server = DHTServer("0.0.0.0", 0, info_queue, max_node_qsize)
    server.daemon = True
    server.start()
    
    # Start the aggressive find_node thread (killer feature!)
    find_node_thread = threading.Thread(target=server.auto_send_find_node)
    find_node_thread.daemon = True
    find_node_thread.start()
    
    # Keep process alive
    while server.is_alive():
        time.sleep(1)

if __name__ == "__main__": main()
