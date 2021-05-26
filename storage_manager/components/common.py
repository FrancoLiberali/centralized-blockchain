import json
from multiprocessing import Lock, Manager

BLOCKCHAIN_FILES_PATH = "/storage_manager/blockchain_files"
MINUTES_INDEX_PATH = f"{BLOCKCHAIN_FILES_PATH}/minutes_index"

# TODO DUDA no es la solucion mas eficiente, lectores entre ellos pueden leer a la vez (problema de lector - escritor)
shared_memory_manager = Manager()
hash_prefix_locks_lock = Lock()
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

def read_block(logger, block_hash_hex):
    prefix = get_block_hash_prefix(block_hash_hex)
    block_with_prefix_path = get_blocks_by_prefix_path(prefix)

    try:
        with hash_prefix_locks_lock:
            lock = hash_prefix_locks[prefix]
        blocks_dict = read_from_json(lock, block_with_prefix_path)
        return blocks_dict[block_hash_hex]
    except (KeyError, FileNotFoundError) as e:
        logger.info(f"Block {block_hash_hex} not found")
        raise e

def get_day_string(minute):
    return minute.replace(hour=0, minute=0).strftime('%Y-%m-%d')
