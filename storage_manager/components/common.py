import json
from multiprocessing import Lock, Manager

BLOCKCHAIN_FILES_PATH = "/storage_manager/blockchain_files"
MINUTES_INDEX_PATH = f"{BLOCKCHAIN_FILES_PATH}/minutes_index"

shared_memory_manager = Manager()
hash_prefix_locks_lock = Lock()
# TODO no es la solucion mas eficiente, lectores deberian poder leer a la vez (problema de lector - escritor)
hash_prefix_locks = shared_memory_manager.dict()
minutes_indexs_locks_lock = Lock()
minutes_indexs_locks = shared_memory_manager.dict()

def get_blocks_by_prefix_path(prefix):
    return f"{BLOCKCHAIN_FILES_PATH}/{prefix}.json"


def get_minutes_index_path(day):
    return f"{MINUTES_INDEX_PATH}/{day}.json"


def get_block_hash_prefix(block_hash_hex):
    return block_hash_hex[2:7]


def read_from_json(lock, json_file_path):
    with lock:
        with open(json_file_path, "r") as json_file:
            return json.load(json_file)

def read_blocks(logger, prefix, hash_list):
    block_with_prefix_path = get_blocks_by_prefix_path(prefix)

    try:
        with hash_prefix_locks_lock:
            lock = hash_prefix_locks[prefix]
        blocks_dict = read_from_json(lock, block_with_prefix_path)
        return [(block_hash_hex, blocks_dict[block_hash_hex]) for block_hash_hex in hash_list]
    except (KeyError, FileNotFoundError) as e:
        logger.info(f"Block not found: {e}")
        raise e

def read_block(logger, block_hash_hex):
    prefix = get_block_hash_prefix(block_hash_hex)
    return read_blocks(logger, prefix, [block_hash_hex])[0][1]

def get_day_string(minute):
    return minute.replace(hour=0, minute=0).strftime('%Y-%m-%d')
