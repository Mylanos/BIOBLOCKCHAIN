from bioblockchain.utils import TimeUtils, ChainUtils
from datetime import datetime
from json import dumps


# TODO daj bacha na tie prevody stringov a adries(wallet)

class Transaction:

    def __init__(self, data, wallet):
        self.id = ChainUtils.id()
        self.sender = wallet.verif_key
        self.payload = {"data": data, "timestamp": TimeUtils.my_date()}
        self.hash = ChainUtils.hash(dumps(self.payload))
        self.signature = wallet.sign(self.payload)

    # verifies wether the transaction is valid
    def verify_transaction(transaction):
        """test

        Args:
            transaction ([type]): [description]

        Returns:
            [type]: [description]
        """
        return ChainUtils.verify_signature(transaction.sender, transaction.signature, ChainUtils.hash(transaction.payload))

    # transforms class variables into json 
    def toJSON(self):
        content = {"id": self.id, "sender": ChainUtils.string_from_verifkey(self.sender), "payload": self.payload,
                   "hash": self.hash.hexdigest(), "signature": self.signature.hex()}
        # print("------- JSON ------")
        # print(self.id)
        # print(ChainUtils.string_from_verifkey(self.sender))
        # print(self.payload)
        # print(self.hash)
        # print(self.signature.hex())
        # print("------- JSON ------")
        return dumps(content)

    # prints formatted class 
    def __str__(self) -> str:
        return (f"""
        Transaction
        From: {ChainUtils.string_from_verifkey(self.sender)}
        Payload: {self.payload}
        Hash: {self.hash}
        Signature: {self.signature.hex()}
        """)
