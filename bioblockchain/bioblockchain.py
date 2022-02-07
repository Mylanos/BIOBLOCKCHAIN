from re import S
from bioblockchain.block import Block
from bioblockchain.transaction import Transaction
from bioblockchain.validators import Validators
from ecdsa import NIST384p, keys
import config
from bioblockchain.wallet import Wallet

class BioBlockchain:
    def __init__(self):
        self.chain = [Block.genesis()]
        self.validators = Validators.generate_validators(config.NUMBER_OF_NODES)
    
    def create_block(self, transactions, wallet):
        block = Block.create_block(
            self.chain[len(self.chain) - 1],
            transactions,
            wallet
        )
        self.chain.append(block)
        return block

    def get_proposer(self):
        pass

    def is_valid_block(self):
        pass

    def update_block(self):
        pass

    def display_chain(self):
        for i in range(len(self.chain)):
            print(self.chain[i])

    @property
    def last_block(self):
        return self.chain[-1]

if __name__ == "__main__":
    blockchain = BioBlockchain()
    stephan = Wallet("Stephan's Super Secret Phrase")
    print(stephan)
    validators = Validators(config.NUMBER_OF_NODES)
    tx1 = Transaction("Stephan just entered room E104", stephan)

    data = {"id": 1234, "room-entered": "E104", "verificated": True, "approved-by": "Stephan"}
    signature = stephan.sign(data)

    blockchain.create_block([tx1], validators._list[1])
    blockchain.create_block([tx1], validators._list[1])

    print(blockchain.last_block)

    print(blockchain.last_block.verify_block())

    """
    seed = urandom(NIST384p.baselen) # or other starting point
    keypair1 = utils.generate_key_from_seed(seed)
    keypair2 = utils.generate_key_from_seed(seed)
    message = b"message"
    signature = keypair1.sign(message)
    assert keypair1.to_string() == keypair2.to_string()
    utils.verify_signature(keypair1.verifying_key, signature, message)
    """
