import datetime
import socket
import json
from common.common import isCryptographicPuzzleSolved, INITIAL_DIFFICULTY, INITIAL_LAST_HASH, STORAGE_MANAGER_HOST, STORAGE_MANAGER_PORT, BLOCK_SIZE_LEN_IN_BYTES

BLOCKS_ADDED_TO_ADJUST_DIFFICULTY = 2  # TODO poner 256
TARGET_TIME_IN_SECONDS = 1 # TODO poner 12

class BlockWriterInterface:
    def __init__(self):
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.socket.connect((STORAGE_MANAGER_HOST, STORAGE_MANAGER_PORT))

    def write(self, block):
        total_sent = 0
        data = self.serialize_block(block)
        # print(len(data))
        # print(data)
        while total_sent < len(data):
            sent = self.socket.send(data[total_sent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent

    def serialize_block(self, block):
        block_in_json = json.dumps({
            "header": {
                'prev_hash': block.header['prev_hash'],
                'nonce': block.header['nonce'],
                'timestamp': block.header['timestamp'].timestamp(),
                'difficulty': block.header['difficulty'],
                'entries_amount': block.header['entries_amount'],
            },
            "entries": block.entries
        }).encode('utf-8')
        return len(block_in_json).to_bytes(BLOCK_SIZE_LEN_IN_BYTES, byteorder='big', signed=False) + block_in_json

class BlockAppender:
    def __init__(self):
        self.difficulty = INITIAL_DIFFICULTY
        self.last_block_hash = INITIAL_LAST_HASH
        self.start_time = datetime.datetime.now()
        self.blocks_added = 0
        self.block_writer_interface = BlockWriterInterface()

    def addBlock(self, block):
        if (self.isBlockValid(block)):
            self.block_writer_interface.write(block)
            # TODO tener en cuenta para lecturas que la mayor cantidad de fd's abiertos por proceso es 1024
            self.blocks_added += 1
            self.last_block_hash = block.hash()
            self.adjustDifficulty()
            return True
        return False

    def adjustDifficulty(self):
        if self.blocks_added == BLOCKS_ADDED_TO_ADJUST_DIFFICULTY:
            ahora = datetime.datetime.now()
            elapsed_time = (ahora -
                            self.start_time).total_seconds()

            self.difficulty = self.difficulty * \
                (TARGET_TIME_IN_SECONDS / elapsed_time) * \
                BLOCKS_ADDED_TO_ADJUST_DIFFICULTY

            self.start_time = ahora
            self.blocks_added = 0

    def isBlockValid(self, block):
        return block.header['prev_hash'] == self.last_block_hash and isCryptographicPuzzleSolved(block, self.difficulty)

def main(miners_queue, miners_coordinator_queue):
    block_appender = BlockAppender()
    while True:
        message = miners_queue.get()
        if block_appender.addBlock(message.block):
            print(message.block)
            # print(message.miner_id)
            miners_coordinator_queue.put(
                (block_appender.last_block_hash,
                 block_appender.difficulty)
            )
