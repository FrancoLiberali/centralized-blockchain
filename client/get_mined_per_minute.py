import argparse
from datetime import datetime

from common.block_interface import recv_hash_and_block_json
from common.common import STORAGE_MANAGER_HOST, \
    STORAGE_MANAGER_MINED_PER_MINUTE_PORT, \
    DATE_SIZE_LEN_IN_BYTES, \
    DATE_STRING_FORMAT, \
    HASH_LIST_SIZE_LEN_IN_BYTES
from common.responses import RESPONSE_SIZE_IN_BYTES, \
    OK_RESPONSE_CODE, \
    NOT_FOUND_RESPONSE_CODE, \
    SERVICE_UNAVAILABLE_RESPONSE_CODE
from common.safe_tcp_socket import SafeTCPSocket

def main():
    parser = argparse.ArgumentParser(
        description='Centralized Blockchain client for getting blocks mined in certain minute.')
    parser.add_argument(
        'minute',
        metavar='<minute>',
        type=str,
        help='"DD/MM/YYYY hh:mm" minute to get mined blocks, e.g ./get_mined_per_minute.sh "25/04/2021 16:04"'
    )

    args = parser.parse_args()
    minute_string = args.minute
    try:
        datetime.strptime(minute_string, DATE_STRING_FORMAT)
    except ValueError:
        print("Date format for minute is incorrect. Example: ./get_mined_per_minute.sh \"25/04/2021 16:04\"")
        return 1

    sock = SafeTCPSocket.newClient(
        STORAGE_MANAGER_HOST, STORAGE_MANAGER_MINED_PER_MINUTE_PORT)

    sock.send_string_with_len_prepended(minute_string, DATE_SIZE_LEN_IN_BYTES)

    response_code = sock.recv_int(RESPONSE_SIZE_IN_BYTES)
    if response_code == OK_RESPONSE_CODE:
        block_amount = sock.recv_int(HASH_LIST_SIZE_LEN_IN_BYTES)
        print(f"{block_amount} blocks mined in {minute_string}:")
        for i in range(0, block_amount):
            block_hash, block_json = recv_hash_and_block_json(sock)
            print(f"\t{i + 1} - {hex(block_hash)}")
            print(f"{block_json}")
    elif response_code == NOT_FOUND_RESPONSE_CODE:
        print(f"No blocks have been mined in minute {minute_string}")
    elif response_code == SERVICE_UNAVAILABLE_RESPONSE_CODE:
        print("Oops! Too many data is being readed at this moment, please retry later")
    else:
        print("Oops! Unknown error")
    sock.close()


if __name__ == '__main__':
    main()
