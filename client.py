import socket
import argparse

from common import BLOCK_BUILDER_HOST, \
    BLOCK_BUILDER_PORT, \
    MAX_ENTRY_SIZE_IN_BYTES, \
    CHUNCK_SIZE_LEN_IN_BYTES, \
    BLOCK_BUILDER_RESPONSE_SIZE_IN_BYTES, \
    BLOCK_BUILDER_OK_RESPONSE_CODE, \
    BLOCK_BUILDER_SERVICE_UNAVAILABLE_RESPONSE_CODE

def main():
    parser = argparse.ArgumentParser(description='Centralized Blockchain client.')
    parser.add_argument('input_file_path', metavar='<input_file>', type=argparse.FileType('rb'), help='path to the file to read a chunck')

    args = parser.parse_args()
    
    input = args.input_file_path
    chunk = input.read(MAX_ENTRY_SIZE_IN_BYTES)
    input.close()

    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    sock.connect((BLOCK_BUILDER_HOST, BLOCK_BUILDER_PORT))

    message = len(chunk).to_bytes(
        CHUNCK_SIZE_LEN_IN_BYTES, byteorder='big', signed=False) + chunk
    total_sent = 0
    while total_sent < len(message):
        sent = sock.send(message[total_sent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        total_sent = total_sent + sent

    chunks = []
    bytes_recd = 0
    while bytes_recd < BLOCK_BUILDER_RESPONSE_SIZE_IN_BYTES:
        chunk = sock.recv(BLOCK_BUILDER_RESPONSE_SIZE_IN_BYTES - bytes_recd)
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
    response_code = int.from_bytes(b''.join(chunks), byteorder='big', signed=False)
    if response_code == BLOCK_BUILDER_OK_RESPONSE_CODE:
        print("OK! Your chunck will be mined and added to the blockchain")
    elif response_code == BLOCK_BUILDER_SERVICE_UNAVAILABLE_RESPONSE_CODE:
        print("Oops! Too many data is being mined at this moment, please retry later")
    else:
        print("Oops! Unknown error")


if __name__ == '__main__':
    main()
