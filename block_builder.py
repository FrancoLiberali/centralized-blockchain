from common import Block

def main(queue):
    for i in range(0, 10):
        block = Block([f"{i}"])
        queue.put(block)
