from inspect import classify_class_attrs
from bioblockchain.bioblockchain import BioBlockchain
import asyncio
from bioblockchain.parser import MyParser

"""main script running bioblockchain scenarios"""

if __name__ == "__main__":
    parser = MyParser()
    bio_blockchain = BioBlockchain(parser.verbose)
    asyncio.run(bio_blockchain.run_enrollment())
    # call retrieves first user in the database in form of his key()
    claimed_identity = next(iter(bio_blockchain.template_storage))
    asyncio.run(bio_blockchain.run_authentication("identification", claimed_identity=claimed_identity))
    asyncio.run(bio_blockchain.run_authentication("verification"))