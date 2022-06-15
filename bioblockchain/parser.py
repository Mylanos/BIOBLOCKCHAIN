import argparse


class MyParser:
    """argument parser
    """
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--verbose', action='store_true', default=False)
        self.args = parser.parse_args()
        self.verbose = self.args.verbose
        print(self.verbose)
