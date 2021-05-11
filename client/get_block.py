import argparse

import sys
sys.path.append(".")


from common.common import STORAGE_MANAGER_HOST, \
    STORAGE_MANAGER_READ_PORT
from common.responses import RESPONSE_SIZE_IN_BYTES, \
    OK_RESPONSE_CODE, \
    NOT_FOUND_RESPONSE_CODE, \
    SERVICE_UNAVAILABLE_RESPONSE_CODE
from common.safe_tcp_socket import SafeTCPSocket
from common.block_interface import send_hash, recv_hash_and_block_json

def main():
    parser = argparse.ArgumentParser(
        description='Centralized Blockchain client for getting a block.')
    parser.add_argument('block_hash', metavar='<block_hash>',
                        type=str, help='hex hash of the block')

    args = parser.parse_args()
    block_hash = args.block_hash

    sock = SafeTCPSocket.newClient(
        STORAGE_MANAGER_HOST, STORAGE_MANAGER_READ_PORT)
    send_hash(sock, int(block_hash, 16))

    response_code = sock.recv_int(RESPONSE_SIZE_IN_BYTES)
    if response_code == OK_RESPONSE_CODE:
        block_hash_response, block = recv_hash_and_block_json(sock)  # TODO ver si el block_hash_response lo quiero o no
        block_hash_response_hex = hex(block_hash_response)
        # TODO codigo repetido con el storage manager
        with open(f"./blockchain_files/{block_hash_response_hex}.json", "w") as block_file:
            block_file.write(block)
        print(
            f"OK! The block has been saved in blockchain_files/{block_hash_response_hex}.json")
    elif response_code == NOT_FOUND_RESPONSE_CODE:
        print(
            f"Oops! Could not found block with hash {block_hash}. Remember that it should be ther hex representation starting with the '0x...'")
    elif response_code == SERVICE_UNAVAILABLE_RESPONSE_CODE:
        print("Oops! Too many data is being readed at this moment, please retry later")
    else:
        print("Oops! Unknown error")
    sock.close()


if __name__ == '__main__':
    main()
