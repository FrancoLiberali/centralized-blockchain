import json

# TODO verificar que en esto pueden entrar las max entries
BLOCK_SIZE_LEN_IN_BYTES = 4
BLOCK_HASH_LEN_IN_BYTES = 32

# TODO me gustaria que te abstraiga del socket tambien
def send_hash(sock, block_hash):
    sock.send_int(block_hash, BLOCK_HASH_LEN_IN_BYTES)

def send_block_with_hash(sock, block):
    send_hash_and_block_json(
        sock,
        block.hash(),
        _block_to_json(block)
    )

def send_hash_and_block_json(sock, block_hash, block_json):
    send_hash(sock, block_hash)
    sock.send_int(len(block_json), BLOCK_SIZE_LEN_IN_BYTES)
    sock.send(block_json.encode('utf-8'))

def _block_to_json(block):
    return json.dumps({
        "header": {
            'prev_hash': hex(block.header['prev_hash']),
            'nonce': block.header['nonce'],
            'timestamp': block.header['timestamp'].timestamp(),
            'difficulty': block.header['difficulty'],
            'entries_amount': block.header['entries_amount'],
        },
        "entries": block.entries
    }, indent=4, sort_keys=False)

def recv_hash(sock):
    return sock.recv_int(BLOCK_HASH_LEN_IN_BYTES)

def recv_hash_and_block_json(sock):
    block_hash = recv_hash(sock)

    block_len = sock.recv_int(BLOCK_SIZE_LEN_IN_BYTES)
    block = sock.recv(block_len).decode('utf-8')
    return (block_hash, block)
