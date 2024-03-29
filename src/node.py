
from enum import Enum
from hashlib import md5
import bioblockchain.config as config
import random
import string
from bioblockchain.message_log import MessageLogged
from bioblockchain.chain_utils import ChainUtils
from bioblockchain.wallet import Wallet
from colorama import Back, Fore, Style
from bioblockchain.transaction import Transaction
from bioblockchain.block import Block


class Biometric_Processes(str, Enum):
    """processes in biometric systems

    Args:
        str (str): string representation 
        Enum (): Enum inheritance
    """
    ENROLLMENT = "enrollment"
    VERIFICATION = "verification"
    IDENTIFICATION = "identification"


class Node:
    """single node participating in the peer-2-peer network
    """

    def __init__(self, node_num, storage, users, blockchain, weight):
        # reference to storage
        self.template_storage = storage
        # nodes ID
        self.id = node_num
        # wallet keypair for given Node
        self.wallet = Wallet(f"NODE {node_num}")
        # reference to blockchain
        self.blockchain = blockchain
        # request log containing received request messages
        self.request_log = []
        # list containing processed transactions
        self.transaction_pool = []
        # list of enrolled users wallets
        self.users = users
        # sequence number of received requests
        self.request_sequence_num = 0
        self.current_view = 0
        # malfunctionous node always returns YES/NO
        self.always_true = False
        self.always_false = False
        # weight of the node
        self.weight = weight
        # compromised feature extractor
        self.compromised_extraction = False
        # compromised matcher
        self.compromised_matching = False

    def matcher(self, features, mode, claimed_identity, process_id):
        """
        matcher operates as the matcher component that is proposing the operation to the network

        Args:
            features (Str):  representation of extracted features
            mode (Str): mode of operation(either identification or verification)
            claimed_identity (Str): identifier of the claimed identity
            process_id (Str): process identifier for given operation
            compromised (Bool): flag used for compromised node simulation (proposing wrong match result)

        Returns:
            Dict: dictionary containing all the operational data and outcome of matching
        """
        data = {}
        data["operation"] = "Matching"
        data["process_id"] = process_id
        data["approached_node"] = f"NODE{self.id}"
        if mode == Biometric_Processes.IDENTIFICATION:
            # search is made by 1:M comparison, in real world scenario templates/biometrics wouldnt be perfectly same
            result = self.features_in_database(features)
            data["process_type"] = "identification"
            data["match_timestamp"] = "12.07.1999"

            if result:
                data["user"] = result
                data["score"] = 87
                data["success"] = True
            else:
                data["user"] = None
                data["success"] = False
                data["score"] = 23
        if mode == Biometric_Processes.VERIFICATION:
            # search is made by 1:1 comparison, in real world scenario templates/biometrics wouldnt be perfectly same
            result = self.claimed_identity_in_database(
                features, claimed_identity)
            data["process_type"] = "verification"
            data["claimed_identity"] = claimed_identity
            data["match_timestamp"] = "12.07.1999"

            if result:
                data["user"] = result
                # maybe do custom scores
                data["score"] = 87
                data["success"] = True
            else:
                data["user"] = None
                data["success"] = False
                data["score"] = 23

        return data

    def features_in_database(self, features):
        """
        features_in_database method searches for a given feature in the whole database of templates(1:M search)

        Args:
            features (str):  string representation of feature

        Returns:
            str: found key/identifier for given features/user or None
        """
        if self.compromised_matching:
            return "Some artificially chosen user that happens to be in the system"
        for key, feature in self.template_storage.items():
            if features == feature:
                return key
        return None

    def claimed_identity_in_database(self, features, claimed_identity):
        """
        claimed_identity_in_database method validates if given feature is stored in the template database in form of claimed identity(1:1 search)

        Args:
            features (Str): string representation of acquired features
            claimed_identity (str): string representation of the claimed identity

        Returns:
            Str: string representation of found user's key/identifier or None
        """
        # search for claimed user in DB
        search_result = self.search_user_in_database(claimed_identity)
        if self.compromised_matching:
            return claimed_identity
        if search_result:
            # compare features of the user found by claimed_identity
            if self.template_storage[search_result] == features:
                return search_result
        return None

    def add_request_to_log(self, message):
        """store a newly received request

        Args:
            message (Message Object): request message object

        Returns:
            Str: hash representation of found message
        """
        log = self.search_log_msghash(message.hash)
        # redundant request message
        if not log:
            self.request_log.append(MessageLogged(
                message=message, weight=self.weight))
        else:
            print(
                f"Request from the same message was already in the Node{self.id}'s log!")
            exit(1)
        return self.request_log[-1].msg_hash

    def corresponding_view_seq(self, view, seq):
        """
        corresponding_view_seq check for valid sequence and view number

        Args:
            view (int): current view number of pbft
            seq (int): current sequence number of pbft

        Returns:
            Bool: true
        """
        return True

    def set_seq_number(self, message_hash):
        """
        set_seq_number assign next available sequence number to the request

        Args:
            message_hash (str): hash of the request message

        Returns:
            Tuple: sequence and view number that was assigned to the request
        """
        # assigning next available sequence number
        log = self.search_log_msghash(message_hash)
        if log:
            log.update_nums(self.current_view, self.request_sequence_num)
            self.request_sequence_num += 1
        else:
            print("Requested to set view and sequence number for brand new message!")
            exit(1)
        return self.current_view, self.request_sequence_num - 1

    def search_log_msg(self, message):
        """search for a given message in node's backlog

        Args:
            message (Message): searched message 

        Returns:
            Message/None: Message if succesfull search, else None
        """
        for entry in self.request_log:
            if entry.msg_hash == message.hash:
                return entry
        return None

    def search_log_msghash(self, message_hash):
        """search message in log of request messages 

        Args:
            message_hash (bytes): hash representation of searched message

        Returns:
            Message object: message on succesful search of message, else None
        """
        for entry in self.request_log:
            if entry.msg_hash == message_hash:
                return entry
        return None

    def search_user_in_database(self, user):
        """searches for identifier of user in database

        Args:
            user (Str): representation of users identification in database

        Returns:
            Str: return found user or None
        """
        for key in self.template_storage.keys():
            if key == user:
                return key
        return None

    def store_features(self, features, new_user):
        """store features in template storage

        Args:
            features (Str): string features to be stored
        """
        self.users.append(new_user)
        self.template_storage[new_user] = features

    def get_sensor_data(self, string):
        """naive way of acquiring sensor biometric data

        Returns:
            Str:  representation of acquired biometric data
        """
        # return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        h = md5(bytes(string, encoding='utf8'))
        raw_data = h.hexdigest()
        return raw_data

    def extract(self, data, compromised=False):
        """naive way of extracting features from biometric data

        Args:
            data (Str): biometric data 

        Returns:
            Str: string representation of extracted features
        """
        if self.compromised_extraction:
            return "This is a representation of artificial features, set by the attacker who compromised one node!"
        else:
            h = md5(bytes(data, encoding='utf8'))
            features = h.hexdigest()
            return features

    def get_matching_compromised(self):
        """
        get_extraction_compromised after calling this function the nodes feature extraction module gets compromised
        """
        self.compromised_matching = True

    def get_extraction_compromised(self):
        """
        get_extraction_compromised after calling this function the nodes feature extraction module gets compromised
        """
        self.compromised_extraction = True

    def feature_extractor(self, data_sensory, process_type, process_id):
        """simulation of feature extraction component

        Args:
            data_sensory (Str): biometric data acquired from sensor
            process_type (Biometric_Processes): type of operation executed by the extractor(enrollment/authentication)

        Raises:
            Exception: repetitive enrollment()

        Returns:
            Dict: json/dict data containing acquired information with timestamps
        """
        # provisional feature extraction
        features = None
        features = self.extract(data_sensory)
        transaction_data = {}
        biometric_data = {}
        if process_type == Biometric_Processes.ENROLLMENT:
            if self.features_in_database(features):
                raise Exception(
                    "Features were already enrolled: Operation forbidden!")
            new_user = Wallet(''.join(random.choices(
                string.ascii_letters + string.digits, k=10)))
            transaction_data["user"] = ChainUtils.string_from_verifkey(
                new_user.verif_key)
            transaction_data["process_type"] = "enrollment"

        elif process_type == Biometric_Processes.VERIFICATION:
            transaction_data["process_type"] = "verification"
        elif process_type == Biometric_Processes.IDENTIFICATION:
            transaction_data["process_type"] = "identification"
        biometric_data["sensor_data"] = data_sensory
        biometric_data["features"] = features
        transaction_data["operation"] = "Feature Extraction"
        transaction_data["success"] = True
        transaction_data["approached_node"] = f"NODE{self.id}"
        transaction_data["extraction_timestamp"] = "12.07.1999"
        transaction_data["process_id"] = process_id

        return biometric_data, transaction_data

    def add_transaction(self, transaction):
        """add transaction to the queue waiting for block proposal

        Args:
            transaction (Transaction): processed transaction ready to be stored in blockchain
        """
        self.transaction_pool.append(transaction)

    def compare_features(self, features1, features2):
        """naive comparison of features

        Args:
            features1 (str): first features 
            features2 (str): second features

        Returns:
            Bool: True if they are similar
        """
        return features1 == features2

    def verify_decision(self, transaction, biometrics):
        """verifies the transaction 

        Args:
            transaction (Transaction): verifies the operation outcome of given transaction

        Returns:
            Str or None: If the result of the operation is validated returns None, otherwise returns the different found result
        """
        self.add_transaction(transaction)
        data = transaction.get_data()
        
        if data["operation"] == "Feature Extraction":
            features = self.extract(biometrics["sensor_data"])
            print(Fore.CYAN +
                  f'- NODE{self.id}\t\t\t\t executing feature extraction')
            if self.always_false:
                return "Proposing other artificial features to show node malfunction!"
            # if always true return the proposed result instantly
            if self.always_true:
                return None
            if self.compare_features(features, biometrics["features"]):
                return None
            else:
                return features
        if data["operation"] == "Matching":
            print(
                Fore.CYAN + f'- NODE{self.id}\t\t\t\t executing matching ' + data["process_type"])
            if self.always_false:
                return "Proposing other artificial features to show node malfunction!"
            # if always true return the proposed result instantly
            if self.always_true:
                return None

            # check blockchain for previous result of the feature extraction validation
            blockchain_data = self.blockchain.search_by_process(data["process_id"])
            if blockchain_data:
                # firstly check if the proposed user is in database
                if Biometric_Processes(data["process_type"]) == Biometric_Processes.VERIFICATION.value:
                    result = self.claimed_identity_in_database(
                        biometrics["features"], data["claimed_identity"])
                    if result:
                        # check if the users found are the same as proposed
                        if result == data["user"]:
                            return None
                    else:
                        return "Didnt find the claimant in the database"
                if Biometric_Processes(data["process_type"]) == Biometric_Processes.IDENTIFICATION.value:
                    result = self.features_in_database(biometrics["features"])
                    if result:
                        # check if found user for given features is the same as proposed one
                        if result == data["user"]:
                            return None
                    else:
                        return "Didnt find the individual in the database"
            else:
                return "Prerequisite operations are not in the blockchain"

    def verify_block(self, block):
        """
        verify_block node verifies validity of proposen block

        Args:
            block (Block): proposed block

        Returns:
            Bool: is the block valid or not
        """
        print(Fore.CYAN +
              f'- NODE{self.id}\t\t\t\t validates the proposed block!')
        if self.always_false:
            return "Proposing other artificial block to show node malfunction!"
        if self.always_true:
            return None
        if block.verify_block():
            return None
        else:
            return "Verification failed"

    def add_block_to_blockchain(self, block):
        """
        add_block_to_blockchain given node adds block to blockchain

        Args:
            block (Block): block to be added to blockchain
        """
        self.blockchain.add_block(block)

    async def received_prepare(self, msg_hash):
        """update the count of received prepares

        Args:
            msg_hash (Str): hash message representation 

        Returns:
            MessageLog: log of message that received prepare message
        """
        log = self.search_log_msghash(msg_hash)
        if log:
            log.prepare_count += self.weight
            if log.prepare_count >= config.MIN_WEIGHT_PREPARE:
                log.prepare_flag = True
        else:
            print("DIDNT FIND A MESSAGE WITH HASH " + msg_hash)
            exit(1)
        return log

    async def received_reply(self, msg_hash, result):
        """update the count of received replies

        Args:
            msg_hash (Str): hash message representation 

        Returns:
            MessageLog: log of message that received prepare message
        """
        log = self.search_log_msghash(msg_hash)
        if result:
            log.reply_count_disagree += self.weight
            log.disagreement_solution = result
        else:
            log.reply_count_agree += self.weight
        if log.reply_count_agree >= config.MIN_WEIGHT_REPLY:
            log.reply_flag = True
        if log.reply_count_disagree >= config.MIN_WEIGHT_REPLY:
            log.reply_flag = True
            log.disagreement = True
        return log

    async def received_commit(self, msg_hash):
        """update the count of received commits

        Args:
            msg_hash (Str): hash message representation 

        Returns:
            MessageLog: log of message that received prepare message
        """
        log = self.search_log_msghash(msg_hash)
        log.commit_count += self.weight
        if log.commit_count >= config.MIN_WEIGHT_COMMIT:
            log.commit_flag = True
        return log

    def get_other_nodes(self, nodes):
        """get other nodes from the network

        Args:
            nodes (List(Node)): list of nodes in the network

        Returns:
            List(Node): list of nodes containing all other nodes
        """
        if self in nodes:
            others = nodes.copy()
            others.remove(self)
            return others
        else:
            return nodes

    def create_block(self, transaction):
        """
        create_block creation of a new block with given transaction proposed by this node

        Args:
            transaction (Transaction object): transaction to be added to the block

        Returns:
            Block: created block object
        """
        block = self.blockchain.create_block(transaction, self.wallet)
        return block

    def execute_operation(self, log):
        """
        execute_operation after receiving enough replies the primary node performs this operation in this method according to the vote result

        Args:
            log (MessageLogged object): message log for given request for which the primary received enough replies
        """
        consensus_object = log.message.content["consensus_object"]
        biometrics = log.message.content["biometrics"]
        if isinstance(consensus_object, Transaction):
            data = consensus_object.get_data()
            if data["operation"] == "Feature Extraction":
                if data["success"]:
                    if not log.disagreement:
                        print(Back.GREEN + Fore.WHITE +
                              "- Feature extraction result has been validated!" + Style.RESET_ALL)
                        if Biometric_Processes(data["process_type"]) == Biometric_Processes.ENROLLMENT.value:
                            print(
                                Fore.LIGHTGREEN_EX + "- Storing features into database!" + Style.RESET_ALL)
                            self.store_features(
                                biometrics["features"], data["user"])
                        else:
                            print(
                                Fore.GREEN + "- Features have been validated and prepared for transmission to matcher!" + Style.RESET_ALL)
                    else:
                        if Biometric_Processes(data["process_type"]) == Biometric_Processes.ENROLLMENT.value:
                            print(Back.YELLOW + Fore.WHITE + "- Proposed feature extraction result has been disagreed with, other outcome determined for " +
                                  data["process_type"] + "!" + Style.RESET_ALL)

                            print(
                                Fore.YELLOW + "- Storing features into database!" + Style.RESET_ALL)
                            self.store_features(
                                log.disagreement_solution, data["user"])
                            data["success"] = True
                        else:
                            print(Back.YELLOW + Fore.WHITE + "- Proposed feature extraction result has been disagreed with, other outcome determined for " +
                                  data["process_type"] + "!" + Style.RESET_ALL)
                            data["success"] = False
                        consensus_object.update_transaction(data, self.wallet)
                else:
                    print(Back.RED + Fore.WHITE + "- Feature extraction result has not been validated, failed " +
                          data["process_type"] + "!" + Style.RESET_ALL)
            if data["operation"] == "Matching":
                if data["success"]:
                    if not log.disagreement:
                        print(Back.GREEN + Fore.WHITE + "- Matching result has been validated, succesfull " +
                              data["process_type"] + "!" + Style.RESET_ALL)
                    else:
                        print(Back.YELLOW + Fore.WHITE + "- Proposed matching result has been disagreed with, other outcome determined for " +
                              data["process_type"] + "!" + Style.RESET_ALL)
                        data["success"] = True
                        data["user"] = None
                        data["score"] = 42
                    consensus_object.update_transaction(data, self.wallet)
                else:
                    print(Back.RED + Fore.WHITE + "- Matching result has not been validated, failed " +
                          data["process_type"] + "!" + Style.RESET_ALL)
        elif isinstance(consensus_object, Block):
            print(Back.GREEN + Fore.WHITE +
                  "- Block has been validated, succesfull block proposal!" + Style.RESET_ALL)
            self.add_block_to_blockchain(consensus_object)
