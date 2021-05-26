from hashlib import sha256

MINERS_AMOUNT = 4  # TODO envvar
MINERS_IDS = range(1, MINERS_AMOUNT + 1)

INITIAL_LAST_HASH = 0
INITIAL_DIFFICULTY = 1
MAX_ENTRIES_AMOUNT = 256
MAX_NONCE = 2**(32*8) - 1 # max number posible in 32 bytes
TARGET_TIME_IN_SECONDS = 12

STORAGE_MANAGER_HOST = 'storage_manager' # TODO envvar
STORAGE_MANAGER_WRITE_PORT = 12345          # TODO envvar
STORAGE_MANAGER_READ_PORT = 12346  # TODO envvar
STORAGE_MANAGER_MINED_PER_MINUTE_PORT = 12347  # TODO envvar

BLOCK_BUILDER_HOST = 'blockchain_server' # TODO envvar
BLOCK_BUILDER_PORT = 12345  # TODO envvar

BLOCK_APPENDER_HOST = 'blockchain_server' # TODO envvar
MINED_COUNTER_PORT = 12346  # TODO envvar
MINER_ID_LEN_IN_BYTES = 4
ALL_MINERS = 0
MINED_PER_MINER_SIZE_LEN_IN_BYTES = 4
ADD_SUCCESSFUL_MINING_OP = 1
ADD_WRONG_MINING_OP = 2
SUCCESSFUL_INDEX = 0
WRONG_INDEX = 1

MAX_ENTRY_SIZE_IN_BYTES = 65356
CHUNK_SIZE_LEN_IN_BYTES = 4

DATE_SIZE_LEN_IN_BYTES = 4
DATE_STRING_FORMAT = '%d/%m/%Y %H:%M'
HASH_LIST_SIZE_LEN_IN_BYTES = 4

def isCryptographicPuzzleSolved(block, difficulty):
    return block.hash() < (2**256) / difficulty - 1

class Block:
    def __init__(self, entries):
        self.header = {
            'prev_hash': 0,
            'nonce': 0,
            'timestamp': None,
            'difficulty': 0,
            'entries_amount': len(entries),
        }
        if (len(entries) <= MAX_ENTRIES_AMOUNT):
            self.entries = entries
        else:
            raise 'Exceeding max block size'

    def hash(self):
        return int(sha256(repr(self.header).encode('utf-8') + repr(self.entries).encode('utf-8')).hexdigest(), 16)

    def __str__(self):
        entries = ",\n\t\t\t".join(map(repr, self.entries))
        return """
        'block_hash': {0}

        'header': {{
            'prev_hash':{1}
            'nonce': {2}
            'timestamp': {3}
            'difficulty': {5}
            'entries_amount': {4}
        }}

        'entries': [
\t\t\t{6}
        ]
        """.format(hex(self.hash()), hex(self.header['prev_hash']), self.header['nonce'], self.header['timestamp'], self.header['entries_amount'], self.header['difficulty'], entries)
