from common.common import Block, \
    BLOCK_BUILDER_PORT, \
    CHUNK_SIZE_LEN_IN_BYTES,\
    BLOCK_BUILDER_OK_RESPONSE_CODE, \
    BLOCK_BUILDER_RESPONSE_SIZE_IN_BYTES
from common.safe_tcp_socket import SafeTCPSocket

def main(queue):
    serversocket = SafeTCPSocket.newServer(BLOCK_BUILDER_PORT)
    while True:
        # TODO meter el client adress en algun lado para poder saber quien lo mando?
        (clientsocket, _) = serversocket.accept()

        chunk_size_bytes = clientsocket.recv(CHUNK_SIZE_LEN_IN_BYTES)
        chunk_size = int.from_bytes(
            chunk_size_bytes, byteorder='big', signed=False)
        # TODO ver esto, limita que solo sean archivos de texto pero sino no lo puedo meter en el json
        chunk = clientsocket.recv(chunk_size).decode("utf-8")

        block = Block([chunk])
        queue.put(block) # TODO falta ver el tema de que esté llena

        response_ok = BLOCK_BUILDER_OK_RESPONSE_CODE.to_bytes(
            BLOCK_BUILDER_RESPONSE_SIZE_IN_BYTES, byteorder='big', signed=False)
        clientsocket.send(response_ok)
