import json, asyncio
from random import random, uniform
from bioblockchain.transaction import Transaction
import bioblockchain.config as config
from bioblockchain.message import Message, PBFT_Message
from colorama import Fore, Style, Back

class PBFT:
    """PBFT protocol communication
    """
    def __init__(self, nodes, verbosity):
        self.nodes = nodes
        self.view = 0
        self.verbose = verbosity
        # primary node for now hardly set TODO - changing views with primary nodes
        self.primary_node = self.get_leader()

    def get_leader(self):
        """returns current leader

        Returns:
            Node: Node object with current leader
        """
        index = self.view % config.NUM_NODES
        return self.nodes[index]

    # broadcasts transactions
    async def validate_decision(self, data, user):
        """interface of the pbft protocol where the Transaction is made and Request to validate decision/operation sent """
        print(Fore.BLUE + "----------------PBFT START----------------" + Style.RESET_ALL)
        #TODO maybe move this to user/node class
        transaction = Transaction(data, user.wallet)
        print(Fore.CYAN + f"""- Creating new validation request for {data["operation"]}!""" + Style.RESET_ALL)
        await self.broadcast_request(transaction, user)
        if True:
            print(Fore.BLUE  + "----------------PBFT END----------------" + Style.RESET_ALL)
            return True
        print("\n" + Fore.BLUE  + "----------------PBFT COMMUNICATION----------------" + Style.RESET_ALL)
        return False

    async def broadcast_request(self, transaction, from_node):
        """brodcasts new request to all nodes in the network
        """
        await asyncio.gather(*(self.message_handler(Message(PBFT_Message.REQUEST, from_node, content=transaction), val) for val in self.nodes))

    async def broadcast_pre_prepare(self, content=None, from_node=None):
        """brodcasts pre_prepare to all nodes in the network

        Args:
            content (Dict, optional): json data neccesary for pre_prepare message(msg_hash/seq_no/view). Defaults to None.
            from_node (Node, optional): node object sending the pre_prepare message. Defaults to None.
        """
        if content:
            others = from_node.get_other_nodes(self.nodes)
            await asyncio.gather(*(self.message_handler(Message(PBFT_Message.PRE_PREPARE, from_node, content=content), val) for val in others))   

    async def broadcast_prepare(self, content=None, from_node=None):
        """brodcasts prepare to all nodes in the network


        Args:
            content (Dict, optional): json data neccesary for prepare message(msg_hash/seq_no/view). Defaults to None.
            from_node (Node, optional): node object sending the prepare message. Defaults to None.
        """
        if content:
            others = from_node.get_other_nodes(self.nodes)
            await asyncio.gather(*(self.message_handler(Message(PBFT_Message.PREPARE, from_node, content=content), val) for val in others))

    async def broadcast_commit(self, content=None, from_node = None):
        """brodcasts commit to all nodes in the network


        Args:
            content (Dict, optional): json data neccesary for commit message(msg_hash/seq_no/view). Defaults to None.
            from_node (Node, optional): node object sending the commit message. Defaults to None.
        """
        if content:
            others = from_node.get_other_nodes(self.nodes)
            await asyncio.gather(*(self.message_handler(Message(PBFT_Message.COMMIT, from_node, content=content), val) for val in others))


    def broadcast_round_change(self):
        #TODO unfinished round changing - primary 
        print(f"********************ROUND-CHANGE********************")
        for validator in self.nodes:
           self.message_handler(
                f"Validator{validator} received ROUND-CHANGE message")

    # TODO maybe some other class for matcher functionality or put it somewhere else
    def check_match(self):
        return True

    def is_verified_node(self, node):
        if node in self.nodes:
            return True
        return False

    def is_leader(self, wallet):
        if wallet == self.primary_node:
            return True
        return False

    async def message_handler(self, message, recipient):
        """message execution manager function

        Args:
            message (Message): message object being handled by the PBFT protocl
            recipient (Node): adressee of the message being handled
        """
        # simulation mode? -> delays between messages -> await asyncio.sleep(uniform(0,1))
        # check if the message is correct
        if not message.verify():
            #TODO handle raise error
            exit(1)

        if message.ttype == PBFT_Message.REQUEST:
            if self.verbose:
                print(Fore.CYAN + f'- NODE{recipient.id} (INIT) \t\t received message({json.dumps(message.ttype)})')
            transaction = message.content
            tx_type = transaction.get_type()
            #TODO check for repetitive request(also possibly think about repetitive transactions)
            if transaction.verify_transaction():
                msg_hash = recipient.add_request_to_log(message)
                if self.is_leader(recipient) and self.is_verified_node(recipient):
                    view, seq = recipient.set_seq_number(msg_hash)
                    content = {"msg_hash": msg_hash, "seq": seq, "view": view}
                    await self.broadcast_pre_prepare(content=content, from_node=recipient)
                    # TODO handle creation of new blocks, maybe it would make sense to do in the reply message phase
                      
            else:
                raise("Unsuccesful verification of sent transaction!")
        elif message.ttype == PBFT_Message.PRE_PREPARE: 
            if self.verbose:
                print(f'- NODE{recipient.id} (PRE-PREPARING)\t received message({json.dumps(message.ttype)})')
            msg_hash = message.content["msg_hash"]
            seq = message.content["seq"]
            view = message.content["view"]
            if self.is_verified_node(recipient):
                log = recipient.search_log_msghash(msg_hash)
                # not sure if its needed to keep this check for existence of request for given pre_prepare
                if log:
                    if recipient.corresponding_view_seq(view, seq):
                        if self.verbose:
                            print(f"- NODE{recipient.id} (PRE-PREPARED) \t sending prepare messages")
                        await self.broadcast_prepare(content=message.content, from_node=recipient)

                # TODO node accepts pre prepare if there are not any other hash digests for given seq and view
                # after all this checks node is ready to assign seq num and view num to message proposed by pre_prepare


        elif message.ttype == PBFT_Message.PREPARE:
            msg_hash = message.content["msg_hash"]
            log = await recipient.received_prepare(msg_hash)
            if self.verbose:
                print(f'- NODE{recipient.id} (PREPARES:{log.prepare_count - 1}->{log.prepare_count})\t received message({json.dumps(message.ttype)})')
            seq = message.content["seq"]
            view = message.content["view"]
            if log.prepare_flag and not log.commit_sent:
                log.commit_sent = True
                if self.verbose:
                    print(f"- NODE{recipient.id} (PREPARES:{log.prepare_count})\t sending commit messages")
                await self.broadcast_commit(content=message.content, from_node=recipient)

        elif message.ttype == PBFT_Message.COMMIT:
            msg_hash = message.content["msg_hash"]
            log = await recipient.received_commit(msg_hash)
            if self.verbose:
                print(Fore.CYAN + f'- NODE{recipient.id} (COMMITS:{log.commit_count - 1}->{log.commit_count})\t received message({json.dumps(message.ttype)})')
            if log.commit_flag and not log.reply_sent:
                # execution of the operation being validated(feature extraction / matching)
                decision = recipient.verify_decision(log.message.content)
                if self.verbose:
                    print(f"- NODE{recipient.id} (COMMITS:{log.commit_count})\t validated transaction, sending \"REPLY\" message!")
                log.reply_sent = True
                content = message.content["msg_hash"], decision
                reply = Message(PBFT_Message.REPLY, recipient, content)
                await self.message_handler(reply, log.message.sender)

        elif message.ttype == PBFT_Message.REPLY:
            msg_hash, decision = message.content
            log = await recipient.received_reply(msg_hash)
            if self.verbose:
                print(f'- NODE{recipient.id} (REPLIES:{log.reply_count - 1}->{log.reply_count})\t received message({json.dumps(message.ttype)})')
            if log.reply_flag and not log.reply_operation_executed:
                log.reply_operation_executed = True
                print(Fore.GREEN + "- Enough replies have been received, request has been executed and succesfully validated!" + Style.RESET_ALL)
            
    
"""
data = {}
data["type"] = "request"
data["markants"] = "jofanfafnakejnaskjgbhjfkberghkas"
fero = Wallet("lmao")

transaction = Transaction(data, fero)
validator = Node(69)
msg = Message(PBFT_Message.REQUEST, validator, transaction=transaction)
#json_data = json.dumps(msg, default=lambda o: o.__dict__)
print(msg.toJSON())
print(PBFT_Message.PRE_PREPARE)
"""

"""
if recipient.transaction_pool.filled():
    print("Transaction pool THRESHOLD reached: ready to propose new BLOCK!")
    if self.blockchain.get_proposer() == self.primary_node:
        print("Validated proposer: proposing new BLOCK!")
        new_block = self.blockchain.create_block(
            self.transaction_pool.transactions, self.primary_node)
        self.block_pool.add_block(new_block)
        print(f"************************************************TRANSACTION************************************************")
        self.broadcast_pre_prepare(new_block)
"""  


"""
Môj thougth process

Takže spravit funkciu ktora bude len simulovať požiadavok na jednu z komponent(nebude sa vytvarať žiadna transakcia pre požiadavok). Tento požiadavok pôjde z nodu ktorý bude reprezentovať
a sprostredkovávať matcher.
Po prijatí požiadavku daný node danej komponenty vytvorí novú transakciu tvorenú contentom markantov, id daného nodu(validatora) a výsledok(True/False/Score u Matchera) uklada transaction
do local poolu transakcii
Broadcast transakcie - preprepare. Po prijatí pre_prepare správy overí transakciu(prijimatel, či ju už nemá v poole a či odosielateľ je korekt validator). Ak rozhodne a nenastane žiadna chyba pri prenose odosiela 
spravu Prepare všetkym ostatnym nodom v sieti.

"""

"""
node is considered prepared when it has seen request from the primary node, has pre-prepared and has seen 2f prepare messages that matches pre-prepare(looking for 2f+1 prepares)
when nodes are prepared they sent commit message, if a node has seen f+1 valid commit messages, they carry out the client request and sendout a reply to the client
"""

"""
data = {"id": 1234,
        "room-entered": "E104",
        "verificated": True,
        "entered-by": "Alice"}

data2 = {"id": 3434,
            "room-entered": "E105",
            "verificated": False,
            "entered-by": "Alice"}

data3 = {"id": 3714,
            "room-entered": "D105",
            "verificated": True,
            "entered-by": "Stephan"}

data4 = {"id": 9834,
            "room-entered": "D105",
            "verificated": False,
            "entered-by": "Stephan"}

data5 = {"id": 4324,
            "content": "osjf-fsafsaf-asdfdsf-sff",
            "req_type": "match",
            "req-by": "node_xyz"}
"""