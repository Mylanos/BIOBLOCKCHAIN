from re import S
from bioblockchain.block import Block
from bioblockchain.transaction import Transaction
from bioblockchain.validators import Validators
from ecdsa import NIST384p, keys
import bioblockchain.config as config
from bioblockchain.wallet import Wallet
from random import randint
from secrets import compare_digest

#TODO argparse

class Blockchain:
    def __init__(self):
        self.chain = [Block.genesis()]

    # wrapper function
    def create_block(self, transactions, wallet):
        block = Block.create_block(
            self.chain[len(self.chain) - 1],
            transactions,
            wallet
        )
        return block

    def add_block(self, block: Block):
        self.chain.append(block)
        return block

    def is_valid_block(self, block: Block):
        last_block = self.chain[-1]
        if((last_block.seq_number + 1) == block.seq_number and
                last_block.hash_hexdigest == block.previous_hash_hexdigest):
            #TODO not sure if its needed to verify the proposer with block method verify_proposer 
            if(block.hash_hexdigest == Block.block_hash(block).hexdigest() and block.verify_block()):
                return True
        return False

    #updates the block by appending the prepare and commit messages to the block
    def update_block(self, hash, block_pool, prepare_pool, commit_pool):
        block = block_pool.getBlock(hash)
        block.prepareMessages = prepare_pool.list[hash]
        block.commitMessages = commit_pool.list[hash]
        self.addBlock(block)
  

    def display_chain(self):
        for i in range(len(self.chain)):
            print(self.chain[i])
        
    

    @property
    def last_block(self):
        return self.chain[-1]


if __name__ == "__main__":
    blockchain = Blockchain()
    stephan = Wallet("Stephan's Super Secret Phrase")
    alice = Wallet("Alice's Super Secret Phrase")

    matchers = Validators(config.NUMBER_OF_NODES)
    tx1 = Transaction("Stephan just entered room E104", stephan)

    # print(tx1.verify_transaction())

    # print(tx1.toJSON())

    data = {"id": 1234, "room-entered": "E104",
            "verificated": True, "approved-by": "Stephan"}

    tx2 = Transaction(data, alice)
    signature = stephan.sign(data)
    tx2.payload = {}
    proposer1 = matchers._list[1]
    proposer2 = matchers._list[2]

    block1 = blockchain.create_block([tx1], proposer1)


    block2 = blockchain.create_block([tx2], proposer2)
    last_block = blockchain.last_block

    print(block2.verify_proposer(proposer2))
    print(blockchain.is_valid_block(block2))

    """
    seed = urandom(NIST384p.baselen) # or other starting point
    keypair1 = utils.generate_key_from_seed(seed)
    keypair2 = utils.generate_key_from_seed(seed)
    message = b"message"
    signature = keypair1.sign(message)
    assert keypair1.to_string() == keypair2.to_string()
    utils.verify_signature(keypair1.verifying_key, signature, message)
    """
