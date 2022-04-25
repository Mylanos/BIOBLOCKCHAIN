from bioblockchain.transaction import Transaction
from bioblockchain.block import Block

#TODO redundance of the pools(block, transaction etc..) - try to refactor it into one POOL


"""
BlockPool class holds the blocks until it is added to the chain. 
A block is added to the block pool when a PRE-PREPARE message is received.
"""

class BlockPool:

    def __init__(self) -> None:
        self.blocks = []

    def add_block(self, block: Block):
        print("Adding BLOCK to the BLOCK POOL!")
        self.blocks.append(block)
        
    # gets block for given hash
    def get_block(self, hash):
        return [b for b in self.blocks if b.hash == hash]

    def exists(self, block: Block):
        return [b for b in self.blocks if b.hash == block.hash]
        
    def clear(self):
        print("Clearing TRANSACTION POOL!")
        self.transactions = []