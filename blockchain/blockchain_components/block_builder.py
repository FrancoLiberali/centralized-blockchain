import datetime
from common.common import Block, \
    BLOCK_BUILDER_PORT, \
    CHUNK_SIZE_LEN_IN_BYTES,\
    MAX_ENTRIES_AMOUNT, \
    TARGET_TIME_IN_SECONDS, \
    MAX_ENTRY_SIZE_IN_BYTES
from common.safe_tcp_socket import SafeTCPSocket
from common.responses import respond_bad_request, respond_ok, respond_service_unavaliable

def main(miners_coordinator_queue):
    serversocket = SafeTCPSocket.newServer(BLOCK_BUILDER_PORT)
    chunks = []
    start_time = None

    while True:
        # TODO meter el client adress en algun lado para poder saber quien lo mando?
        clientsocket = serversocket.accept()
        if not miners_coordinator_queue.full():
            chunk_size_bytes = clientsocket.recv(CHUNK_SIZE_LEN_IN_BYTES)
            chunk_size = int.from_bytes(chunk_size_bytes, byteorder='big', signed=False)
            if chunk_size > MAX_ENTRY_SIZE_IN_BYTES:
                respond_bad_request(clientsocket)

            # TODO ver esto, limita que solo sean archivos de texto pero sino no lo puedo meter en el json
            chunk = clientsocket.recv(chunk_size).decode("utf-8")

            # the start_time if from the acceptation of the first chunk to no to take into account
            # the time that the miners_coordinator_queue is full
            if len(chunks) == 0:
                start_time = datetime.datetime.now()
            chunks.append(chunk)

            now = datetime.datetime.now()
            elapsed_time = (now - start_time).total_seconds()

            if len(chunks) == MAX_ENTRIES_AMOUNT or elapsed_time >= TARGET_TIME_IN_SECONDS:
                block = Block(chunks)
                miners_coordinator_queue.put(block)
                chunks = []

            respond_ok(clientsocket)
        else:
            respond_service_unavaliable(clientsocket)
