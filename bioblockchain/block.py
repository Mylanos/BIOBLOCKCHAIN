from hashlib import sha256
from bioblockchain.utils import ChainUtils, TimeUtils
from bioblockchain.wallet import Wallet
import json

#TODO watchout for the proposer print, might be a unnecessary check for strings

class Block:

    def __init__(self, timestamp, previous_hash, current_hash, data, proposer, signature, seq_number):
        """Header"""
        # timestamp of block being hashed
        self.timestamp = timestamp
        self._previous_hash = previous_hash
        self._hash = current_hash
        self.proposer = proposer
        self.signature = signature
        # or index
        self.seq_number = seq_number
        """Payload"""
        # contain transactions
        self.data = data

    @property
    def hash(self):
        return self._hash

    @property
    def hash_hexdigest(self):
        return self._hash.hexdigest()
    
    @property
    def previous_hash_hexdigest(self):
        return self._previous_hash.hexdigest()

    @property
    def previous_hash(self):
        return self._previous_hash
    
    def __str__(self):
        return f"""
        - - - - - - - - - - - - - - - - - Block - - - - - - - - - - - - - - - - - - - 
        Timestamp   : {self.timestamp}
        Last Hash   : {self._previous_hash.hexdigest()}
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
        proposer = Wallet("B!0BL0CKCH41N")
        previous_hash = ChainUtils.hash("This is the previous hash for genesis block")
        now = TimeUtils.my_date()
        content = Block.block_content_to_json(now, previous_hash, [])
        hash = ChainUtils.hash(content)
        return Block(now, previous_hash, hash, 
                     [], proposer.verif_key, proposer.sign_data(content), 0)
    
    
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
        timestamp = TimeUtils.my_date()
        previous_hash = previous_block._hash
        proposer = proposer_wallet.verif_key
        seq_number = previous_block.seq_number + 1

        content = Block.block_content_to_json(timestamp, previous_hash, data)
        block_hash = ChainUtils.hash(content)
        signature = proposer_wallet.sign(content)
        return Block(timestamp, previous_hash, block_hash, 
                     data, proposer, signature, seq_number)

    # signs the block using the wallet instance
    @staticmethod
    def sign_block_hash(hash, wallet):
        return wallet.sign(hash)


    #TODO maybe just remake to a __dict__ function
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
        return {"timestamp" : timestamp, 
                "previous_hash": previous_hash.hexdigest(), 
                "data": ChainUtils.transactionlist_to_json(data)}

    @staticmethod
    def block_hash(block):
        content = Block.block_content_to_json(block.timestamp, block.previous_hash, block.data)
        return ChainUtils.hash(content)

    def verify_block(self):
        """verifies block

        Returns:
            True if valid block, else False
        """
        return ChainUtils.verify_signature(
            self.proposer,
            self.signature,
            Block.block_content_to_json(self.timestamp, self._previous_hash, self.data)
        )

    def verify_proposer(self, wallet: Wallet):
        return (self.proposer == wallet.verif_key)

    