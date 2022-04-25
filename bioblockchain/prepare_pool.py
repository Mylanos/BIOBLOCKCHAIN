from bioblockchain.config import TRANSACTION_THRESHOLD
from bioblockchain.transaction import Transaction
from bioblockchain.block import Block
from bioblockchain.wallet import Wallet
from bioblockchain.utils import ChainUtils

"""
PreparePool stores all messages of type prepare received or sent from other nodes.
"""

class Prepare:
    def __init__(self, block, wallet):
        self.block_hash_hex = block.hash_hexdigest
        self.block_hash = block.hash
        self.public_key = wallet._verif_key
        self.content = {"block_hash": self.block_hash_hex, 
                        "public_key": wallet._verif_key}
        self.signature = wallet.sign(self.content)

class PreparePool:

    def __init__(self) -> None:
        self.prepares = {}

    def prepare(self, block: Block, wallet: Wallet):
        prepare = Prepare(block, wallet)
        self.prepares[block.hash_hexdigest] = []
        return prepare

    def add_prepare(self, prepare):
        self.prepares[prepare.block_hash_hex]

    def find_prepare(self, prepare):
         return [p for p in self.prepares[prepare.block_hash_hex] if p.public_key == prepare.public_key] 
    
    def is_valid(self, prepare):
        return ChainUtils.verify_signature(prepare.public_key, prepare.signature, prepare.content)