import unittest
from bioblockchain.wallet import Wallet
from bioblockchain.transaction import Transaction

class TransactionTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.wallet1 = Wallet("Wallet1's Super Secret Phrase")
        self.wallet2 = Wallet("Wallet2's Super Secret Phrase")

    def test_transaction_creation(self):
        tx1 = Transaction("Stephan just entered room E104", stephan)
        self.assertEqual(True, True)