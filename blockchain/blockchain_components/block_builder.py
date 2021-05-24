import datetime
from common.common import Block, \
    BLOCK_BUILDER_PORT, \
    CHUNK_SIZE_LEN_IN_BYTES,\
    MAX_ENTRIES_AMOUNT, \
    TARGET_TIME_IN_SECONDS, \
    MAX_ENTRY_SIZE_IN_BYTES
from common.safe_tcp_socket import SafeTCPSocket
from common.responses import respond_bad_request, respond_ok, respond_service_unavaliable
from common.logger import Logger


def main(miners_coordinator_queue):
    logger = Logger("Block builder")
    serversocket = SafeTCPSocket.newServer(BLOCK_BUILDER_PORT)
    chunks = []
    start_time = None

    while True:
        # TODO DUDA meter el client adress en algun lado para poder saber quien lo mando? Podria pero no es obligatorio
        clientsocket, client_adress = serversocket.accept()
        if not miners_coordinator_queue.full():
            chunk_size = clientsocket.recv_int(CHUNK_SIZE_LEN_IN_BYTES)
            if chunk_size > MAX_ENTRY_SIZE_IN_BYTES:
                respond_bad_request(clientsocket) # TODO aclarar

            chunk = clientsocket.recv_string(chunk_size)
            logger.info(f"Received chuck from client {client_adress}: {chunk}")

            # the start_time if from the acceptation of the first chunk to no to take into account
            # the time that the miners_coordinator_queue is full
            if len(chunks) == 0:
                start_time = datetime.datetime.now()
            chunks.append(chunk)

            now = datetime.datetime.now()
            # TODO DUDA problema: es necesario que llegue un nuevo chunck para esto, quizas hay que chequearlo de otra forma. Si, que se mine solo cuando pasa el tiempo
            elapsed_time = (now - start_time).total_seconds()

            if len(chunks) == MAX_ENTRIES_AMOUNT or elapsed_time >= TARGET_TIME_IN_SECONDS:
                block = Block(chunks)
                logger.info(
                    f"Block appended to Miner's coordinator queue: {block}"
                )
                miners_coordinator_queue.put(block)
                chunks = []

            respond_ok(clientsocket)
        else:
            respond_service_unavaliable(clientsocket)
