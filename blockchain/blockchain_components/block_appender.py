import datetime
import json
from common.common import isCryptographicPuzzleSolved, \
    INITIAL_DIFFICULTY, \
    INITIAL_LAST_HASH, \
    STORAGE_MANAGER_HOST, \
    STORAGE_MANAGER_WRITE_PORT, \
    TARGET_TIME_IN_SECONDS
from common.safe_tcp_socket import SafeTCPSocket
from common.block_interface import send_block_with_hash

BLOCKS_ADDED_TO_ADJUST_DIFFICULTY = 2  # TODO poner 256

class BlockAppender:
    def __init__(self):
        self.difficulty = INITIAL_DIFFICULTY
        self.last_block_hash = INITIAL_LAST_HASH
        self.start_time = datetime.datetime.now()
        self.blocks_added = 0
        self.socket = SafeTCPSocket.newClient(
            STORAGE_MANAGER_HOST, STORAGE_MANAGER_WRITE_PORT)

    def addBlock(self, block):
        if (self.isBlockValid(block)):
            send_block_with_hash(self.socket, block)
            self.blocks_added += 1
            self.last_block_hash = block.hash()
            self.adjustDifficulty()
            return True
        return False

    def adjustDifficulty(self):
        if self.blocks_added == BLOCKS_ADDED_TO_ADJUST_DIFFICULTY:
            now = datetime.datetime.now()
            elapsed_time = (now -
                            self.start_time).total_seconds()

            self.difficulty = self.difficulty * \
                (TARGET_TIME_IN_SECONDS / elapsed_time) * \
                BLOCKS_ADDED_TO_ADJUST_DIFFICULTY

            self.start_time = now
            self.blocks_added = 0

    def isBlockValid(self, block):
        return block.header['prev_hash'] == self.last_block_hash and isCryptographicPuzzleSolved(block, self.difficulty)

def main(miners_queue, miners_coordinator_queue):
    block_appender = BlockAppender()
    while True:
        message = miners_queue.get()
        if block_appender.addBlock(message.block):
            miners_coordinator_queue.put(
                (block_appender.last_block_hash,
                 block_appender.difficulty)
            )
