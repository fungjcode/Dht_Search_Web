import socket
import struct
import time
import hashlib
import math
from bencode import bencode, bdecode
from utils import get_rand_id

BT_PROTOCOL = b"BitTorrent protocol"
BT_MSG_ID = 20
EXT_HANDSHAKE_ID = 0

class MetadataFetcher:
    def __init__(self, info_hash, address, timeout=10):
        self.info_hash = info_hash
        self.address = address
        self.timeout = timeout
        self.peer_id = get_rand_id()
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect(self.address)
            return True
        except:
            return False

    def handshake(self):
        try:
            # BT handshake
            bt_header = bytes([len(BT_PROTOCOL)]) + BT_PROTOCOL
            ext_bytes = b"\x00\x00\x00\x00\x00\x10\x00\x00"
            packet = bt_header + ext_bytes + self.info_hash + self.peer_id
            self.sock.sendall(packet)
            
            # Read response with timeout
            self.sock.settimeout(3)  # Quick handshake timeout
            response = self.sock.recv(68)
            if len(response) < 68:
                return False
            
            # Check protocol
            plen = response[0]
            if plen != len(BT_PROTOCOL):
                return False
            if response[1:1+plen] != BT_PROTOCOL:
                return False
            
            # Restore normal timeout
            self.sock.settimeout(self.timeout)
            return True
        except:
            return False

    def get_metadata(self):
        try:
            # Send extension handshake
            msg = bytes([BT_MSG_ID, EXT_HANDSHAKE_ID]) + bencode({b"m": {b"ut_metadata": 1}})
            self.send_message(msg)
            
            # Read extension handshake response with longer timeout
            packet = self.recv_all(timeout=self.timeout)
            if not packet:
                return None
            
            # Parse to find ut_metadata and metadata_size
            ut_metadata = self.get_ut_metadata(packet)
            metadata_size = self.get_metadata_size(packet)
            
            if not ut_metadata or not metadata_size:
                return None
            
            # Request each piece
            num_pieces = int(math.ceil(metadata_size / (16.0 * 1024)))
            metadata = []
            
            for piece in range(num_pieces):
                self.request_metadata(ut_metadata, piece)
                packet = self.recv_all(timeout=self.timeout)
                if packet:
                    # Extract piece data - try multiple methods
                    piece_data = None
                    
                    # Method 1: Look for "ee" marker (most common)
                    try:
                        idx = packet.index(b"ee")
                        piece_data = packet[idx+2:]
                    except:
                        pass
                    
                    # Method 2: Look for msg_type and extract after bencode
                    if not piece_data:
                        try:
                            # Find the bencode dict end and take everything after
                            msg_type_idx = packet.find(b"msg_type")
                            if msg_type_idx > 0:
                                # Scan for the end of bencode dict
                                for i in range(msg_type_idx, len(packet)):
                                    if packet[i:i+2] == b"ee":
                                        piece_data = packet[i+2:]
                                        break
                        except:
                            pass
                    
                    if piece_data:
                        metadata.append(piece_data)
            
            # Combine and verify
            if not metadata:
                return None
                
            full_metadata = b"".join(metadata)
            
            # Trim to exact size if we got extra data
            if len(full_metadata) > metadata_size:
                full_metadata = full_metadata[:metadata_size]
            
            # Verify hash
            if hashlib.sha1(full_metadata).digest() == self.info_hash:
                try:
                    return bdecode(full_metadata)
                except:
                    return None
            
            return None
        except:
            return None

    def send_message(self, msg):
        length = struct.pack(">I", len(msg))
        self.sock.sendall(length + msg)

    def request_metadata(self, ut_metadata, piece):
        msg = bytes([BT_MSG_ID, ut_metadata]) + bencode({b"msg_type": 0, b"piece": piece})
        self.send_message(msg)

    def recv_all(self, timeout=6):
        self.sock.setblocking(False)
        total_data = []
        begin = time.time()
        
        while True:
            time.sleep(0.01)  # Even faster polling
            elapsed = time.time() - begin
            
            # If we have data and haven't received more for timeout seconds, done
            if total_data and elapsed > timeout:
                break
            # If we have no data and it's been timeout*1.5, give up faster
            elif not total_data and elapsed > timeout * 1.5:
                break
            
            try:
                data = self.sock.recv(8192)  # Even larger buffer
                if data:
                    total_data.append(data)
                    begin = time.time()  # Reset timer on new data
            except:
                pass
        
        return b"".join(total_data)

    def get_ut_metadata(self, data):
        try:
            ut_metadata = b"_metadata"
            index = data.index(ut_metadata) + len(ut_metadata) + 1
            return int(data[index:index+1])
        except:
            return None

    def get_metadata_size(self, data):
        try:
            metadata_size = b"metadata_size"
            start = data.index(metadata_size) + len(metadata_size) + 1
            data = data[start:]
            end = data.index(b"e")
            return int(data[:end])
        except:
            return None

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
