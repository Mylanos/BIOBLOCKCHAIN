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

    async def run_enrollment(self, compromised=False):
        """
        run_enrollment showcases enrollment scenario of a new user to the biometric system
        """
        # unique ID identifying this process of enrollment for later tracing of transactions within this operation
        new_process_id = ChainUtils.id()
        print("\n" + Back.YELLOW + Fore.WHITE + "***\tSTART OF ENROLLMENT\t\t***" + Style.RESET_ALL)
        print("- Sensor scanning raw biometrics...")
        # sensor collects and stores received data
        data_sensory = self.node.get_sensor_data(f"Naive way of acquiring raw data from sensor for simulating successfull sensor operation!")
        print("- Feature extractor processing raw data...")
        # feature extraction of collected data on approached terminal
        biometric_data, feature_extraction_data = self.node.feature_extractor(data_sensory, Biometric_Processes.ENROLLMENT, new_process_id, compromised=compromised)
        feature_extraction_data["process_id"] = new_process_id
        print("- Extracted features requesting to be validated...")
        # extracted features on approached terminal
        await self.pbft.validate_decision(feature_extraction_data, biometric_data, self.node)
        #print(Fore.RED + "System haven't received enough replies for consensus on the enroll request!"+ Style.RESET_ALL)
        print(Back.YELLOW + Fore.WHITE +"***\tEND OF ENROLLMENT\t\t***" + Style.RESET_ALL)

    async def run_authentication(self, process, claimed_identity = None, success = True):
        """run_authentication_success showcases identification or verification scenario in the biometric system

        Args:
            process (str): type of authentication/recognition process
        """
        new_process_id = ChainUtils.id()
        print(Back.YELLOW + Fore.WHITE + f"\n***\tSTART OF {process.upper()}\t\t\t***{Style.RESET_ALL}")
        print("- Sensor scanning raw biometrics...")
        data_sensory = self.node.get_sensor_data(f"Naive way of acquiring raw data from sensor for simulating successfull sensor operation!")
        print("- Feature extractor processing raw data...")
        biometric_data, feature_extraction_data = self.node.feature_extractor(data_sensory, Biometric_Processes(process), new_process_id)
        # just for the showcase of successful authentication HARD SELECT of first user stored in the database
        first_user_key = next(iter(self.template_storage))
        biometric_data["features"] = self.template_storage[first_user_key]
        print("- Extracted features requesting to be validated...")
        # self.node represents one node in the network making validating request to others
        await self.pbft.validate_decision(feature_extraction_data, biometric_data, self.node)
        # check blockchain result of the validation
        blockchain_data = self.blockchain.search_by_process(new_process_id)
        if blockchain_data["success"]:
            matcher_data = self.node.matcher(biometric_data["features"], Biometric_Processes(process), claimed_identity, new_process_id)
            await self.pbft.validate_decision(matcher_data, biometric_data, self.node)
        else:
            print(Fore.RED + "System haven't reached consensus on the authorization request!"+ Style.RESET_ALL)
        print(Back.YELLOW + Fore.WHITE + f"***\tEND OF {process.upper()}\t\t\t***" + Style.RESET_ALL)

    #TODO change the selection of the nodes to be evenly spread out in the distributed system
    def get_random_node(self):
        """
        get_random_node random node to simulate undeterministic choice of biometric terminal/node

        Returns:
            Node: node selected from the network
        """
        index = randint(0, 1000) % config.NUM_PARTICIPATING_NODES
        return self.nodes[index]
