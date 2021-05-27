from common.block import DIFFICULTY_KEY, ENTRIES_AMOUNT_KEY, HEADER_KEY, NONCE_KEY, PREV_HASH_KEY, TIMESTAMP_KEY
import json

# 2**32 is bigger than 256*65356 (MAX_ENTRIES_AMOUNT*MAX_ENTRY_SIZE_IN_BYTES)
BLOCK_SIZE_LEN_IN_BYTES = 4
BLOCK_HASH_LEN_IN_BYTES = 32

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
    sock.send_string_with_len_prepended(block_json, BLOCK_SIZE_LEN_IN_BYTES)

def _block_to_json(block):
    return json.dumps({
        HEADER_KEY: {
            PREV_HASH_KEY: hex(block.header[PREV_HASH_KEY]),
            NONCE_KEY: block.header[NONCE_KEY],
            TIMESTAMP_KEY: block.header[TIMESTAMP_KEY].timestamp(),
            DIFFICULTY_KEY: block.header[DIFFICULTY_KEY],
            ENTRIES_AMOUNT_KEY: block.header[ENTRIES_AMOUNT_KEY],
        },
        "entries": block.entries
    }, indent=4, sort_keys=False)

def recv_hash(sock):
    return sock.recv_int(BLOCK_HASH_LEN_IN_BYTES)

def recv_hash_and_block_json(sock):
    block_hash = recv_hash(sock)

    block = sock.recv_string_with_len_prepended(BLOCK_SIZE_LEN_IN_BYTES)
    return (block_hash, block)
