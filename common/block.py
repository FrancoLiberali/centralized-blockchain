from hashlib import sha256

MAX_ENTRIES_AMOUNT = 256

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