from datetime import datetime
import json
import logging

from common.block_interface import recv_hash_and_block_json
from common.common import STORAGE_MANAGER_WRITE_PORT
from common.safe_tcp_socket import SafeTCPSocket
from components.common import get_day_string, \
    get_minutes_index_path, \
    shared_memory_manager, \
    hash_prefix_locks_lock, \
    hash_prefix_locks, \
    minutes_indexs_locks_lock, \
    minutes_indexs_locks, \
    get_block_hash_prefix, \
    get_blocks_by_prefix_path

logger = logging.getLogger(name="Storage manager - Block writer")


def get_or_create_lock(locks_dict_lock, locks_dict, locks_key):
    with locks_dict_lock:
        lock = locks_dict.get(locks_key, None)
        if not lock:
            lock = shared_memory_manager.Lock()
            locks_dict[locks_key] = lock
    return lock

def append_to_json(locks_dict_lock, locks_dict, locks_key, file_path, append_function):
    lock = get_or_create_lock(locks_dict_lock, locks_dict, locks_key)

    with lock:
        try:
            with open(file_path, "r") as json_file:
                json_dict = json.load(json_file)
        except FileNotFoundError:
            json_dict = {}

        append_function(json_dict)
        with open(file_path, "w") as json_file:
            json.dump(json_dict, json_file, indent=4)

def append_block_to_blocks_by_prefix(block_hash_hex, block_json):
    # function currying in python
    def append_func(blocks_dict):
        blocks_dict[block_hash_hex] = block_json
    return append_func


def append_block_hash_to_minutes_index(minute, block_hash_hex):
    minute_key = repr(minute.timestamp())
    # function currying in python

    def append_func(minutes_index):
        mined_that_minute = minutes_index.get(minute_key, [])
        mined_that_minute.append(block_hash_hex)
        minutes_index[minute_key] = mined_that_minute
    return append_func


def write_block(block_hash, block_json):
    block_hash_hex = hex(block_hash)
    logger.info(f"Received request to write block with hash {block_hash_hex}")

    prefix = get_block_hash_prefix(block_hash_hex)
    blocks_by_prefix_path = get_blocks_by_prefix_path(prefix)
    append_to_json(
        hash_prefix_locks_lock,
        hash_prefix_locks,
        prefix,
        blocks_by_prefix_path,
        append_block_to_blocks_by_prefix(
            block_hash_hex, block_json
        )
    )

    block_dict = json.loads(block_json)
    # TODO poner en variable global
    mined_in = datetime.fromtimestamp(block_dict['header']['timestamp'])
    minute = mined_in.replace(second=0, microsecond=0)
    day_string = get_day_string(minute)
    minutes_index_file_path = get_minutes_index_path(day_string)
    append_to_json(
        minutes_indexs_locks_lock,
        minutes_indexs_locks,
        day_string,
        minutes_index_file_path,
        append_block_hash_to_minutes_index(
            minute, block_hash_hex
        )
    )
    logger.info(f"Writed block with hash {block_hash_hex} in {prefix}.json")


def writer_server():
    # TODO DUDA al parar el container quiere excribir el block 0x0.json y vacio, no se porque. Hay que hacer un gracefully quit?
    serversocket = SafeTCPSocket.newServer(STORAGE_MANAGER_WRITE_PORT)
    block_appender_socket, _ = serversocket.accept()
    while True:
        block_hash, block = recv_hash_and_block_json(block_appender_socket)
        write_block(block_hash, block)
