import os
import hashlib
import random
import struct
import socket

def get_rand_id():
    return os.urandom(20)

def get_neighbor(target, nid, end=10):
    """Generate a neighbor ID close to target"""
    return target[:end] + nid[end:]

def entropy(length):
    return "".join(chr(random.randint(0, 255)) for _ in range(length))

def random_id():
    h = hashlib.sha1()
    h.update(entropy(20).encode('utf-8'))
    return h.digest()

def decode_nodes(nodes):
    n = []
    length = len(nodes)
    if (length % 26) != 0:
        return n
    for i in range(0, length, 26):
        nid = nodes[i:i+20]
        ip = socket.inet_ntoa(nodes[i+20:i+24])
        port = struct.unpack("!H", nodes[i+24:i+26])[0]
        n.append((nid, ip, port))
    return n

def encode_nodes(nodes):
    strings = []
    for node in nodes:
        nid, ip, port = node
        try:
            ip_bytes = socket.inet_aton(ip)
            port_bytes = struct.pack("!H", port)
            strings.append(nid + ip_bytes + port_bytes)
        except:
            continue
    return b"".join(strings)

def dottedQuadToNum(ip):
    "convert decimal dotted quad string to long integer"
    return struct.unpack('!L', socket.inet_aton(ip))[0]

def numToDottedQuad(n):
    "convert long int to dotted quad string"
    return socket.inet_ntoa(struct.pack('!L', n))
