import argparse


class MyParser:
    """argument parser
    """

    def __init__(self):
        parser = argparse.ArgumentParser()
        group = parser.add_mutually_exclusive_group()
        parser.add_argument('-v', '--verbose', action='store_true', default=False,
                            help='shows the detailed information about communication.')
        group.add_argument('-uiv', '--unknown_individual_verification', action='store_true',
                           default=False, help='scenario when unknown individual tries to verify himself.')
        group.add_argument('-uii', '--unknown_individual_identification', action='store_true',
                           default=False, help='scenario when unknown individual tries to get identified.')
        group.add_argument('-fem', '--feature_extraction_malfunctioned', action='store_true',
                           default=False, help='scenario when feature extraction fails/gets compromised.')
        group.add_argument('-nmat', '--node_malfunction_always_true', action='store_true',
                           default=False, help='scenario when one of the nodes always returns true.')
        group.add_argument('-nmaf', '--node_malfunction_always_false', action='store_true',
                           default=False, help='scenario when one of the nodes always returns false.')

        self.args = parser.parse_args()
        self.verbose = self.args.verbose
        self.unknown_individual_verification = self.args.unknown_individual_verification
        self.unknown_individual_identification = self.args.unknown_individual_identification
        self.feature_extraction_malfunctioned = self.args.feature_extraction_malfunctioned
        self.node_malfunction_always_true = self.args.node_malfunction_always_true
        self.node_malfunction_always_false = self.args.node_malfunction_always_false
