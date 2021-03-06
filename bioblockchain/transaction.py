from bioblockchain.chain_utils import ChainUtils
from bioblockchain.time_utils import TimeUtils
from json import dumps


class Transaction:
    """
     Transaction class is holding certain data with accompanying info needed for it's verification
    """

    def __init__(self, data, wallet):
        # id of the transaction for search
        self.id = ChainUtils.id()
        # timestamp
        self.timestamp = TimeUtils.my_date()
        # public key of the Transaction's sender
        self.sender = wallet.verif_key
        # data with unique id of this transaction and timestamp
        self.payload = {"tx_id": self.id,
                        "data": data,
                        "timestamp": self.timestamp}
        # hash of the data
        self.hash = ChainUtils.hash(dumps(self.payload))
        # signature of the data
        self.signature = wallet.sign(self.payload)

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
    ID: {self.id}
    From: {ChainUtils.string_from_verifkey(self.sender)}
    Payload: {dumps(self.payload, sort_keys=True, indent=4)}
    Timestamp: {self.timestamp}
    Hash: {self.hash.hexdigest()}
    Signature: {self.signature.hex()}""")

    def get_data(self):
        """
        get_data returns data contained in Transaction

        Returns:
            Dict: dictionary with data
        """
        return self.payload["data"]

    def update_transaction(self, data, node):
        self.payload["data"] = data
        self.hash = ChainUtils.hash(dumps(self.payload))
        # signature of the data
        self.signature = node.sign(self.payload)
