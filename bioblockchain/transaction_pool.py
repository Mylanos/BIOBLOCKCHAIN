from time import sleep
from bioblockchain.config import TRANSACTION_THRESHOLD
from bioblockchain.transaction import Transaction
"""
TransactionPool class stores all transactions received from other nodes.
"""

class TransactionPool:

    def __init__(self) -> None:
        self.transactions = []

    def add_transaction(self, transaction):
        print("Adding TRANSACTION to the TRANSACTION POOL!")
        #sleep(0.7)
        self.transactions.append(transaction)

    def verify_transaction(self, transaction: Transaction):
        return transaction.verify_transaction()

    def _find(self, transaction: Transaction):
        return [t for t in self.transactions if t.id == transaction.id]
        
    def clear(self):
        print("Clearing TRANSACTION POOL!")
        self.transactions = []

    def filled(self):
        if len(self.transactions) < TRANSACTION_THRESHOLD:
            return False
        return True