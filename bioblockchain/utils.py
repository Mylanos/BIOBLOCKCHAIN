from hashlib import sha256
import json
from os import stat
from uuid import uuid1
from ecdsa import NIST256p, SigningKey, NIST384p, util
from ecdsa.keys import BadSignatureError
from ecdsa.util import randrange_from_seed__trytryagain, sigdecode_string
from datetime import datetime
from pickle import dumps

#TODO redo the verification of tx/wallet/blocks to signing the hashes instead of the data

class TimeUtils:
    """
     TimeUtils contains static methods for time operations
    """
    @staticmethod
    def my_date():
        """
        my_date returns current date in given format

        Returns:
            _type_: _description_
        """
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


class ChainUtils:
    """
    ChainUtils contains static methods for cryptographic operations and operations with blockchain

    Raises:
        ValueError: Raised when passed arguments to verify_signature are of wrong type 
        BadSignatureError: Raised in verify_signature when the signature is wrong
    """
    
    @staticmethod
    def transactionlist_to_json(tx_list):
        """
        transactionlist_to_json converts Transaction objects to list of dictionaries(json)

        Args:
            tx_list (List or Transaction): list of transactions or single Transaction

        Returns:
            List: list of dictionaries
        """
        json_list = []
        if isinstance(tx_list, list):
            json_list = [tx.toJSON() for tx in tx_list]
        else:
            json_list = [tx_list.toJSON()]
        return json_list

    @staticmethod
    def id():
        """generates UUID(universally unique identifier)

        Returns:
            string]: generated UUID
        """
        return str(uuid1())

    @staticmethod
    def generate_key_from_seed(seed):
        """generates private key from secret phrase

        Args:
            seed (string): secret phrase

        Returns:
            SigningKey: private key generated from `seed`
        """
        secexp = randrange_from_seed__trytryagain(seed, NIST256p.order)
        sk = SigningKey.from_secret_exponent(secexp, NIST256p)
        return sk

    @staticmethod
    def hash(data_to_hash: str):
        """sha256 hashing function

        Args:
            string_to_hash (str | dict): string/dict to be hashed

        Returns:
            (_Hash object): object representing calculated hash from given `string_to_hash`
        """
        if (isinstance(data_to_hash, dict)):
            data = dumps(data_to_hash)
        else:
            data = data_to_hash.encode('utf-8')
        #encoded_string = string_to_hash.encode('utf-8')
        return sha256(data)

    @staticmethod
    def verify_signature(public_key, signature, data):
        """verifies validity of signature

        Args:
            public_key (VerifyingKey): public key associated with `signature`
            signature (Bytes): encoded signature over `data`
            data (String): data which was used for signature calculation

        Returns:
            Bool: True when the signature is valid, False otherwise
        """

        if not (isinstance(data, str) or  isinstance(data, dict)):
            raise ValueError('Need a dict or string, got {0!r}'.format(data))
        try:
            data_bytes = dumps(data)
            public_key.verify(signature, data_bytes, hashfunc=sha256)
            return True
        except BadSignatureError as e:
            raise BadSignatureError('Signature is not valid!')

    @staticmethod
    def string_from_verifkey(verifying_key):
        """turns bytes like public key, to its string representation

        Args:
            verifying_key ([Bytes]): [public key]

        Returns:
            String: public key's string representation
        """
        return verifying_key.to_string().hex()
