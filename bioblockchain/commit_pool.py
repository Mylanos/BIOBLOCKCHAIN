from bioblockchain.utils import ChainUtils

class CommitPool:
    
    # list object is mapping that holds a list commit messages for a hash of a block
    def __init__(self):
        self.commits = {}

    """initializes a list of commit message for a prepare message
    and adds the commit message for the current node and returns it"""
    def commit(self, prepare, wallet):
        commit = self.createCommit(prepare, wallet)
        self.commits[prepare.blockHash] = []
        self.commits[prepare.blockHash].append(commit)
        return commit
  

    # creates a commit message for the given prepare message
    def createCommit(self, prepare, wallet):
        commit = {}
        commit["block_hash"] = prepare.blockHash
        commit["public_key"] = wallet._verif_key
        commit["signature"] = wallet.sign(prepare.blockHash)
        return commit

    # checks if the commit message already exists
    def existingCommit(self, commit):
        return [c for c in self.commits if c.id == commit.id]

    # checks if the commit message is valid or not
    def isValidCommit(self, commit):
        return ChainUtils.verify_signature(
            commit.publicKey,
            commit.signature,
            commit.blockHash
        )

    # pushes the commit message for a block hash into the list
    def addCommit(self, commit):
        self.commits[commit.blockHash].push(commit)
    
