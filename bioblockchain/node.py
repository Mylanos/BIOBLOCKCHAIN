from enum import Enum
from hashlib import blake2b
import bioblockchain.config as config
import random, string
from bioblockchain.message import MessageLogged
from bioblockchain.utils import ChainUtils
from bioblockchain.wallet import Wallet
from json import dumps

class Biometric_Processes(str, Enum):
    ENROLLMENT = "enrollment"
    VERIFICATION = "verification"

class Node:
    def __init__(self, node_num, storage, users):
        self.template_storage = storage
        self.id = node_num
        self.wallet = Wallet(f"NODE {node_num}")
        self.request_log = []
        self.transaction_pool = []
        self.users = users
        self.request_sequence_num = 0
        #TODO figure out how the views are represented
        self.current_view = 0
        self.prepare_count = 0
        self.commit_count = 0
        self.reply_count = 0
        self.prepare_flag = False
        self.commit_flag = False
        self.reply_flag = False
        self.commit_sent = False
        self.reply_sent = False
        
    def matcher(self, data):
        # reference_data = self.__get_feature_from_storage()
        if self.feature_in_database(data):
            raise Exception("Features were already enrolled: Operation forbidden!")
        data["markant"] = data
        data["extraction_timestamp"] = "12.07.1999"
        return data

    def feature_in_database(self, features):
        if features in self.template_storage.values():
            return True
        return False

    def add_request_to_log(self, message):
        log = self.search_log_msghash(message.hash)
        # redundant request message
        if not log:
            self.request_log.append(MessageLogged(message=message))
        else:
            #TODO change this error handling
            print(f"Request from the same message was already in the Node{self.id}'s log!")
            exit(1)
        return self.request_log[-1].msg_hash

    def corresponding_view_seq(self, view, seq):
        # TODO somehow check for the valid sequence number
        return True

    #TODO handling of repetitive sets of numbers or numbers out of valid range
    def set_seq_number(self, message_hash):
        # assigning next available sequence number
        log = self.search_log_msghash(message_hash)
        if log:
            log.update_nums(self.current_view, self.request_sequence_num)
            self.request_sequence_num += 1
        else:
            #TODO change this error handling
            print("Requested to set view and sequence number for brand new message!")
            exit(1)
        return self.current_view, self.request_sequence_num - 1

    def search_log_msg(self, message):
        for entry in self.request_log:
            if entry.msg_hash == message.hash:
                return entry
        return None


    def search_log_msghash(self, message_hash):
        """search message in log of request messages 

        Args:
            message_hash (bytes): hash representation of searched message

        Returns:
            Message object: Succesful search of message
            None: Failed search
        """
        for entry in self.request_log:
            if entry.msg_hash == message_hash:
                return entry
        return None
    
    def get_feature_from_storage(self):
        pass   
    
    def store_features(self, features):
        new_user = Wallet(''.join(random.choices(string.ascii_letters + string.digits, k=10)))
        self.users.append(new_user)
        new_user_pub_key = ChainUtils.string_from_verifkey(new_user.verif_key)
        self.template_storage[new_user_pub_key] = features

    def get_sensor_data(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    def extract(self, data):
        h = blake2b(digest_size=20)
        h.update(bytes(data, encoding='utf8'))
        features = h.hexdigest()
        return features

    def feature_extractor(self, data_sensory, process_type):
        # provisional feature extraction
        features = self.extract(data_sensory)
        data = {}
        if self.feature_in_database(features) and process_type == Biometric_Processes.ENROLLMENT:
            raise Exception("Features were already enrolled: Operation forbidden!")
        data["sensor_data"] = data_sensory
        data["features"] = features
        data["extraction_timestamp"] = "12.07.1999"
        data["process_type"] = dumps(process_type)

        return data

    def add_transaction(self, transaction):
        self.transaction_pool.append(transaction)

    def compare_features(self, features1, features2):
        return True

    def verify_decision(self, transaction):
        self.add_transaction(transaction)
        data = transaction.get_data()
        features = self.extract(data["sensor_data"])
        if self.compare_features(features, data["features"]):
            return True
        else:
            return False

    # TODO watchout for unsuccesful search, might cause errors 
    async def received_prepare(self, msg_hash):
        log = self.search_log_msghash(msg_hash)
        log.prepare_count += 1   
        if log.prepare_count >= config.MIN_PREPARE:
            log.prepare_flag = True
        return log
    
    async def received_reply(self, msg_hash):
        log = self.search_log_msghash(msg_hash)
        self.reply_count += 1   
        if self.reply_count >= config.MIN_REPLY:
            self.reply_flag = True 
        return self
    
    async def received_commit(self, msg_hash):
        log = self.search_log_msghash(msg_hash)
        log.commit_count += 1   
        if log.commit_count >= config.MIN_COMMIT:
            log.commit_flag = True
        return log

    def get_other_nodes(self, nodes):
        if self in nodes:
            others = nodes.copy()
            others.remove(self)
            return others
        else:
            return nodes