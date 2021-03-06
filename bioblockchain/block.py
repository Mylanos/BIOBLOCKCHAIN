from bioblockchain.chain_utils import ChainUtils
from bioblockchain.time_utils import TimeUtils
from bioblockchain.wallet import Wallet
from bioblockchain.transaction import Transaction


class Block:
    """ class representing one block in the blockchain
    """

    def __init__(self, timestamp, previous_hash, current_hash, data, proposer, signature, seq_number):
        """Header"""
        # timestamp of block being hashed
        self.timestamp = timestamp
        # previous hash
        self._previous_hash = previous_hash
        self._hash = current_hash
        # wallet of the proposer
        self.proposer = proposer
        # signature
        self.signature = signature
        # index
        self.seq_number = seq_number

        """Payload"""
        # transactions
        self.data = data

    @property
    def hash(self):
        """ hash is a property representing hash value of given block

        Returns:
            Hash: hash object from hashlib library
        """
        return self._hash

    @property
    def hash_hexdigest(self):
        """
        hash_hexdigest is a property representing string hash value of given block

        Returns:
            str: string hash value 
        """
        return self._hash.hexdigest()

    @property
    def previous_hash_hexdigest(self):
        """
        previous_hash_hexdigest is a property representing string hash value of previous block

        Returns:
            str: string hash value of previous block
        """
        return self._previous_hash.hexdigest()

    @property
    def previous_hash(self):
        """
        previous_hash is a property representing hash value of previous block

        Returns:
            _Hash: hash object from hashlib library
        """
        return self._previous_hash

    def __str__(self):
        """ magic method for string representation of Block instance
        """

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
        """genesis creates genesis block of bioblockchain

        Returns:
            Block object: genesis block
        """
        proposer = Wallet("B!0BL0CKCH41N")
        previous_hash = ChainUtils.hash(
            "This is the previous hash for genesis block")
        now = TimeUtils.my_date()
        genesis_tx = Transaction(
            {"data": "GENESIS BLOCK", "process_id": 42, "location": "Dornbirn"}, proposer)
        content = Block.block_content_to_json(now, previous_hash, genesis_tx)
        hash = ChainUtils.hash(content)
        return Block(now, previous_hash, hash,
                     genesis_tx, proposer.verif_key, proposer.sign(content), 0)

    @staticmethod
    def create_block(previous_block, data, proposer_wallet):
        """create_block is a static method that instantiates Block class

        Args:
            previous_block (Block object): previous block needed for needed attachment in the new block
            data ([Transaction object list]): list of new transactions
            proposer_wallet (Wallet object): voted proposer to append new block to blockchain

        Returns:
            Block object:  new Block instance
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

    @staticmethod
    def sign_block_hash(hash, wallet):
        """
        sign_block_hash signs passed hash value with given wallet

        Args:
            hash (Hash_ object): passed hash value
            wallet (Wallet object): wallet object signing the hash value 

        Returns:
            signature: signature
        """
        return wallet.sign_hash(hash)

    # TODO maybe just remake to a __dict__ function

    @staticmethod
    def block_content_to_json(timestamp, previous_hash, data):
        """block_content_to_json constructs json/dict from block's content

        Args:
            timestamp (String): date
            previous_hash (Hash object): hash pointing at the last block
            data ([Transaction objects list]): transactions

        Returns:
            dict : dict/json containing info about block
        """
        return {"timestamp": timestamp,
                "previous_hash": previous_hash.hexdigest(),
                "data": ChainUtils.transactionlist_to_json(data)}

    @staticmethod
    def block_hash(block):
        """block_hash calculate hash of Block object

        Args:
            block (Block): block object to calculate hash on

        Returns:
            Hash_ object: hash of the object
        """
        content = Block.block_content_to_json(
            block.timestamp, block.previous_hash, block.data)
        return ChainUtils.hash(content)

    def verify_block(self):
        """verifies block

        Returns:
            bool: True if valid block, else False
        """
        return ChainUtils.verify_signature(
            self.proposer,
            self.signature,
            Block.block_content_to_json(
                self.timestamp, self._previous_hash, self.data)
        )

    def verify_proposer(self, wallet: Wallet):
        """
        verify_proposer verifies if the block has been proposed by a given wallet

        Args:
            wallet (Wallet): wallet being verified

        Returns:
            bool: True if valid proposer, else False
        """
        return (self.proposer == wallet.verif_key)

    def search_by_process(self, process_id):
        """
        search_by_process looks for transaction containing given process_id

        Args:
            process_id (Str): string representation of the searched process_id

        Returns:
            Transaction: found Transaction or None
        """
        data = self.data.get_data()
        if data["process_id"] == process_id:
            return data
        else:
            return None
