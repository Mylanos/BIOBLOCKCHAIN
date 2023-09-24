
from hashlib import sha256
from bioblockchain.chain_utils import ChainUtils
from bioblockchain.transaction import Transaction
from pickle import dumps


class Wallet:
    """ The wallet holds the public key and key pair. 
        It is also responsible for signing data hashes and creating signed transactions, messages...
    """

    def __init__(self, secret):
        self._private_key = ChainUtils.generate_key_from_seed(secret)
        self._verif_key = self.private_key.get_verifying_key()

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
        if isinstance(data, bytes):
            return self.private_key.sign_digest_deterministic(data)
        if isinstance(data, str) or isinstance(data, dict):
            #data_b = ChainUtils.hash(data)
            data_bytes = dumps(data)
            return self.private_key.sign_deterministic(data_bytes, hashfunc=sha256)
        else:
            raise ValueError(
                f'Signing function of Wallet class got unexpected data type({type(data)}).')

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
        """
        private_key property contains private or SigningKey property

        Returns:
            SigningKey: private key of given wallet
        """
        return self._private_key

    @private_key.setter
    def private_key(self, key):
        """
        private_key setter of property that contains private or SigningKey property

        Args:
            key (SigningKey object): assigned key 
        """
        self._private_key = key

    @property
    def verif_key(self):
        """
        verif_key property contains public or VerifyingKey property

        Returns:
            VerifyingKey: public key of given wallet
        """
        return self._verif_key

    @verif_key.setter
    def verif_key(self, key):
        """
        verif_key setter of property that contains private or VerifyingKey property

        Args:
            key (VerifyingKey object): assigned key 
        """
        self._verif_key = key
