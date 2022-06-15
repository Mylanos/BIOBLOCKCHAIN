from re import S
from bioblockchain.block import Block
from bioblockchain.transaction import Transaction
from bioblockchain.wallet import Wallet

#TODO argparse
#TODO implement search for the transactions for given wallet blockchain(MAYBE UNNECESARY)

class Blockchain:
    """blockchain class containing list(chain) of blocks
    """
    def __init__(self):
        self.chain = [Block.genesis()]

    def create_block(self, transactions, wallet):
        """wrapper function for Block instantiation

        Args:
            transactions (list of Transaction objects): list of transactions that will be stored in newly created block
            wallet (Wallet object): proposer of the block

        Returns:
            Block: instance of Block object
        """
        block = Block.create_block(
            self.chain[len(self.chain) - 1],
            transactions,
            wallet
        )
        return block

    def add_block(self, block: Block):
        """append block to blockchain

        Args:
            block (Block): block to be appended

        Returns:
            Block: appended block
        """
        self.chain.append(block)
        return block

    def is_valid_block(self, block: Block):
        """check for validity of block

        Args:
            block (Block): Block object to be validated

        Returns:
            Bool: True if valid, else False
        """
        last_block = self.chain[-1]
        if((last_block.seq_number + 1) == block.seq_number and
                last_block.hash_hexdigest == block.previous_hash_hexdigest):
            #TODO not sure if its needed to verify the proposer with block method verify_proposer 
            if(block.hash_hexdigest == Block.block_hash(block).hexdigest() and block.verify_block()):
                return True
        return False
  

    def display_chain(self):
        """prints out the blockchain content
        """
        for i in range(len(self.chain)):
            print(self.chain[i])

    @property
    def last_block(self):
        return self.chain[-1]


if __name__ == "__main__":
    blockchain = Blockchain()
    stephan = Wallet("Stephan's Super Secret Phrase")
    alice = Wallet("Alice's Super Secret Phrase")

    tx1 = Transaction("Stephan just entered room E104", stephan)

    data = {"id": 1234, "room-entered": "E104",
            "verificated": True, "approved-by": "Stephan"}

    tx2 = Transaction(data, alice)
    signature = stephan.sign(data)
    tx2.payload = {}
    proposer1 = Wallet("validatooor2")
    proposer2 = Wallet("validatooor1")

    block1 = blockchain.create_block([tx1], proposer1)


    block2 = blockchain.create_block([tx2], proposer2)
    last_block = blockchain.last_block

    print(block2.verify_proposer(proposer2))
    print(blockchain.is_valid_block(block2))

