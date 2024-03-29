#!/usr/bin/env python
from bioblockchain.bioblockchain import BioBlockchain
import asyncio
from bioblockchain.parser import MyParser


"""
   Original code Copyright (c) 2011 fmark[1]
   Modified code Copyright (c) 2022 Marek Ziska, @marek_ziska7[2]
   Licensed under the CC-BY-SA 3.0[3]
   Original code posted to this question[4] and answer[5] from
   stackoverflow.com where user contributions are licensed under
   CC-BY-SA 3.0 with attribution required.
   [1]: https://stackoverflow.com/users/103225/fmark
   [2]: https://twitter.com/marek_ziska
   [3]: http://creativecommons.org/licenses/by-sa/3.0/
   [4]: https://stackoverflow.com/q/3041986
   [5]: https://stackoverflow.com/a/3041990
"""
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

    # in this scenario unknown user tries to verify himself with his own biometrics as someone who is known for the system
    if parser.unknown_individual_verification:
        asyncio.run(bio_blockchain.run_enrollment())
        print("")
        bio_blockchain.node.get_matching_compromised()
        asyncio.run(bio_blockchain.run_authentication(
            "verification", unknown_biometrics=False))
    # in this scenario known user tries to verify himself as someone else
    elif parser.unknown_individual_identification:
        asyncio.run(bio_blockchain.run_enrollment())
        print("")
        bio_blockchain.node.get_matching_compromised()
        asyncio.run(bio_blockchain.run_authentication(
            "identification", unknown_biometrics=False))
    elif parser.feature_extraction_malfunctioned:
        bio_blockchain.node.get_extraction_compromised()
        asyncio.run(bio_blockchain.run_enrollment())
    elif parser.node_malfunction_always_true:
        node = bio_blockchain.get_random_node()
        node.always_true = True
        bio_blockchain.node.get_extraction_compromised()
        asyncio.run(bio_blockchain.run_enrollment())
    elif parser.node_malfunction_always_false:
        node = bio_blockchain.get_random_node()
        node.always_false = True
        asyncio.run(bio_blockchain.run_enrollment())
        print("")
        asyncio.run(bio_blockchain.run_authentication("identification"))
    elif parser.feature_extraction_matcher_channel_intercepted:
        asyncio.run(bio_blockchain.run_enrollment())
        print("")
        asyncio.run(bio_blockchain.run_authentication_no_feature_extraction("verification"))
    else:
        asyncio.run(bio_blockchain.run_enrollment())
        print("")
        asyncio.run(bio_blockchain.run_authentication("verification"))
        print("")
        asyncio.run(bio_blockchain.run_authentication("identification"))

    if parser.verbose:
        if query_yes_no("Do you want to display the contents of blockchain?"):
            bio_blockchain.blockchain.display_chain()
        if query_yes_no("Do you want to display the contents of template database?"):
            print ("TEMPLATE DATABASE".center(120))
            print("".center(120, '-'))
            for key, value in bio_blockchain.template_storage.items():
                print ("USER_ID : {:<10} \nTEMPLATE : {:<10}".format(key, value))
                print("".center(120, '-'))


if __name__ == "__main__":
    run()
