from unicodedata import name
from bioblockchain.utils import TimeUtils, ChainUtils
from datetime import datetime
from json import dumps


# TODO daj bacha na tie prevody stringov a adries(wallet)
# TODO pridaj timestamp


class Transaction:
    """transaction holding certain data with all accompanying info
    """
    def __init__(self, data, wallet):
        self.id = ChainUtils.id()
        self.sender = wallet.verif_key
        self.payload = {"data": data, "timestamp": TimeUtils.my_date()}
        self.hash = ChainUtils.hash(dumps(self.payload))
        self.signature = wallet.sign_data(self.payload)
        
        """
        self.hash_hex = transaction.hash_hexdigest
        self.block_hash = transaction.hash
        self.public_key = wallet._verif_key
        self.content = {"block_hash": self.hash_hex, 
                        "public_key": wallet._verif_key}
        self.signature = wallet.sign(self.content)
        """

    # verifies wether the transaction is valid
    def verify_transaction(self):
        """verification of transaction

        Args:
            transaction ([type]): [description]

        Returns:
            [type]: [description]
        """
        return ChainUtils.verify_signature(self.sender, self.signature, self.payload)

    @property
    def hash_hexdigest(self):
        return self.hash.hexdigest()

    def toJSON(self):
        """transforms class variables into json/dict

        Returns:
            dict: dictionary from this transaction
        """
        content = {"id": self.id, "sender": ChainUtils.string_from_verifkey(self.sender), "payload": self.payload,
                   "hash": self.hash.hexdigest(), "signature": self.signature.hex()}
        return content

    def get_type(self):
        return self.payload["data"]["process_type"]
 
    def __str__(self) -> str:
        return (f"""
        Transaction
        From: {ChainUtils.string_from_verifkey(self.sender)}
        Payload: {self.payload}
        Hash: {self.hash}
        Signature: {self.signature.hex()}
        """)

    def get_data(self):
        return self.payload["data"]
