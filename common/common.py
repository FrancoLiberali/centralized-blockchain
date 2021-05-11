import sys
from hashlib import sha256

INITIAL_LAST_HASH = 0
INITIAL_DIFFICULTY = 1
MAX_ENTRIES_AMOUNT = 5
MAX_NONCE = sys.maxsize # TODO esto no va, no se como pero representa numeros mas grandes esta mierda de python
TARGET_TIME_IN_SECONDS = 10  # TODO poner 12

STORAGE_MANAGER_HOST = 'storage_manager' # TODO envvar
STORAGE_MANAGER_PORT = 12345          # TODO envvar
BLOCK_SIZE_LEN_IN_BYTES = 4

BLOCK_BUILDER_HOST = 'blockchain_server' # TODO envvar
BLOCK_BUILDER_PORT = 12346  # TODO envvar

MAX_ENTRY_SIZE_IN_BYTES = 65356
CHUNK_SIZE_LEN_IN_BYTES = 4
BLOCK_BUILDER_RESPONSE_SIZE_IN_BYTES = 1
BLOCK_BUILDER_OK_RESPONSE_CODE = 200
BLOCK_BUILDER_SERVICE_UNAVAILABLE_RESPONSE_CODE = 503

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
