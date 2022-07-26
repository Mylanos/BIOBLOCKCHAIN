from random import randint
from bioblockchain.blockchain import Blockchain
import bioblockchain.config as config
from bioblockchain.node import Node, Biometric_Processes
from colorama import Fore, Style, Back
from bioblockchain.pbft import PBFT
from bioblockchain.chain_utils import ChainUtils


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

        self.users = []
        for num in range(config.NUM_PARTICIPATING_NODES):
            self.nodes.append(Node(num, self.template_storage, self.users,
                              self.blockchain, 1 / config.NUM_PARTICIPATING_NODES))
        self.pbft = PBFT(self.nodes, verbosity)
        self.node = self.get_random_node()

    async def run_enrollment(self, compromised_feature_extractor=False):
        """
        run_enrollment showcases enrollment scenario of a new user to the biometric system


        Args:
            compromised_feature_extractor (bool, optional): True when the proposing extractor is compromised. Defaults to False.
        """
        # unique ID identifying this process of enrollment for later tracing of transactions within this operation
        new_process_id = ChainUtils.id()
        print("\n" + Back.YELLOW + Fore.WHITE +
              "***START OF ENROLLMENT***".center(80) + Style.RESET_ALL)
        print("- Sensor scanning raw biometrics...")
        # sensor collects and stores received data
        data_sensory = self.node.get_sensor_data(
            f"Naive way of acquiring known raw biometric data from sensor!")
        print("- Feature extractor processing raw data...")
        # feature extraction of collected data on approached terminal
        biometric_data, feature_extraction_data = self.node.feature_extractor(
            data_sensory, Biometric_Processes.ENROLLMENT, new_process_id, compromised_feature_extractor=compromised_feature_extractor)
        print("- Extracted features requesting to be validated...")
        # extracted features on approached terminal
        await self.pbft.validate_decision(feature_extraction_data, biometric_data, self.node)
        #print(Fore.RED + "System haven't received enough replies for consensus on the enroll request!"+ Style.RESET_ALL)
        print(Back.YELLOW + Fore.WHITE +
              "***END OF ENROLLMENT***".center(80) + Style.RESET_ALL)

    async def run_authentication(self, process, claimed_identity=None, unknown_biometrics=True, unknown_user=False, compromised_matcher=False):
        """
        run_authentication showcases identification or verification scenario in the biometric system

        Args:
            process (str): type of authentication/recognition process
            claimed_identity (str, optional): in case of verification, claimed identity is needed. Defaults to None.
            unknown_biometrics (bool, optional): new biometrics. Defaults to True.
            unknown_user (bool, optional): _description_. Defaults to False.
            compromised_matcher (bool, optional): _description_. Defaults to False.
        """
        new_process_id = ChainUtils.id()
        print(Back.YELLOW + Fore.WHITE +
              f"***START OF {process.upper()}***".center(80) + Style.RESET_ALL)
        print("- Sensor scanning raw biometrics...")
        data_sensory = None
        if unknown_biometrics:
            data_sensory = self.node.get_sensor_data(
                f"Naive way of acquiring known raw biometric data from sensor!")
        else:
            data_sensory = self.node.get_sensor_data(
                f"Naive way of acquiring not known raw biometric data from sensor!")
        print("- Feature extractor processing raw data...")
        biometric_data, feature_extraction_data = self.node.feature_extractor(
            data_sensory, Biometric_Processes(process), new_process_id)

        if unknown_user:
            claimed_identity = "Attackers unknown identity"
        else:
            claimed_identity = next(iter(self.template_storage))

        print("- Extracted features requesting to be validated...")

        # self.node represents one node in the network making validating request to others
        await self.pbft.validate_decision(feature_extraction_data, biometric_data, self.node)

        # check blockchain result of the validation
        blockchain_data = self.blockchain.search_by_process(new_process_id)
        if blockchain_data["success"]:
            matcher_data = self.node.matcher(biometric_data["features"], Biometric_Processes(
                process), claimed_identity, new_process_id, compromised=compromised_matcher)
            template = {}
            template["features"] = biometric_data["features"]
            await self.pbft.validate_decision(matcher_data, template, self.node)
        else:
            print(
                Fore.RED + "System haven't reached consensus on the authorization request!" + Style.RESET_ALL)
        print(Back.YELLOW + Fore.WHITE +
              f"***END OF {process.upper()}***".center(80) + Style.RESET_ALL)


    async def run_authentication_no_feature_extraction(self, process,  compromised_matcher=False):
        """
        run_authentication_no_feature_extraction showcases malicious identification or verification scenario in the biometric system with replayed data

        Args:
            process (str): type of authentication/recognition process
            claimed_identity (str, optional): in case of verification, claimed identity is needed. Defaults to None.
            unknown_biometrics (bool, optional): new biometrics. Defaults to True.
            unknown_user (bool, optional): _description_. Defaults to False.
            compromised_matcher (bool, optional): _description_. Defaults to False.
        """
        new_process_id = ChainUtils.id()
        print(Back.YELLOW + Fore.WHITE +
              f"***START OF {process.upper()}***".center(80) + Style.RESET_ALL)
        
        # "KNOWN USER DATA" - imitated interception and its subsequent replay
        data_sensory = self.node.get_sensor_data(
                f"Naive way of acquiring known raw biometric data from sensor!")
        biometric_data, _ = self.node.feature_extractor(
            data_sensory, Biometric_Processes(process), new_process_id)
        claimed_identity = next(iter(self.template_storage))

        
        matcher_data = self.node.matcher(biometric_data["features"], Biometric_Processes(
            process), claimed_identity, new_process_id, compromised=compromised_matcher)
        template = {}
        template["features"] = biometric_data["features"]
        # check blockchain result of the validation
        blockchain_data = self.blockchain.search_by_process(new_process_id)
        if not blockchain_data:
            matcher_data["success"] = False
            matcher_data["user"] = None
        await self.pbft.validate_decision(matcher_data, template, self.node)
        
        print(Back.YELLOW + Fore.WHITE +
              f"***END OF {process.upper()}***".center(80) + Style.RESET_ALL)


    def get_random_node(self):
        """
        get_random_node random node to simulate undeterministic choice of biometric terminal/node

        Returns:
            Node: node selected from the network
        """
        index = randint(0, 1000) % config.NUM_PARTICIPATING_NODES
        return self.nodes[index]
