import struct

# Exceptions
class BencodeError(Exception):
    pass

def decode_int(x, f):
    f += 1
    newf = x.index(b'e', f)
    n = int(x[f:newf])
    if x[f] == b'-'[0]:
        if x[f + 1] == b'0'[0]:
            raise BencodeError
    elif x[f] == b'0'[0] and newf != f + 1:
        raise BencodeError
    return n, newf + 1

def decode_string(x, f):
    colon = x.index(b':', f)
    n = int(x[f:colon])
    if x[f] == b'0'[0] and colon != f + 1:
        raise BencodeError
    colon += 1
    return x[colon:colon + n], colon + n

def decode_list(x, f):
    r, f = [], f + 1
    while x[f] != b'e'[0]:
        v, f = decode_func[x[f]](x, f)
        r.append(v)
    return r, f + 1

def decode_dict(x, f):
    r, f = {}, f + 1
    while x[f] != b'e'[0]:
        k, f = decode_string(x, f)
        r[k], f = decode_func[x[f]](x, f)
    return r, f + 1

decode_func = {}
decode_func[b'l'[0]] = decode_list
decode_func[b'd'[0]] = decode_dict
decode_func[b'i'[0]] = decode_int
for i in range(b'0'[0], b'9'[0] + 1):
    decode_func[i] = decode_string

def bdecode(x):
    try:
        r, l = decode_func[x[0]](x, 0)
    except (IndexError, KeyError, ValueError):
        raise BencodeError("not a valid bencoded string")
    if l != len(x):
        raise BencodeError("invalid bencoded value (data after valid prefix)")
    return r

def bdecode_safe(x):
    """Returns (decoded_object, length_consumed)"""
    try:
        r, l = decode_func[x[0]](x, 0)
        return r, l
    except (IndexError, KeyError, ValueError):
        raise BencodeError("not a valid bencoded string")

def bencode(x):
    if isinstance(x, int):
        return b'i' + str(x).encode() + b'e'
    elif isinstance(x, str):
        x = x.encode('utf-8')
        return str(len(x)).encode() + b':' + x
    elif isinstance(x, bytes):
        return str(len(x)).encode() + b':' + x
    elif isinstance(x, list) or isinstance(x, tuple):
        r = b'l'
        for i in x:
            r += bencode(i)
        return r + b'e'
    elif isinstance(x, dict):
        r = b'd'
        # Convert all keys to bytes and sort by bytes (Bencode spec)
        items = []
        for k, v in x.items():
            if isinstance(k, str):
                kb = k.encode('utf-8')
            else:
                kb = k
            items.append((kb, v))
        
        items.sort(key=lambda item: item[0])
        
        for kb, v in items:
            r += str(len(kb)).encode() + b':' + kb + bencode(v)
        return r + b'e'
    else:
        raise BencodeError(f"Cannot bencode type: {type(x)}")
