from hashlib import sha256

MAX_ENTRIES_AMOUNT = 256
MAX_NONCE = 2**(32*8) - 1  # max number posible in 32 bytes

HEADER_KEY = 'header'
PREV_HASH_KEY = 'prev_hash'
NONCE_KEY = 'nonce'
TIMESTAMP_KEY = 'timestamp'
DIFFICULTY_KEY = 'difficulty'
ENTRIES_AMOUNT_KEY = 'entries_amount'

class Block:
    def __init__(self, entries):
        self.header = {
            PREV_HASH_KEY: 0,
            NONCE_KEY: 0,
            TIMESTAMP_KEY: None,
            DIFFICULTY_KEY: 0,
            ENTRIES_AMOUNT_KEY: len(entries),
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
        """.format(hex(self.hash()), hex(self.header[PREV_HASH_KEY]), self.header[NONCE_KEY], self.header[TIMESTAMP_KEY], self.header[ENTRIES_AMOUNT_KEY], self.header[DIFFICULTY_KEY], entries)
