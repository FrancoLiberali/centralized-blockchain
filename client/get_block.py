import argparse
import logging

from communications.block_interface import send_hash, recv_hash_and_block_json
from config.envvars import STORAGE_MANAGER_HOST_KEY, STORAGE_MANAGER_READ_PORT_KEY, get_config_params
from communications.responses import RESPONSE_SIZE_IN_BYTES, \
    OK_RESPONSE_CODE, \
    NOT_FOUND_RESPONSE_CODE, \
    SERVICE_UNAVAILABLE_RESPONSE_CODE
from communications.safe_tcp_socket import SafeTCPSocket

def main():
    parser = argparse.ArgumentParser(
        description='Centralized Blockchain client for getting a block.')
    parser.add_argument('block_hash', metavar='<block_hash>',
                        type=str, help='hex hash of the block')

    args = parser.parse_args()
    block_hash = args.block_hash

    config_params = get_config_params(
        [STORAGE_MANAGER_HOST_KEY, STORAGE_MANAGER_READ_PORT_KEY],
        logging.getLogger()
    )

    sock = SafeTCPSocket.newClient(
        config_params[STORAGE_MANAGER_HOST_KEY], config_params[STORAGE_MANAGER_READ_PORT_KEY])
    send_hash(sock, int(block_hash, 16))

    response_code = sock.recv_int(RESPONSE_SIZE_IN_BYTES)
    if response_code == OK_RESPONSE_CODE:
        block_hash_response, block_json = recv_hash_and_block_json(sock)
        print(f"Block with hash {hex(block_hash_response)} is:")
        print(f"{block_json}")
    elif response_code == NOT_FOUND_RESPONSE_CODE:
        print(
            f"Oops! Could not found block with hash {block_hash}. Remember that it should be the hex representation starting with the '0x...'")
    elif response_code == SERVICE_UNAVAILABLE_RESPONSE_CODE:
        print("Oops! Too many data is being readed at this moment, please retry later")
    else:
        print("Oops! Unknown error")
    sock.close()


if __name__ == '__main__':
    main()
