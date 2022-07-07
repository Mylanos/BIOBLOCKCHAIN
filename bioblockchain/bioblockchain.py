from random import randint
from bioblockchain.blockchain import Blockchain
import bioblockchain.config as config
from bioblockchain.node import Node, Biometric_Processes
from colorama import Fore, Style, Back
from bioblockchain.pbft import PBFT
from bioblockchain.utils import ChainUtils

class BioBlockchain():
    """
    BioBlockchain is a main class containing scenarios showcasing integration of blockchain and biometric system processes
    """

    def __init__(self, verbosity):
        self.blockchain = Blockchain()
        self.process_type = None
        # list of nodes in the bioblockchain network
        self.nodes = []
        # template database so far structured in ("public_key": features)
        self.template_storage = {}
        #TODOOO rethink how are you going to store data in database
        self.users = []
        for num in range(config.NUM_NODES):
            self.nodes.append(Node(num, self.template_storage, self.users, self.blockchain))
        self.pbft = PBFT(self.nodes, verbosity)
        self.node = self.get_random_node()

    async def run_enrollment(self):
        """
        run_enrollment showcases enrollment scenario of a new user to the biometric system
        """
        # unique ID identifying this process of enrollment for later tracing of transactions within this operation
        new_process_id = ChainUtils.id()
        print("\n" + Fore.YELLOW + "***\tStart of enrollment\t\t***" + Style.RESET_ALL)
        print("- Sensor scanning raw biometrics...")
        # sensor collects and stores received data
        data_sensory = self.node.get_sensor_data()
        print("- Feature extractor processing raw data...")
        # feature extraction of collected data on approached terminal
        feature_extractor_data = self.node.feature_extractor(data_sensory, Biometric_Processes.ENROLLMENT)
        feature_extractor_data["operation"] = "Feature Extraction"
        feature_extractor_data["process_id"] = new_process_id
        print("- Extracted features requesting to be validated...")
        # extracted features on approached terminal
        decision = await self.pbft.validate_decision(feature_extractor_data, self.node)
        if decision:
            print(Back.GREEN + Fore.WHITE + "- Features have been consensually validated, storing into database!"+ Style.RESET_ALL)
            self.node.store_features(feature_extractor_data["features"])
        else:
            print(Fore.RED + "System haven't reached consensus on the enroll request!"+ Style.RESET_ALL)
        print(Fore.YELLOW + "***\tEnd of enrollment\t\t***" + Style.RESET_ALL)

    async def run_authentication(self, process, claimed_identity = None):
        """run_authentication showcases identification or verification scenario in the biometric system

        Args:
            process (str): type of authentication/recognition process
        """
        new_process_id = ChainUtils.id()
        print("\n" + Fore.YELLOW + f"\n***\tStart of  {process}\t***" + Style.RESET_ALL)
        print("- Sensor scanning raw biometrics...")
        data_sensory = self.node.get_sensor_data()
        print("- Feature extractor processing raw data...")
        feature_extractor_data = self.node.feature_extractor(data_sensory, Biometric_Processes(process))
        feature_extractor_data["operation"] = "Feature Extraction"
        feature_extractor_data["process_id"] = new_process_id
        # just for the showcase of successful authentication HARD SELECT of first user stored in the database
        first_user_key = next(iter(self.template_storage))
        feature_extractor_data["features"] = self.template_storage[first_user_key]
        print("- Extracted features requesting to be validated...")
        # self.node represents one node in the network making validating request to others
        feature_extractor_decision = await self.pbft.validate_decision(feature_extractor_data, self.node)
        if feature_extractor_decision:
            print("- Features have been consensually validated, transmitting to matcher!")
            # this should be done differently from the blockchain/or local state of nodes after last transaction(feature extraction)
            matcher_data = self.node.matcher(feature_extractor_data["features"], Biometric_Processes(process), claimed_identity)
            matcher_data["operation"] = "Matching"
            matcher_data["process_id"] = new_process_id
            matcher_decision = await self.pbft.validate_decision(matcher_data, self.node)
            if matcher_decision:
                print(Back.GREEN + Fore.WHITE + "- Match result has been consensually validated, succesfull " + matcher_data["process_type"] + "!" + Style.RESET_ALL)
        else:
            print(Fore.RED + "System haven't reached consensus on the authorization request!"+ Style.RESET_ALL)
        print(Fore.YELLOW + f"***\tEnd of {process}\t\t\t***" + Style.RESET_ALL)

    #TODO change the selection of the nodes to be evenly spread out in the distributed system
    def get_random_node(self):
        """
        get_random_node random node to simulate undeterministic choice of biometric terminal/node

        Returns:
            Node: node selected from the network
        """
        index = randint(0, 1000) % config.NUM_PARTICIPATING_NODES
        return self.nodes[index]