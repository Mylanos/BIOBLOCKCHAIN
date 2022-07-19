import binascii
import hashlib
import unittest
from bioblockchain.wallet import Wallet
from bioblockchain.chain_utils import ChainUtils
from json import dumps

class WalletTestCase(unittest.TestCase):
    def setUp(self):
        self.secret_phrase = "Super Secret Phrase"
        self.wallet = Wallet(self.secret_phrase)
        self.data = {"some": "Data"}

    def test_generated_keys(self):
        self.assertEqual(self.wallet.private_key,
                         ChainUtils.generate_key_from_seed(self.secret_phrase))

    # tests the signing, hashing and veryfing functionality of Wallet class of a random data
    def test_wallet_signing(self):
        signature = self.wallet.sign(self.data)
        signature_bad = self.wallet.sign({"bad": "data"})

        # valid signature
        self.assertTrue(ChainUtils.verify_signature(self.wallet.verif_key, signature,
                        self.data), "'verify_signature' raised an unexpected exception!")

        # invalid data
        self.assertFalse(ChainUtils.verify_signature(self.wallet.verif_key, signature, {
                         "data": 3}), "'verify_signature' dindnt raise exception on invalid data!")

        # bad signature
        self.assertFalse(ChainUtils.verify_signature(self.wallet.verif_key, signature_bad,
                         self.data), "'verify_signature' dindnt raise exception on bad signature!")

    def test_wallet_transactions(self):
        alice = Wallet("Alice's Super Secret Phrase")
        bob = Wallet("Bob's Super Secret Phrase")
        data = {"data": 42}

        # todo possible future test case
        #alice.create_transaction()



if __name__ == "__main__":
    unittest.main()

