import argparse

from common.common import BLOCK_BUILDER_HOST, \
    BLOCK_BUILDER_PORT, \
    MAX_ENTRY_SIZE_IN_BYTES, \
    CHUNK_SIZE_LEN_IN_BYTES
from common.responses import RESPONSE_SIZE_IN_BYTES, \
    OK_RESPONSE_CODE, \
    SERVICE_UNAVAILABLE_RESPONSE_CODE
from common.safe_tcp_socket import SafeTCPSocket

def main():
    parser = argparse.ArgumentParser(description='Centralized Blockchain client for adding a chuck.')
    parser.add_argument('input_file_path', metavar='<input_file>', type=argparse.FileType('rb'), help='path to the file to read a chunck')

    args = parser.parse_args()

    input = args.input_file_path
    chunk = input.read(MAX_ENTRY_SIZE_IN_BYTES)
    input.close()

    sock = SafeTCPSocket.newClient(BLOCK_BUILDER_HOST, BLOCK_BUILDER_PORT)

    sock.send_int(len(chunk), CHUNK_SIZE_LEN_IN_BYTES)
    sock.send(chunk)

    response_code = sock.recv_int(RESPONSE_SIZE_IN_BYTES)
    if response_code == OK_RESPONSE_CODE:
        print("OK! Your chunck will be mined and added to the blockchain")
    elif response_code == SERVICE_UNAVAILABLE_RESPONSE_CODE:
        print("Oops! Too many data is being mined at this moment, please retry later")
    else:
        print("Oops! Unknown error")
    sock.close()


if __name__ == '__main__':
    main()
