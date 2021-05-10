import socket
from common import Block, \
    BLOCK_BUILDER_HOST, \
    BLOCK_BUILDER_PORT, \
    CHUNCK_SIZE_LEN_IN_BYTES,\
    BLOCK_BUILDER_OK_RESPONSE_CODE, \
    BLOCK_BUILDER_RESPONSE_SIZE_IN_BYTES

def main(queue):
    serversocket = socket.socket(
        family=socket.AF_INET, type=socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port
    serversocket.bind((BLOCK_BUILDER_HOST, BLOCK_BUILDER_PORT))
    # TODO socket.gethostname()
    # become a server socket
    # TODO que poner en este numero y que pasa si se llena
    serversocket.listen(5)
    while True:
        # TODO meter el client adress en algun lado para poder saber quien lo mando?
        (clientsocket, _) = serversocket.accept()
        # TODO falta acá reintentar podria no recibir todo junto
        chunk_size_bytes = clientsocket.recv(CHUNCK_SIZE_LEN_IN_BYTES)
        chunk_size = int.from_bytes(
            chunk_size_bytes, byteorder='big', signed=False)
        # TODO ver esto, limita que solo sean archivos de texto pero sino no lo puedo meter en el json
        chunk = clientsocket.recv(chunk_size).decode("utf-8")
        block = Block([chunk])
        queue.put(block) # TODO falta ver el tema de que esté llena
        response_ok = BLOCK_BUILDER_OK_RESPONSE_CODE.to_bytes(
            BLOCK_BUILDER_RESPONSE_SIZE_IN_BYTES, byteorder='big', signed=False)
        clientsocket.send(response_ok) # TODO falta reintentar esto si no se puede
