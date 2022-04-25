from enum import Enum
from random import randint
from time import sleep
from bioblockchain.blockchain import Blockchain
from bioblockchain.wallet import Wallet
from bioblockchain.transaction import Transaction
from bioblockchain.transaction_pool import TransactionPool
from bioblockchain.prepare_pool import PreparePool
from bioblockchain.message_pool import MessagePool
from bioblockchain.block_pool import BlockPool
from bioblockchain.validators import Validators

import bioblockchain.config as config

# message type enumeration


class PBFT_Message(Enum):
    PRE_PREPARE = 1
    TRANSACTION = 2
    PREPARE = 3
    COMMIT = 4
    ROUND_CHANGE = 5

class Biometric_Processes(Enum):
    ENROLLMENT = 1
    VERIFICATION = 2


class Message:
    def __init__(self, ttype=None, addressee=None, block=None, transaction=None, content=None, prepare=None):
        self.ttype = ttype
        self.block = block
        self.transaction = transaction
        self.addressee = addressee
        self.prepare = prepare

class BioBlockchain():

    def __init__(self, blockchain, pbft):
        self.blockchain = blockchain
        self.process_type = None
        self.pbft = pbft
        self.matchers = Validators(config.NUMBER_OF_NODES)


    # or search not sure
    def __get_feature_from_storage(self):
        pass

    def __matcher(self, data):
        # reference_data = self.__get_feature_from_storage()
        if data["markant"] == "o482-4JfQ-fsCf-saWf-aqSf-dsff":
            return True
        return False

    def __get_sensor_data(self):
        return {"id": 4324,
                "content": "osjf-fsafsaf-asdfdsf-sff"}

    def __feature_extraction(self, data):
        data["markant"] = "o482-4JfQ-fsCf-saWf-aqSf-dsff"
        data["extraction_timestamp"] = "12.07.1999"
        return data

    def run_enrollment(self):
        print("*\tReceived request for enrollment!")
        print("processing the data...")
        data_sensory = self.__get_sensor_data()
        data = self.__feature_extraction(data_sensory)
        data["process_type"] = "enrollment"
        self.pbft.validate_decision(data)

        print("*\tYayyy")
        print(print(f"*****************************************************************************************************************************************"))

    def run_verification(self):
        pass

    # TODO do special kind of choosing of the next proposer - based on reputation?
    # currently just randomized
    def get_proposer(self):
        index = randint(0, 1000) % config.NUMBER_OF_NODES
        return self.matchers[2]

class PBFT:

    def __init__(self, blockchain, wallet, block_pool, prepare_pool, message_pool, transaction_pool):
        self.blockchain = blockchain
        self.wallet = wallet
        self.block_pool = block_pool
        self.prepare_pool = prepare_pool
        self.transaction_pool = transaction_pool
        #self.commit_pool = commit_pool
        self.message_pool = message_pool

    #idk some how do the voting
    def set_leader(self, leader):
        self.wallet = self.blockchain.get_proposer()

    # broadcasts transactions
    def validate_decision(self, data):
        print(f"\n*************************************************************VALIDATION*************************************************************")
        print("Creating Transaction for new PBFT request!")
        transaction = Transaction(data, self.wallet)
        message = Message(PBFT_Message.TRANSACTION, self.wallet, transaction=transaction)
        self.message_handler(message)

    def broadcast_pre_prepare(self, block):
        print("\n")
        print(f"************************************************PRE-PREPARE************************************************")
        # print(f"************************PRE-PREPARE for block({block.hash_hexdigest})************************")

        for validator in self.blockchain.matchers:
            message = Message(PBFT_Message.PRE_PREPARE, validator, block=block)
            self.message_handler(message)

    def broadcast_prepare(self, prepare):
        print("\n")
        print(f"************************************************PREPARE************************************************")
        for validator in self.blockchain.matchers:
            message = Message(PBFT_Message.PREPARE, validator, prepare=prepare)
            self.message_handler(message)

    def broadcast_commit(self):
        print("\n")
        print(f"************************************************COMMIT************************************************")
        exit(1)
        for validator in self.blockchain.matchers:
            self.message_handler(f"Validator{validator} received COMMIT message")

    def broadcast_round_change(self):
        print(f"************************************************ROUND-CHANGE************************************************")
        for validator in self.blockchain.matchers:
           self.message_handler(
                f"Validator{validator} received ROUND-CHANGE message")

    # TODO maybe some other class for matcher functionality or put it somewhere else
    def check_match(self):
        return True

    def message_handler(self, message):
        print(f'Processed by validator with {message.addressee}')

        # check if the language is correct
        if message.ttype == PBFT_Message.TRANSACTION:
            print("Validating...")
            if (not self.transaction_pool._find(message.transaction) and message.transaction.verify_transaction() and self.blockchain.matchers.is_valid(self.wallet._verif_key)):
                
                print(
                    f"TRANSACTION has been validated: New TRANSACTION added to the pool!")
                self.transaction_pool.add_transaction(message.transaction)
                if self.transaction_pool.filled():
                    print("Transaction pool THRESHOLD reached: ready to propose new BLOCK!")
                    # if the current node is the proposer he creates a new block and proposes it
                    if self.blockchain.get_proposer() == self.wallet:
                        print("Validated proposer: proposing new BLOCK!")
                        new_block = self.blockchain.create_block(
                            self.transaction_pool.transactions, self.wallet)
                        self.block_pool.add_block(new_block)
                        print(f"*************************************************************TRANSACTION*************************************************************")
                        self.broadcast_pre_prepare(new_block)
                else:
                    print(
                        f"************************************************TRANSACTION************************************************")
            else:
                print("Unsuccesfull validation!")
        elif message.ttype == PBFT_Message.PRE_PREPARE:
            if (not self.block_pool.exists(message.block) and self.blockchain.is_valid_block(message.block)):
                print("Received BLOCK is valid! Ready to append to the pool.")
                self.block_pool.add_block(message.block)
                # self.broadcast_pre_prepare(data.block) <-- not sure about this
                print(f"New BLOCK added to the pool!")
                prepare = self.prepare_pool.prepare(message.block, self.wallet)
                self.broadcast_prepare(prepare)
        elif message.ttype == PBFT_Message.PREPARE:
            if (not self.prepare_pool.find_prepare(message.prepare) and self.prepare_pool.is_valid(message.prepare) and self.blockchain.matchers.is_valid(message.prepare.public_key)):
                print("Prepare message is valid! Ready to append to the pool.")
                self.prepare_pool.add_prepare(message.prepare)
                print(f"New PREPARE message added to the pool!")
                # self.broadcast_prepare(message.prepare)

                if len(self.prepare_pool.prepares) >= config.MIN_APPROVALS:
                    self.broadcast_commit()




if __name__ == "__main__":

    transaction_pool = TransactionPool()
    blockchain = Blockchain()
    block_pool = BlockPool()
    prepare_pool = PreparePool()
    # commitPool = CommitPool();
    message_pool = MessagePool()

    # TODO the chosen proposer is at the first index right now, (hard coded), the proposer makes problems when chosen different index
    pbft = PBFT(blockchain,
                blockchain.matchers[2], block_pool, prepare_pool, message_pool, transaction_pool)

    bio_blockchain = BioBlockchain(blockchain, pbft)

    bio_blockchain.run_enrollment()


"""
Môj thougth process

Takže spravit funkciu ktora bude len simulovať požiadavok na jednu z komponent(nebude sa vytvarať žiadna transakcia pre požiadavok). Tento požiadavok pôjde z nodu ktorý bude reprezentovať
a sprostredkovávať matcher.
Po prijatí požiadavku daný node danej komponenty vytvorí novú transakciu tvorenú contentom markantov, id daného nodu(validatora) a výsledok(True/False u Matchera) uklada transaction
do local poolu transakcii
Broadcast transakcie - preprepare. Po prijatí pre_prepare správy overí transakciu(prijimatel, či ju už nemá v poole a či odosielateľ je korekt validator). Ak rozhodne a nenastane žiadna chyba pri prenose odosiela 
spravu Prepare všetkym ostatnym nodom v sieti.

"""

"""
node is considered prepared when it has seen request from the primary node, has pre-prepared and has seen 2f prepare messages that matches pre-prepare(looking for 2f+1 prepares)
when nodes are prepared they sent commit message, if a node has seen f+1 valid commit messages, they carry out the client request and sendout a reply to the client
"""

"""
    data = {"id": 1234,
            "room-entered": "E104",
            "verificated": True,
            "entered-by": "Alice"}

    data2 = {"id": 3434,
             "room-entered": "E105",
             "verificated": False,
             "entered-by": "Alice"}

    data3 = {"id": 3714,
             "room-entered": "D105",
             "verificated": True,
             "entered-by": "Stephan"}

    data4 = {"id": 9834,
             "room-entered": "D105",
             "verificated": False,
             "entered-by": "Stephan"}

    data5 = {"id": 4324,
             "content": "osjf-fsafsaf-asdfdsf-sff",
             "req_type": "match",
             "req-by": "node_xyz"}
"""