from hashlib import sha256
from os import truncate
from ecdsa.ecdsa import Private_key
from bioblockchain.utils import ChainUtils
from bioblockchain.transaction import Transaction
from pickle import dumps

"""
The wallet holds the public key and key pair. 
It is also responsible for signing data hashes and creating signed transactions.
"""

class Wallet:
    def __init__(self, secret):
        self.secret = secret
        self._private_key = ChainUtils.generate_key_from_seed(self.secret)
        self._verif_key = self.private_key.get_verifying_key()

    def __eq__(self, __o: object) -> bool:
        #TODO secrets should probably be handled differently
        if (isinstance(__o, Wallet)):
            return self.secret == __o.secret and self._private_key == __o._private_key
        return False

    def __str__(self) -> str:
        return (f"Wallet - Public Key: {ChainUtils.string_from_verifkey(self.verif_key)}")

    def sign(self, data):
        """calculates signature over given data

        Args:
            data (Dict|String|Bytes): [data to be signed]

        Raises:
            ValueError: Passed unexpected argument type

        Returns:
            (String): encoded signature over `data`
        """
        if isinstance(data, str) or isinstance(data, dict) or isinstance(data, bytes):
            #data_b = ChainUtils.hash(data)
            data_bytes = dumps(data)
            return self.private_key.sign_deterministic(data_bytes, hashfunc=sha256)
        else:
            raise ValueError(
                "Signing function of Wallet class expected string or dict type argument.")

    def create_transaction(self, data):
        """ creates transaction

        Args:
            data (Dict): transaction payload

        Returns:
            (Transaction object): [object representing transaction]
        """
        return Transaction(data, self)

    @property
    def private_key(self):
        return self._private_key

    @private_key.setter
    def private_key(self, key):
        self._private_key = key

    @property
    def verif_key(self):
        return self._verif_key

    @verif_key.setter
    def verif_key(self, key):
        self._verif_key = key
