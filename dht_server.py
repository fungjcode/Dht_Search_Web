import socket
import threading
import time
import logging
import os
import hashlib
import struct
from bencode import bdecode, bencode, BencodeError
from utils import get_rand_id, get_neighbor, decode_nodes, encode_nodes
from collections import deque

# Bootstrap nodes
BOOTSTRAP_NODES = [
    ("router.bittorrent.com", 6881),
    ("dht.transmissionbt.com", 6881),
    ("router.utorrent.com", 6881)
]

class KNode:
    def __init__(self, nid, ip, port):
        self.nid = nid
        self.ip = ip
        self.port = port

class DHTServer(threading.Thread):
    def __init__(self, bind_ip, bind_port, info_queue, max_node_qsize=500):
        super().__init__()
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        self.info_queue = info_queue
        self.max_node_qsize = max_node_qsize
        self.nid = get_rand_id()
        self.nodes = deque(maxlen=max_node_qsize)  #style node queue
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.bind_ip, self.bind_port))
        self.bind_port = self.sock.getsockname()[1]
        self.sock.settimeout(0.2)
        self.recent_hashes = deque(maxlen=2000)
        self.secret = os.urandom(20)
        self.last_secret = self.secret
        self.last_rotate = time.time()
        self.logger = logging.getLogger("DHTServer")
        self.logger.setLevel(logging.ERROR)

        self.recv_packets = 0
        self.decode_errors = 0
        self.rx_queries = 0
        self.rx_responses = 0
        self.tx_messages = 0
        self.tx_errors = 0
        self.bootstrap_sends = 0
        self.last_tx_error = None
        self.last_tx_error_at = 0.0
        self.tid_to_hash = {}
        self.tid_lock = threading.Lock()

    def cleanup_expired_tids(self):
        try:
            now = time.time()
            to_remove = []
            with self.tid_lock:
                for tid, (_, ts) in self.tid_to_hash.items():
                    if now - ts > 120:  # 2 minutes timeout
                        to_remove.append(tid)
                for tid in to_remove:
                    del self.tid_to_hash[tid]
        except Exception:
            pass

    def bootstrap(self):
        for host, port in BOOTSTRAP_NODES:
            try:
                infos = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_DGRAM)
                addrs = list({(ai[4][0], ai[4][1]) for ai in infos})
            except Exception:
                addrs = [(host, port)]
            for address in addrs:
                self.send_find_node(address, get_rand_id())
                self.bootstrap_sends += 1

    def send_find_node(self, address, target=None):
        if not target:
            target = get_rand_id()
        nid = get_neighbor(target, self.nid) if target else self.nid
        tid = os.urandom(2)
        msg = {
            b"t": tid,
            b"y": b"q",
            b"q": b"find_node",
            b"a": {
                b"id": nid,
                b"target": target
            }
        }
        self.send_message(msg, address)

    def send_message(self, msg, address):
        try:
            if address[1] == 0:
                return
            self.sock.sendto(bencode(msg), address)
            self.tx_messages += 1
        except Exception as e:
            self.tx_errors += 1

    def ping(self, address):
        nid = self.nid
        tid = os.urandom(2)
        msg = {
            b"t": tid,
            b"y": b"q",
            b"q": b"ping",
            b"a": {b"id": nid}
        }
        self.send_message(msg, address)

    def get_peers(self, address, info_hash):
        nid = get_neighbor(info_hash, self.nid)
        tid = os.urandom(2)
        with self.tid_lock:
            self.tid_to_hash[tid] = (info_hash, time.time())
        msg = {
            b"t": tid,
            b"y": b"q",
            b"q": b"get_peers",
            b"a": {
                b"id": nid,
                b"info_hash": info_hash
            }
        }
        self.send_message(msg, address)

    def token_for(self, address):
        ip = address[0].encode()
        return hashlib.sha1(self.secret + ip).digest()[:2]

    def check_token(self, address, token):
        ip = address[0].encode()
        if not token or len(token) != 2:
            return False
        if token == hashlib.sha1(self.secret + ip).digest()[:2]:
            return True
        if token == hashlib.sha1(self.last_secret + ip).digest()[:2]:
            return True
        return False

    def run(self):
        #self.logger.info(f"DHT Server started on {self.bind_ip}:{self.bind_port}")
        self.bootstrap()
        last_bootstrap = time.time()
        
        while self.running:
            # Cleanup expired transactions every 60 seconds
            if time.time() - self.last_rotate > 60:
                self.cleanup_expired_tids()
            
            if time.time() - self.last_rotate > 300:
                self.last_secret = self.secret
                self.secret = os.urandom(20)
                self.last_rotate = time.time()
            if time.time() - last_bootstrap > 2:
                self.bootstrap()
                last_bootstrap = time.time()

            try:
                data, address = self.sock.recvfrom(65536)
                self.recv_packets += 1
                msg = bdecode(data)
                self.handle_message(msg, address)
            except socket.timeout:
                continue
            except BencodeError:
                self.decode_errors += 1
                continue
            except Exception:
                pass

    def handle_message(self, msg, address):
        try:
            msg_type = msg.get(b"y")
            if msg_type == b"q":
                self.rx_queries += 1
                self.handle_query(msg, address)
            elif msg_type == b"r":
                self.rx_responses += 1
                self.handle_response(msg, address)
        except KeyError:
            pass

    def handle_query(self, msg, address):
        try:
            query_type = msg.get(b"q")
            tid = msg.get(b"t")
            args = msg.get(b"a")
            
            if query_type == b"get_peers":
                info_hash = args.get(b"info_hash")
                if info_hash and info_hash not in self.recent_hashes:
                    self.recent_hashes.append(info_hash)
                    try:
                        self.info_queue.put_nowait((b"get_peers", info_hash, address, None))
                    except Exception:
                        pass
                nid = get_neighbor(info_hash, self.nid) if info_hash else self.nid
                tok = self.token_for(address)
                # Return empty nodes list
                self.send_response(tid, address, {b"id": nid, b"token": tok, b"nodes": b""})

            elif query_type == b"announce_peer":
                info_hash = args.get(b"info_hash")
                port = args.get(b"port")
                token = args.get(b"token")
                if args.get(b"implied_port", 0) != 0:
                    port = address[1]
                
                try:
                    port = int(port)
                except (TypeError, ValueError):
                    port = None

                if info_hash and token and self.check_token(address, token):
                    if info_hash not in self.recent_hashes:
                        self.recent_hashes.append(info_hash)
                        try:
                            self.info_queue.put_nowait((b"announce_peer", info_hash, address, port))
                        except Exception:
                            pass
                sender_id = args.get(b"id", self.nid)
                self.send_response(tid, address, {b"id": get_neighbor(sender_id, self.nid)})

            elif query_type == b"find_node":
                target = args.get(b"target")
                nid = get_neighbor(target, self.nid) if target else self.nid
                self.send_response(tid, address, {b"id": nid, b"nodes": b""})

            elif query_type == b"ping":
                self.send_response(tid, address, {b"id": self.nid})

            # Add responding node to queue
            sender_nid = args.get(b"id")
            if sender_nid and len(sender_nid) == 20:
                self.add_node(sender_nid, address)
            
        except Exception:
            pass

    def add_node(self, nid, address):
        ip, port = address
        if not ip or port == 0:
            return
        if ip == self.bind_ip:
            return
        # Add to deque (auto-removes oldest if full)
        self.nodes.append(KNode(nid, ip, port))

    def handle_response(self, msg, address):
        try:
            args = msg.get(b"r")
            if not args:
                return
            
            # Add responding node
            if b"id" in args and len(args[b"id"]) == 20:
                self.add_node(args[b"id"], address)
            
            # Handle peer values
            if b"values" in args:
                tid = msg.get(b"t")
                info_hash = None
                if tid:
                    with self.tid_lock:
                        entry = self.tid_to_hash.get(tid)
                        if entry:
                            info_hash = entry[0]
                
                for v in args[b"values"]:
                    try:
                        if len(v) == 6:
                            ip = socket.inet_ntoa(v[:4])
                            port = struct.unpack("!H", v[4:])[0]
                            self.info_queue.put_nowait((b"peer_value", info_hash, (ip, port), port))
                    except:
                        continue

            # Handle nodes list
            if b"nodes" in args:
                new_nodes = decode_nodes(args[b"nodes"])
                for nid, ip, port in new_nodes:
                    if len(nid) == 20:
                        self.add_node(nid, (ip, port))
        except:
            pass

    def send_response(self, tid, address, args):
        msg = {
            b"t": tid,
            b"y": b"r",
            b"r": args
        }
        self.send_message(msg, address)
    
    def auto_send_find_node(self):
        """ killer feature: dedicated find_node spam thread"""
        wait = 1.0 / self.max_node_qsize  # e.g., 1/500 = 0.002s = 500 Hz!
        while self.running:
            try:
                if len(self.nodes) > 0:
                    node = self.nodes.popleft()
                    self.send_find_node((node.ip, node.port), node.nid)
            except:
                pass
            try:
                time.sleep(wait)
            except KeyboardInterrupt:
                break
    
    def stop(self):
        self.running = False
        self.sock.close()
