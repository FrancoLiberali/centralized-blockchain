import datetime
from common import isCryptographicPuzzleSolved, INITIAL_DIFFICULTY, INITIAL_LAST_HASH

BLOCKS_ADDED_TO_ADJUST_DIFFICULTY = 2  # TODO poner 256
TARGET_TIME_IN_SECONDS = 1 # TODO poner 12

class BlockAppender:
    def __init__(self):
        self.difficulty = INITIAL_DIFFICULTY
        self.last_block_hash = INITIAL_LAST_HASH
        self.start_time = datetime.datetime.now()
        self.blocks_added = 0

    def addBlock(self, block):
        if (self.isBlockValid(block)):
            # TODO self.blocks.append(newBlock)
            self.blocks_added += 1
            self.last_block_hash = block.hash()
            self.adjustDifficulty()
            return True
        return False

    def adjustDifficulty(self):
        if self.blocks_added == BLOCKS_ADDED_TO_ADJUST_DIFFICULTY:
            print("justando dificultad")
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
        mined_block = miners_queue.get()
        print(f"block supuestamente ganador recibido: {mined_block}")
        print(
            f"self.difficulty: {block_appender.difficulty}, self.last_block_hash: {hex(block_appender.last_block_hash)}")
        if block_appender.addBlock(mined_block):
            # print(mined_block)
            miners_coordinator_queue.put(
                (block_appender.last_block_hash,
                 block_appender.difficulty)
            )
        else:
            print("esta mal")
            print(mined_block.header['prev_hash']
                  == block_appender.last_block_hash)
            print(mined_block.header['difficulty']
                  == block_appender.difficulty)
            print(isCryptographicPuzzleSolved(
                mined_block, block_appender.difficulty))
            print(isCryptographicPuzzleSolved(
                mined_block, mined_block.header['difficulty']))
