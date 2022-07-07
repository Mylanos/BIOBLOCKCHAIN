import bioblockchain
from bioblockchain.bioblockchain import BioBlockchain
import asyncio
from bioblockchain.parser import MyParser

def query_yes_no(question, default="yes"):
    """
    query_yes_no Ask a yes/no question via and returns the answer.

    Args:
        question (Str): question asked to the user
        default (Str, optional): Default answear when the entered answear is blank. Defaults to "yes".

    Returns:
        Bool:  Depending on the answer returns True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True,  "no": False, "n": False}
    while True:
        print(question + " [Y/n] ")
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please enter 'yes' or 'no' answear! (or 'y' or 'n').\n")

def run():
    """
    run is a main script running the bioblockchain demonstrator
    """
    parser = MyParser()
    bio_blockchain = BioBlockchain(parser.verbose)
    asyncio.run(bio_blockchain.run_enrollment())
    # call retrieves first user in the database in form of his key()
    claimed_identity = next(iter(bio_blockchain.template_storage))
    asyncio.run(bio_blockchain.run_authentication("verification", claimed_identity=claimed_identity))
    asyncio.run(bio_blockchain.run_authentication("identification"))
    if parser.verbose:
        if query_yes_no("Do you want to display the contents of blockchain?"):
            bio_blockchain.blockchain.display_chain()
    print(bio_blockchain.template_storage)


if __name__ == "__main__":
    run()