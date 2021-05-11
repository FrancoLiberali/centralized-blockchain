import argparse

import sys
sys.path.append(".")

from common.common import BLOCK_BUILDER_HOST, \
    BLOCK_BUILDER_PORT, \
    MAX_ENTRY_SIZE_IN_BYTES, \
    CHUNK_SIZE_LEN_IN_BYTES, \
    BLOCK_BUILDER_RESPONSE_SIZE_IN_BYTES, \
    BLOCK_BUILDER_OK_RESPONSE_CODE, \
    BLOCK_BUILDER_SERVICE_UNAVAILABLE_RESPONSE_CODE

from common.safe_tcp_socket import SafeTCPSocket

def main():
    parser = argparse.ArgumentParser(description='Centralized Blockchain client.')
    parser.add_argument('input_file_path', metavar='<input_file>', type=argparse.FileType('rb'), help='path to the file to read a chunck')

    args = parser.parse_args()
    
    input = args.input_file_path
    chunk = input.read(MAX_ENTRY_SIZE_IN_BYTES)
    input.close()

    sock = SafeTCPSocket.newClient(BLOCK_BUILDER_HOST, BLOCK_BUILDER_PORT)

    message = len(chunk).to_bytes(
        CHUNK_SIZE_LEN_IN_BYTES, byteorder='big', signed=False) + chunk
    sock.send(message)

    response = sock.recv(BLOCK_BUILDER_RESPONSE_SIZE_IN_BYTES)
    response_code = int.from_bytes(response, byteorder='big', signed=False)
    if response_code == BLOCK_BUILDER_OK_RESPONSE_CODE:
        print("OK! Your chunck will be mined and added to the blockchain")
    elif response_code == BLOCK_BUILDER_SERVICE_UNAVAILABLE_RESPONSE_CODE:
        print("Oops! Too many data is being mined at this moment, please retry later")
    else:
        print("Oops! Unknown error")


if __name__ == '__main__':
    main()
