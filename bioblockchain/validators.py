from typing import List
from bioblockchain.wallet import Wallet

class Validators:

    def __init__(self, validators_count):
        self._list = Validators.generate_validators(validators_count)
    
    @staticmethod
    def generate_validators(count):
        list = []
        for i in range(count):
            list.append(Wallet("NODE" + str(i)))
        return list

    def is_valid(self, node):
        return node in self._list

    def __str__(self) -> str:
        validators = ''.join("%s\n" % x for x in self._list)
        return "***LIST OF VALIDATORS***\n" + validators