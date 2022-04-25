from bioblockchain.config import TRANSACTION_THRESHOLD
from bioblockchain.transaction import Transaction
from bioblockchain.block import Block
from bioblockchain.wallet import Wallet
from bioblockchain.utils import ChainUtils

"""
PreparePool stores all messages of type prepare received or sent from other nodes.
"""


class MessagePool:

    def __init__(self) -> None:
        self.messages = {}
        self.message = "Start the next round!"

    def prepare(self, block: Block, wallet: Wallet):
        prepare = self.create_prepare(block, wallet)
        self.prepare_messages[block.hash] = []
        self.list[block.hash].append(prepare)
        return prepare

    def create_message(self, block: Block, wallet: Wallet):
        # TODO create maybe a prepare object?
        round_change = {"public_key": wallet._verif_key,
                        "message": self.message,
                        "signature": wallet.sign(block.hash),
                        "block_hash": block.hash}

        self.messages[block.hash] = [round_change]
        return round_change

    def find_message(self, message):
        return [m for m in self.messages[message["block_hash"]] if m["public_key"] == message["public_key"]]

    def check_valid_message(self, message):
        return ChainUtils.verify_signature(message["public_key"], message["signature"], ChainUtils.hash(message["message"] + message["block_hash"]))

    def add_message(self, message):
        self.messages[message["blockhash"]].append(message)