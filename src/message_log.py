
from bioblockchain.chain_utils import ChainUtils


class MessageLogged:
    """Single log stored in a node for given message
    """

    def __init__(self, message, weight):
        self.msg_hash = ChainUtils.hash(message.toJSON()).digest()
        self.message = message
        self.prepare_count = weight
        self.commit_count = 0
        self.reply_count_agree = 0
        self.reply_count_disagree = 0
        self.prepare_flag = False
        self.commit_flag = False
        self.reply_flag = False
        self.disagreement = False
        self.disagreement_solution = None
        self.reply_operation_executed = False
        self.commit_sent = False
        self.reply_sent = False
        self.view_num = None
        self.seq_num = None

    def update_nums(self, view_num, seq_num):
        """
        update_nums updates view and sequence number of PBFT protocol

        Args:
            view_num (Int): current view number
            seq_num (Int): current sequence number
        """
        self.view_num = view_num
        self.seq_num = seq_num

    def __str__(self) -> str:
        return (f"""
- MessageLog
Hash: {self.msg_hash}
Message: {self.message.toJSON()}
Prepares: {self.prepare_count}
ViewNum: {self.view_num}
SeqNum: {self.view_num}
        """)
