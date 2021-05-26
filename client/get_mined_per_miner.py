import argparse
import json

from common.common import ALL_MINERS, \
    BLOCK_APPENDER_HOST, \
    MINED_COUNTER_PORT, \
    MINED_PER_MINER_SIZE_LEN_IN_BYTES, \
    MINER_ID_LEN_IN_BYTES, \
    SUCCESSFUL_INDEX, \
    WRONG_INDEX
from common.responses import RESPONSE_SIZE_IN_BYTES, \
    OK_RESPONSE_CODE
from common.safe_tcp_socket import SafeTCPSocket

def main():
    parser = argparse.ArgumentParser(
        description='Centralized Blockchain client for getting blocks mined per miner.')
    parser.add_argument(
        '-m',
        '--miner_id',
        const=ALL_MINERS,
        default=ALL_MINERS,
        type=int,
        help='id of the miner to get info. Info of all miners will be returned if empty',
        nargs='?')

    args = parser.parse_args()
    miner_id = args.miner_id

    sock = SafeTCPSocket.newClient(
        BLOCK_APPENDER_HOST, MINED_COUNTER_PORT)
    sock.send_int(miner_id, MINER_ID_LEN_IN_BYTES)

    response_code = sock.recv_int(RESPONSE_SIZE_IN_BYTES)
    if response_code == OK_RESPONSE_CODE:
        print("{:<10} {:<10} {:<10}".format(
            'Miner id', 'Successful', 'Wrong'
        ))
        mined_per_miner_json = sock.recv_string_with_len_prepended(MINED_PER_MINER_SIZE_LEN_IN_BYTES)
        mined_per_miner = json.loads(mined_per_miner_json)
        if miner_id == ALL_MINERS:
            for miner_id, mined_info_list in mined_per_miner.items():
                print_row_for_miner(miner_id, mined_info_list)
        else:
            print_row_for_miner(miner_id, mined_per_miner)
    else:
        print("Oops! Unknown error")
    sock.close()

def print_row_for_miner(miner_id, mined_info_list):
    print("{:<10} {:<10} {:<10}".format(
        miner_id,
        mined_info_list[SUCCESSFUL_INDEX],
        mined_info_list[WRONG_INDEX]
    ))


if __name__ == '__main__':
    main()
