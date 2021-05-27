import datetime

from business.block import PREV_HASH_KEY

BLOCKS_ADDED_TO_ADJUST_DIFFICULTY = 256
TARGET_TIME_IN_SECONDS = 12
INITIAL_LAST_HASH = 0
INITIAL_DIFFICULTY = 1

class BlockAppender:
    def __init__(self):
        self.difficulty = INITIAL_DIFFICULTY
        self.last_block_hash = INITIAL_LAST_HASH
        self.start_time = datetime.datetime.now()
        self.blocks_added = 0

    def addBlock(self, block):
        if (self.isBlockValid(block)):
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
        return block.header[PREV_HASH_KEY] == self.last_block_hash and isCryptographicPuzzleSolved(block, self.difficulty)

def isCryptographicPuzzleSolved(block, difficulty):
    return block.hash() < (2**256) / difficulty - 1
