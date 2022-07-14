import argparse


class MyParser:
    """argument parser
    """
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--verbose', action='store_true', default=False, help='shows the detailed information about communication.')
        parser.add_argument('-uuv', '--unknown_user_verification', action='store_true', default=False, help='scenario when unknown user tries to authenticate himself.')
        parser.add_argument('-fef', '--feature_extraction_fail', action='store_true', default=False, help='scenario when feature extraction fails/gets compromised.')
        parser.add_argument('-nmat', '--node_malfunction_always_true', action='store_true', default=False, help='scenario when one of the nodes always returns true.')
        parser.add_argument('-nmaf', '--node_malfunction_always_false', action='store_true', default=False, help='scenario when one of the nodes always returns false.')

        self.args = parser.parse_args()
        self.verbose = self.args.verbose
        self.unknown_user_verification = self.args.unknown_user_verification
        self.feature_extraction_fail = self.args.feature_extraction_fail
        self.node_malfunction_always_true = self.args.node_malfunction_always_true
        self.node_malfunction_always_false = self.args.node_malfunction_always_false

