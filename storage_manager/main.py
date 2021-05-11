import sys
sys.path.append(".")

from common.common import STORAGE_MANAGER_PORT, BLOCK_SIZE_LEN_IN_BYTES
from common.safe_tcp_socket import SafeTCPSocket

def main():
    serversocket = SafeTCPSocket.newServer(STORAGE_MANAGER_PORT)
    (clientsocket, _) = serversocket.accept()
    while True:
        block_len_bytes = clientsocket.recv(BLOCK_SIZE_LEN_IN_BYTES)
        # print(block_len_bytes)
        block_len = int.from_bytes(
            block_len_bytes, byteorder='big', signed=False)
        block = clientsocket.recv(block_len)
        print(block)
        # now do something with the clientsocket
        # in this case, we'll pretend this is a threaded server
        # ct = client_thread(clientsocket)
        # ct.run()

if __name__ == '__main__':
    main()
