from hashlib import blake2b, new
import json, asyncio
from pickle import FALSE
from random import randint
from bioblockchain.blockchain import Blockchain
from bioblockchain.transaction import Transaction
import bioblockchain.config as config
from bioblockchain.node import Node, Biometric_Processes
from bioblockchain.message import Message, PBFT_Message, MessageLogged
# message type enumeration

# TODO FINDOUT what should be stored in the blockchain
# TODO get_feature_from_storage - ask on the consultation if its ok to get or search not sure
# TODO make user class instead of Node for users



class BioBlockchain():

    def __init__(self):
        self.blockchain = Blockchain()
        self.process_type = None
        self.nodes = []
        self.template_storage = {}
        self.users = []
        for num in range(config.NUM_NODES):
            self.nodes.append(Node(num, self.template_storage, self.users))
        self.pbft = PBFT(self.nodes)
        self.node = self.get_random_node()

    async def run_enrollment(self):
        print("***Received request for enrollment***")
        print("- processing the data...")
        data_sensory = self.node.get_sensor_data()
        data = self.node.feature_extractor(data_sensory, Biometric_Processes.ENROLLMENT)
        decision = await self.pbft.validate_decision(data, self.node)
        if decision:
            print("Features have been validated, storing into database!")
            self.node.store_features(data)
        else:
            raise Exception("System haven't reached consensus on the enroll request!")
        print(self.template_storage)

    async def run_verification(self):
        print("*Received request for authorization*")
        print("Processing the data...")
        data_sensory = self.node.get_sensor_data()
        data = self.node.feature_extractor(data_sensory, Biometric_Processes.VERIFICATION)
        # self.node represents an user making request to biometric system 
        decision = await self.pbft.validate_decision(data, self.node)
        if decision:
            # this should be done differently from the blockchain/or local state of nodes after last transaction(feature extraction)
            self.node.__matcher(data)
        else:
            raise Exception("System haven't reached consensus on the authorization request!")

    # random node to simulate undeterministic choice of biometric terminal/node
    def get_random_node(self):
        index = randint(0, 1000) % config.NUM_NODES
        return self.nodes[index]

class PBFT:

    def __init__(self, nodes):
        self.nodes = nodes
        self.view = 0
        # primary node for now hardly set TODO - changing views with primary nodes
        self.primary_node = self.get_leader()

    def get_leader(self):
        index = self.view % config.NUM_NODES
        return self.nodes[index]

    # broadcasts transactions
    async def validate_decision(self, data, user):
        print(f"\n-------PBFT COMMUNICATION-------")
        #TODO maybe move this to user/node class
        transaction = Transaction(data, user.wallet)
        print(f"- Creating new request!")
        await self.broadcast_request(transaction, user)
        if user.reply_flag:
            print("- Enough replies have been received, request has been executed and the decision made!")
            print(f"-------PBFT COMMUNICATION-------\n")
            return True
        print(f"\n-------PBFT COMMUNICATION-------\n")
        return False

    async def broadcast_request(self, transaction, from_node):
        await asyncio.gather(*(self.message_handler(Message(PBFT_Message.REQUEST, from_node, content=transaction), val) for val in self.nodes))

    async def broadcast_pre_prepare(self, content=None, from_node=None):
        # broadcast preprepare
        if content:
            others = from_node.get_other_nodes(self.nodes)
            await asyncio.gather(*(self.message_handler(Message(PBFT_Message.PRE_PREPARE, from_node, content=content), val) for val in others))   

    async def broadcast_prepare(self, content=None, from_node=None):
        if content:
            others = from_node.get_other_nodes(self.nodes)
            await asyncio.gather(*(self.message_handler(Message(PBFT_Message.PREPARE, from_node, content=content), val) for val in others))

    async def broadcast_commit(self, content=None, from_node = None):
        if content:
            others = from_node.get_other_nodes(self.nodes)
            await asyncio.gather(*(self.message_handler(Message(PBFT_Message.COMMIT, from_node, content=content), val) for val in others))


    def broadcast_round_change(self):
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
        # check if the language is correct
        if not message.verify():
            #TODO handle raise error
            exit(1)

        if message.ttype == PBFT_Message.REQUEST:
            print(f'- Replica{recipient.id} received message({json.dumps(message.ttype)})')
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
            print(f'- Replica{recipient.id} received message({json.dumps(message.ttype)})')
            msg_hash = message.content["msg_hash"]
            seq = message.content["seq"]
            view = message.content["view"]
            if self.is_verified_node(recipient):
                log = recipient.search_log_msghash(msg_hash)
                # not sure if its needed to keep this here, check for existence of request for given pre_prepare
                if log:
                    if recipient.corresponding_view_seq(view, seq):
                        print(f"- Replica{recipient.id} sending prepare messages")
                        await self.broadcast_prepare(content=message.content, from_node=recipient)

                # TODO node accepts pre prepare if there are not any other hash digests for given seq and view
                # after all this checks node is ready to assign seq num and view num to message proposed by pre_prepare


        elif message.ttype == PBFT_Message.PREPARE:
            print(f'- Replica{recipient.id}(n.p: {recipient.prepare_count} -> {recipient.prepare_count + 1}) received message({json.dumps(message.ttype)})')
            msg_hash = message.content["msg_hash"]
            seq = message.content["seq"]
            view = message.content["view"]
            log = await recipient.received_prepare(msg_hash)
            if log.prepare_flag and not log.commit_sent:
                log.commit_sent = True
                print(f"- Replica{recipient.id}(n.p: {log.prepare_count}) sending commit messages")
                await self.broadcast_commit(content=message.content, from_node=recipient)

        elif message.ttype == PBFT_Message.COMMIT:
            print(f'- Replica{recipient.id}(n.c: {recipient.commit_count} -> {recipient.commit_count + 1}) received message({json.dumps(message.ttype)})')
            msg_hash = message.content["msg_hash"]
            log = await recipient.received_commit(msg_hash)
            if log.commit_flag and not log.reply_sent:
                decision = recipient.verify_decision(log.message.content)
                print(f"- Replica{recipient.id}(n.c: {recipient.commit_count}) sending reply message with {decision} decision!")
                log.reply_sent = True
                content = message.content["msg_hash"], decision
                reply = Message(PBFT_Message.REPLY, recipient, content)
                await self.message_handler(reply, log.message.sender)

        elif message.ttype == PBFT_Message.REPLY:
            msg_hash, decision = message.content
            log = await recipient.received_reply(msg_hash)
            print(f'- Replica{recipient.id}(decision: {decision}) received message({json.dumps(message.ttype)})')





if __name__ == "__main__":
    bio_blockchain = BioBlockchain()
    asyncio.run(bio_blockchain.run_enrollment())
    asyncio.run(bio_blockchain.run_enrollment())
    
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
Po prijatí požiadavku daný node danej komponenty vytvorí novú transakciu tvorenú contentom markantov, id daného nodu(validatora) a výsledok(True/False u Matchera) uklada transaction
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