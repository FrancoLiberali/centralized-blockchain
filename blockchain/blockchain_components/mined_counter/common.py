import json

MINED_PER_MINER_PATH = "/blockchain/blockchain_components/mined_counter/mined_per_miner_files"

# TODO no es la solucion mas eficiente, lectores deberian poder leer a la vez (problema de lector - escritor)
mined_per_miner_locks = {}

def get_mined_by_miner_path(miner_id):
    return f"{MINED_PER_MINER_PATH}/{miner_id}.json"

def write_list_to_miner_file(miner_id, list):
    with open(get_mined_by_miner_path(miner_id), "w+") as miner_file:
        json.dump(list, miner_file)

def read_list_from_miner_file(miner_id):
    with open(get_mined_by_miner_path(miner_id), "r") as miner_file:
        return json.load(miner_file)
