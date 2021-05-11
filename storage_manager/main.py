from pathlib import Path
from threading import Thread
import sys
sys.path.append("..")


from common.common import STORAGE_MANAGER_PORT, \
    BLOCK_SIZE_LEN_IN_BYTES, \
    BLOCK_HASH_LEN_IN_BYTES
from common.safe_tcp_socket import SafeTCPSocket

def write_block(block_hash, block):
    block_file = open(f"./blockchain_files/{hex(block_hash)}.json", "x")
    block_file.write(block)
    block_file.close()

def main():
    Path("./blockchain_files").mkdir(parents=True, exist_ok=True)
    # TODO al parar el container quiere excribir el block 0x0.json y vacio, no se porque
    serversocket = SafeTCPSocket.newServer(STORAGE_MANAGER_PORT)
    (clientsocket, _) = serversocket.accept()
    while True:
        block_hash_bytes = clientsocket.recv(BLOCK_HASH_LEN_IN_BYTES)
        block_hash = int.from_bytes(
            block_hash_bytes, byteorder='big', signed=False)
        print(block_hash)

        block_len_bytes = clientsocket.recv(BLOCK_SIZE_LEN_IN_BYTES)
        block_len = int.from_bytes(
            block_len_bytes, byteorder='big', signed=False)
        block = clientsocket.recv(block_len).decode('utf-8')

        print(block)
        # i have choosen to use threads because it is allmost all i/o,
        # so paralelism between instructions is not needed,
        # and multithreading if ligther than multiprocessing
        writer_t = Thread(target=write_block, args=((block_hash), (block),))
        writer_t.start()

if __name__ == '__main__':
    main()
