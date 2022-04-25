import unittest
from bioblockchain.wallet import Wallet
from bioblockchain.block import Block
from bioblockchain.transaction import Transaction

class BlockTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.wallet1 = Wallet("Wallet1's Super Secret Phrase")
        self.wallet2 = Wallet("Wallet2's Super Secret Phrase")
        self.tx1 = Transaction("Stephan just entered room E104", self.wallet1)
        self.block1 = Block.create_block(Block.genesis(), [self.tx1], self.wallet2)

    def test_block_valid_data(self):
        self.assertEqual(self.block1.verify_block(), True)
        #print(tx1.toJSON())

    def test_block_modified_data(self):
        self.block1.data = []
        self.assertEqual(self.block1.verify_block(), False)

    def test_block_valid_proposer(self):
        self.assertEqual(self.block1.verify_proposer(self.wallet2), True)

    def test_block_valid_block(self):
        self.assertEqual(self.block1.verify_block(), True)
    
    def test_block_modified_block(self):
        self.block1.data = []
        self.assertEqual(self.block1.verify_block(), False)