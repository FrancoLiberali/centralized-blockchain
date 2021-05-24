import json

from common.common import BLOCK_APPENDER_HOST, \
    BLOCK_APPENDER_PORT, \
    MINED_PER_MINER_SIZE_LEN_IN_BYTES, \
    SUCESSFULL_INDEX, \
    WRONG_INDEX
from common.responses import RESPONSE_SIZE_IN_BYTES, \
    OK_RESPONSE_CODE
from common.safe_tcp_socket import SafeTCPSocket

def main():
    sock = SafeTCPSocket.newClient(
        BLOCK_APPENDER_HOST, BLOCK_APPENDER_PORT)

    response_code = sock.recv_int(RESPONSE_SIZE_IN_BYTES)
    if response_code == OK_RESPONSE_CODE:
        mined_per_miner_json = sock.recv_string_with_len_prepended(MINED_PER_MINER_SIZE_LEN_IN_BYTES)
        mined_per_miner = json.loads(mined_per_miner_json)
        print("{:<10} {:<10} {:<10}".format(
            'Miner id', 'Exitosos', 'Erroneos'
        ))
        for miner_id, mined_info_list in mined_per_miner.items():
            print("{:<10} {:<10} {:<10}".format(
                miner_id,
                mined_info_list[SUCESSFULL_INDEX],
                mined_info_list[WRONG_INDEX]
            ))
    else:
        print("Oops! Unknown error")
    sock.close()


if __name__ == '__main__':
    main()
