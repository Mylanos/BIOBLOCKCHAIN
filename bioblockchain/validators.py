from typing import List
from bioblockchain.wallet import Wallet

"""
PBFT is a permissioned blockchain consensus algorithm so its needed to store the address of all the nodes in each nodes system. 
There are two posibilities how to store them
    1. Manually by choosing a secret, creating a wallet, getting its public key and storing it into a file and when project is run it reads this file for keys.
    2. Automatically for demonstration purposes, by creating a class and adding a function that can return a list of public keys of N number of nodes.
Validator class generates a list of public keys known to every node. In this project, we have used the secret phrase for each node as XYZ......
This way it would be easier for us to make a list of public keys and create the nodes from the command line with the same public key.
"""

class Validators:

    def __init__(self, validators_count):
        self._list = Validators.generate_validators(validators_count)
    
    @staticmethod
    def generate_validators(count):
        list = []
        for i in range(count):
            # TODO secret phrase should never be made public
            list.append(Wallet("NODE" + str(i)))
        return list

    def is_valid(self, validator_pk):
        for val in self._list:
            if val._verif_key == validator_pk:
                return True
        return False

    def __str__(self) -> str:
        validators = ''.join("%s\n" % x for x in self._list)
        return "***LIST OF VALIDATORS***\n" + validators

    """ Returns the Iterator object """
    def __iter__(self):
        return ValidatorsIterator(self)

    def __getitem__(self, index):
        return self._list[index]


#TODO inheritance from list may aswell do the job
class ValidatorsIterator:
    def __init__(self, matchers) -> None:
        self._matchers = matchers
        self._index = 0

    """ Returns the next value from team object's lists """ 
    def __next__(self):
        if self._index < (len(self._matchers._list)) :
            result = self._matchers._list[self._index]
            self._index +=1
            return result
        # End of Iteration
        raise StopIteration