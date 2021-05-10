from common import isCryptographicPuzzleSolved, INITIAL_DIFFICULTY, INITIAL_LAST_HASH

class BlockAppender:
    def __init__(self):
        self.difficulty = INITIAL_DIFFICULTY
        self.last_block_hash = INITIAL_LAST_HASH

    def addBlock(self, block):
        if (self.isBlockValid(block)):
            # self.blocks.append(newBlock)
            self.last_block_hash = block.hash()
            # TODO ajustar dificultar
            return True
        return False

    def isBlockValid(self, block):
        return block.header['prev_hash'] == self.last_block_hash and isCryptographicPuzzleSolved(block, self.difficulty)

def main(miners_queue, miners_coordinator_queue):
    block_appender = BlockAppender()
    while True:
        mined_block = miners_queue.get()
        if block_appender.addBlock(mined_block):
            print(mined_block)
            miners_coordinator_queue.put(
                (block_appender.last_block_hash,
                 block_appender.difficulty)
            )
