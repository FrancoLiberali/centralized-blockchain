from pathlib import Path
from threading import Thread

from common.logger import initialize_log
from components.block_reader import reader_server
from components.block_writer import writer_server
from components.common import MINUTES_INDEX_PATH
from components.mined_per_minute import mined_per_minute_server

def main():
    initialize_log()

    Path(MINUTES_INDEX_PATH).mkdir(parents=True, exist_ok=True)

    writers_t = Thread(target=writer_server) # TODO pasar a proccess
    writers_t.start()

    mined_per_minute_t = Thread(target=mined_per_minute_server)
    mined_per_minute_t.start()

    reader_server()

if __name__ == '__main__':
    main()
