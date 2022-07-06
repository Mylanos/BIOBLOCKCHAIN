from unicodedata import name
from bioblockchain.utils import TimeUtils, ChainUtils
from datetime import datetime
from json import dumps


# TODO daj bacha na tie prevody stringov a adries(wallet)
# TODO pridaj timestamp


class Transaction:
    """
     Transaction class is holding certain data with accompanying info needed for it's verification
    """
    def __init__(self, data, wallet):
        # id of the transaction for search 
        self.id = ChainUtils.id()
        # id of the operation
        self.operation_id = ChainUtils.id()
        # public key of the Transaction's sender 
        self.sender = wallet.verif_key
        # data
        self.payload = {"data": data, "timestamp": TimeUtils.my_date()}
        # hash of the data
        self.hash = ChainUtils.hash(dumps(self.payload))
        # signature of the data
        self.signature = wallet.sign_data(self.payload)

    def verify_transaction(self): 
        """verify_transaction verifies wether the transaction is valid

        Args:
            transaction ([type]): [description]

        Returns:
            [type]: [description]
        """
        return ChainUtils.verify_signature(self.sender, self.signature, self.payload)

    @property
    def hash_hexdigest(self):
        """
        hash_hexdigest is a property value of Transaction's hash in it's string representation

        Returns:
            Str: Hash representation of string
        """
        return self.hash.hexdigest()

    def toJSON(self):
        """transforms class variables into json/dict

        Returns:
            dict: dictionary from this transaction
        """
        content = {"id": self.id, "sender": ChainUtils.string_from_verifkey(self.sender), "payload": self.payload,
                   "hash": self.hash.hexdigest(), "signature": self.signature.hex()}
        return content
 
    def __str__(self) -> str:
        return (f"""
            Transaction
            From: {ChainUtils.string_from_verifkey(self.sender)}
            Payload: {self.payload}
            Hash: {self.hash}
            Signature: {self.signature.hex()}
        """)

    def get_data(self):
        """
        get_data returns data contained in Transaction

        Returns:
            Dict: dictionary with data
        """
        return self.payload["data"]
