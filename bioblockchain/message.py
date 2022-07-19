from enum import Enum
import json
from bioblockchain.transaction import Transaction
from bioblockchain.block import Block
from bioblockchain.chain_utils import ChainUtils
from ecdsa.keys import BadSignatureError, BadDigestError

class PBFT_Message(str, Enum):
    """PBFT message types

    Args:
        str (str): string representation
        Enum (Enum): Enum inheritance
    """
    PRE_PREPARE = "PRE_PREPARE"
    REQUEST = "REQUEST"
    PREPARE = "PREPARE"
    COMMIT = "COMMIT"
    ROUND_CHANGE = "ROUND_CHANGE"
    REPLY = "REPLY"

class Message:
    """Object passed between nodes in peer-to-peer communication
    """
    def __init__(self, ttype=None, sender=None, content=None):
        self.ttype = ttype
        self.sender = sender            
        self.content = content
        self.timestamp = "12.07.1999"
        self.hash = ChainUtils.hash(self.toJSON()).digest()
        self.signature = sender.wallet.sign(self.hash)

    def toJSON(self):
        """custom object to json conversion

        Returns:
            dict: json/dict object 
        """
        dictionary = {}
        if self.ttype == PBFT_Message.REQUEST:
            dictionary = {"ttype": json.dumps(self.ttype)}
            if isinstance(self.content["consensus_object"], Transaction):
                biom = self.content["biometrics"]
                tx = self.content["consensus_object"]
                dictionary["content"] = {"consensus_object": tx.toJSON(), "biometrics": biom}
            elif isinstance(self.content["consensus_object"], Block):
                block = self.content["consensus_object"]
                dictionary["content"] = Block.block_content_to_json(block.timestamp, block.previous_hash, block.data)
            else: 
                dictionary["content"] = self.content               
            dictionary["sender"] = ChainUtils.string_from_verifkey(self.sender.wallet.verif_key)
            dictionary["timestamp"] = self.timestamp
        return dictionary

    def verify(self):
        """verifies message

        Returns:
            bool: True if valid, else False
        """
        hash = ChainUtils.hash(self.toJSON()).digest()
        try:
            public_key = self.sender.wallet.verif_key
            public_key.verify_digest(self.signature, hash)
            return True
        except (BadSignatureError, BadDigestError) as error:
            print(error)
            #TODO MISSING RAISE HANDLING?????
            return False

class MessageLogged:
    """Single log stored in a node for given message
    """
    def __init__(self, message, weight):
        self.msg_hash = ChainUtils.hash(message.toJSON()).digest()
        self.message = message
        self.prepare_count = weight
        self.commit_count = 0
        self.reply_count_agree = 0
        self.reply_count_disagree = 0
        self.prepare_flag = False
        self.commit_flag = False
        self.reply_flag = False
        self.disagreement = False
        self.disagreement_solution = None
        self.reply_operation_executed = False
        self.commit_sent = False
        self.reply_sent = False
        self.view_num = None
        self.seq_num = None

    def update_nums(self, view_num, seq_num):
        """
        update_nums updates view and sequence number of PBFT protocol

        Args:
            view_num (Int): current view number
            seq_num (Int): current sequence number
        """
        self.view_num = view_num
        self.seq_num = seq_num
    
    def __str__(self) -> str:
        return (f"""
- MessageLog
Hash: {self.msg_hash}
Message: {self.message.toJSON()}
Prepares: {self.prepare_count}
ViewNum: {self.view_num}
SeqNum: {self.view_num}
        """)
