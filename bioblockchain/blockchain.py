from bioblockchain.block import Block


class Blockchain:
    """blockchain class containing list(chain) of blocks
    """

    def __init__(self):
        self.chain = [Block.genesis()]

    def create_block(self, transactions, wallet):
        """create_block wrapper function for Block instantiation

        Args:
            transactions ([Transaction object]): list of transactions that will be stored in newly created block
            wallet (Wallet object): proposer of the block

        Returns:
            Block object: instance of Block object
        """
        block = Block.create_block(
            self.chain[len(self.chain) - 1],
            transactions,
            wallet
        )
        return block

    def add_block(self, block: Block):
        """add_block appends block to the blockchain

        Args:
            block (Block object): block to be appended

        Returns:
            Block object: appended block
        """
        self.chain.append(block)
        return block

    def is_valid_block(self, block: Block):
        """check for validity of block

        Args:
            block (Block object): Block object to be validated

        Returns:
            bool: True if valid, else False
        """
        last_block = self.chain[-1]
        if((last_block.seq_number + 1) == block.seq_number and
                last_block.hash_hexdigest == block.previous_hash_hexdigest):
            # TODO not sure if its needed to verify the proposer with block method verify_proposer
            if(block.hash_hexdigest == Block.block_hash(block).hexdigest() and block.verify_block()):
                return True
        return False

    def display_chain(self):
        """prints out the blockchain content
        """
        for i in range(len(self.chain)):
            print(self.chain[i])

    @property
    def last_block(self):
        """
        last_block property containing last block in the blockchain

        Returns:
            Block object: latest block object appended to the blockchain
        """
        return self.chain[-1]

    def search_by_process(self, process_id):
        """
        search_by_process looks for block containing transaction with given process_id

        Args:
            process_id (Str): string representation of the searched process_id

        Returns:
            Block: found Block or None
        """
        for block in self.chain:
            result = block.search_by_process(process_id)
            if result:
                return result
        return None
