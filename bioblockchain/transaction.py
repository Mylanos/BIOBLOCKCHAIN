from bioblockchain.utils import TimeUtils, ChainUtils
from datetime import datetime
from json import dumps


# TODO daj bacha na tie prevody stringov a adries(wallet)
# TODO Uprav túto triedu pre účely bakalarskej prace
# TODO skontroluj co je treba podpisovat ci ten content alebo uz len hash z contentu
"""

"""

class Transaction:

    def __init__(self, data, wallet):
        self.id = ChainUtils.id()
        self.sender = wallet.verif_key
        self.payload = {"data": data, "timestamp": TimeUtils.my_date()}
        self.hash = ChainUtils.hash(dumps(self.payload))
        self.signature = wallet.sign(self.payload)

    # verifies wether the transaction is valid
    def verify_transaction(self):
        """test

        Args:
            transaction ([type]): [description]

        Returns:
            [type]: [description]
        """
        return ChainUtils.verify_signature(self.sender, self.signature, self.payload)

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
        return content

    # prints formatted class 
    def __str__(self) -> str:
        return (f"""
        Transaction
        From: {ChainUtils.string_from_verifkey(self.sender)}
        Payload: {self.payload}
        Hash: {self.hash}
        Signature: {self.signature.hex()}
        """)
