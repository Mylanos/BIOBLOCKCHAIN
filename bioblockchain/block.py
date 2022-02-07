from hashlib import sha256
from os import stat_result
from utils import ChainUtils
from datetime import datetime
from bioblockchain.wallet import Wallet
import json

#TODO watchout for the proposer print, might be a unnecessary check for strings

class Block:

    def __init__(self, timestamp, previous_hash, current_hash, data, proposer, signature, seq_number):
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self._hash = current_hash
        self.data = data
        self.proposer = proposer
        self.signature = signature
        self.seq_number = seq_number

    @property
    def hash(self):
        return self._private_key

    @hash.setter
    def hash(self, key):
        self._private_key = key
    
    def __str__(self):
        return f"""
        - - - - - - - - - - - - - - - - - Block - - - - - - - - - - - - - - - - - - - 
        Timestamp   : {self.timestamp}
        Last Hash   : {self.previous_hash.hexdigest()}
        Hash        : {self._hash.hexdigest()}
        Data        : {self.data}
        Proposer    : {ChainUtils.string_from_verifkey(self.proposer) if type(self.proposer ) != str else self.proposer}
        Signature   : {self.signature.hex()}
        Sequence No : {self.seq_number}
        - - - - - - - - - - - - - - - - - - - - - - - - - - -- - - - - - - - - - - - -
        """

    
    @staticmethod
    def genesis():
        """creates genesis block of bioblockchain

        Returns:
            Block object: genesis block
        """
        previous_hash = sha256("This is the genesis of super duper biometric blockchain".encode())
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        content = Block.block_content_to_json(now, previous_hash, [])
        hash = ChainUtils.hash(content)
        return Block(datetime.now(), ChainUtils.hash("genesis hash"), hash, 
                     [], "B!0BL0CKCH41N", b"signature", 0)
    
    
    @staticmethod
    def create_block(previous_block, data, proposer_wallet):
        """creates another block to blockchain

        Args:
            previous_block (Block object): previous block to be connected with the newly appended block
            data ([Transaction objects list]): listof new transactions
            proposer_wallet (Wallet object): voted proposer to append new block to blockchain

        Returns:
            Block object:  new block
        """
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        previous_hash = previous_block._hash
        proposer = proposer_wallet.verif_key

        content = Block.block_content_to_json(timestamp, previous_hash, data)
        block_hash = ChainUtils.hash(content)
        signature = proposer_wallet.sign(content)
        return Block(timestamp, previous_hash, block_hash, 
                     data, proposer, signature, previous_block.seq_number + 1)

    # signs the passed block using the passed wallet instance
    @staticmethod
    def sign_block_hash(hash, wallet):
        return wallet.sign(hash)

    @staticmethod
    def block_content_to_json(timestamp, previous_hash, data):
        """constructs json of block's content

        Args:
            timestamp (String): date
            previous_hash (Hash object): hash pointing at the last block
            data ([Transaction objects list]): transactions

        Returns:
            dict : dict containing info about block
        """
        return { "timestamp" : timestamp, 
                    "previous_hash": previous_hash.hexdigest(), 
                    "data": ChainUtils.transactionlist_to_json(data)}

    def block_hash(self):
        pass

    def verify_block(self):
        """verifies block

        Returns:
            True if valid block, else False
        """
        return ChainUtils.verify_signature(
            self.proposer,
            self.signature,
            Block.block_content_to_json(self.timestamp, self.previous_hash, self.data)
        )

    def verify_proposer(self, block, proposer):
        return block.proposer == proposer

    