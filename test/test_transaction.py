import unittest
from bioblockchain.wallet import Wallet
from bioblockchain.transaction import Transaction

class TransactionTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.wallet1 = Wallet("Wallet1's Super Secret Phrase")
        self.wallet2 = Wallet("Wallet2's Super Secret Phrase")
        self.tx1 = Transaction("Stephan just entered room E104", self.wallet1)

    def test_transaction_valid_data(self):
        self.assertEqual(self.tx1.verify_transaction(), True)
        #print(tx1.toJSON())

    def test_transaction_modified_data(self):
        self.tx1.payload = {}
        self.assertEqual(self.tx1.verify_transaction(), False)