import logging
from pathlib import Path
from multiprocessing import Process

from components.block_reader import reader_server
from components.block_writer import writer_server
from components.common import MINUTES_INDEX_PATH
from config.envvars import STORAGE_MANAGER_MINED_PER_MINUTE_PORT_KEY, STORAGE_MANAGER_MINED_PER_MINUTE_PROCESS_AMOUNT_KEY, STORAGE_MANAGER_READ_PORT_KEY, STORAGE_MANAGER_READ_PROCESS_AMOUNT_KEY, STORAGE_MANAGER_WRITE_PORT_KEY, get_config_params
from logger.logger import configure_log
from components.mined_per_minute import mined_per_minute_server

def main():
    configure_log()

    Path(MINUTES_INDEX_PATH).mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("Store manager main")
    config_params = get_config_params(
        [
            STORAGE_MANAGER_WRITE_PORT_KEY,
            STORAGE_MANAGER_READ_PORT_KEY,
            STORAGE_MANAGER_READ_PROCESS_AMOUNT_KEY,
            STORAGE_MANAGER_MINED_PER_MINUTE_PORT_KEY,
            STORAGE_MANAGER_MINED_PER_MINUTE_PROCESS_AMOUNT_KEY
        ],
        logger
    )

    writers_t = Process(
        target=writer_server,
        args=(config_params[STORAGE_MANAGER_WRITE_PORT_KEY],)
    )
    writers_t.start()

    mined_per_minute_t = Process(
        target=mined_per_minute_server,
        args=(
            config_params[STORAGE_MANAGER_MINED_PER_MINUTE_PORT_KEY],
            config_params[STORAGE_MANAGER_MINED_PER_MINUTE_PROCESS_AMOUNT_KEY]
        )
    )
    mined_per_minute_t.start()

    reader_server(
        config_params[STORAGE_MANAGER_READ_PORT_KEY],
        config_params[STORAGE_MANAGER_READ_PROCESS_AMOUNT_KEY]
    )

if __name__ == '__main__':
    main()
