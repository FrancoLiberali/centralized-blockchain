import socket
from common import STORAGE_MANAGER_HOST, STORAGE_MANAGER_PORT, BLOCK_SIZE_LEN_IN_BYTES

def main():
    serversocket = socket.socket(
        family=socket.AF_INET, type=socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port
    serversocket.bind((STORAGE_MANAGER_HOST, STORAGE_MANAGER_PORT))
    # TODO socket.gethostname()
    # become a server socket
    serversocket.listen(5) # TODO que poner en este numero y que pasa si se llena
    (clientsocket, _) = serversocket.accept()
    while True:
        block_len_bytes = clientsocket.recv(BLOCK_SIZE_LEN_IN_BYTES) # TODO falta acá reintentar podria no recibir todo junto
        # print(block_len_bytes)
        block_len = int.from_bytes(
            block_len_bytes, byteorder='big', signed=False)
        block = clientsocket.recv(block_len)
        print(block)
        # now do something with the clientsocket
        # in this case, we'll pretend this is a threaded server
        # ct = client_thread(clientsocket)
        # ct.run()
