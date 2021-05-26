from multiprocessing import Lock, Process
from pathlib import Path

from blockchain_components.mined_counter.add_mining import add_mining_server
from blockchain_components.mined_counter.get_mined_per_miner_server import get_mined_per_miner_server
from blockchain_components.mined_counter.common import MINED_PER_MINER_PATH, \
    write_list_to_miner_file, \
    mined_per_miner_locks
from blockchain_components.common import MINERS_IDS

def initialize_mined_per_miner_files_and_locks():
    Path(MINED_PER_MINER_PATH).mkdir(parents=True, exist_ok=True)
    for miner_id in MINERS_IDS:
        mined_per_miner_locks[miner_id] = Lock()
        write_list_to_miner_file(miner_id, [0, 0])

def initialize(block_appender_queue):
    initialize_mined_per_miner_files_and_locks()
    get_mined_per_miner_server_p = Process(
        target=get_mined_per_miner_server
    )
    get_mined_per_miner_server_p.start()
    add_mining_server(block_appender_queue)
