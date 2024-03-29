import json
import asyncio
from bioblockchain.transaction import Transaction
from bioblockchain.block import Block
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
        # long repeating list of nodes for round robin, async generator might be needed in future versions
        # self.iter_nodes = self.nodes * config.ITER_LIST_AMMOUNT
        self.iter_index = 0
        self.participating_nodes = []

    def get_leader(self):
        """returns current leader

        Returns:
            Node: Node object with current leader
        """
        index = self.view % config.NUM_PARTICIPATING_NODES
        return self.nodes[index]

    async def async_range(self, count):
        for i in range(count):
            yield(i)
            await asyncio.sleep(0)

    """
    async def round_robin(self):
        self.participating_nodes.clear()
        for x in range(config.NUM_PARTICIPATING_NODES - 1):
            if self.iter_index == config.ITER_LIST_AMMOUNT:
                self.iter_index = 0
            if self.primary_node != self.iter_nodes[self.iter_index]:
                self.participating_nodes.append(
                    self.iter_nodes[self.iter_index])
            else:
                self.iter_index += 1
                self.participating_nodes.append(
                    self.iter_nodes[self.iter_index])
            self.iter_index += 1
        self.participating_nodes.append(self.primary_node)
    """

    async def validate_decision(self, transaction_data, biometric_data, user):
        """interface of the pbft protocol where the Transaction is made for given operation and broadcasts request to validate decision/operation to PBFT 

        Args:
            data (Dict): json/dict data of executed operation to get validated 
            user (Node): entry Node executing the operation

        Returns:
            Bool: result of the validation
        """
        transaction = Transaction(transaction_data, user.wallet)
        content = {"consensus_object": transaction,
                   "biometrics": biometric_data}
        if transaction_data["success"]:
            print(
                Fore.GREEN + f"""- Creating new request for {transaction_data["operation"]} validation of SUCCESS {transaction_data["process_type"]}!""" + Style.RESET_ALL)
        else:
            print(
                Fore.RED + f"""- Creating new request for {transaction_data["operation"]} validation of FAILED {transaction_data["process_type"]}!""" + Style.RESET_ALL)
        await self.broadcast_request(content, user)

    # broadcasts transactions
    async def validate_block(self, block, user):
        """interface of the pbft protocol where the Block is proposed to be validated in PBFT 

        Args:
            block (Block): proposed Block 
            user (Node): entry Node proposing the block
        """
        content = {"consensus_object": block, "biometrics": None}

        print(f"""- Creating new validation request for new block proposal!""")
        await self.broadcast_request(content, user)

    async def broadcast_request(self, content, from_node):
        """brodcasts new request to all nodes in the network

        Args:
            content (Transaction, Block): data sent to network in request
            user (Node): Node who sent the message

        """
        print(Fore.BLUE + "PBFT START".center(80, '-') + Style.RESET_ALL)
        # await self.round_robin()

        await asyncio.gather(*(self.message_handler(Message(PBFT_Message.REQUEST, from_node, content=content), val) for val in self.nodes))

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

    async def broadcast_commit(self, content=None, from_node=None):
        """brodcasts commit to all nodes in the network


        Args:
            content (Dict, optional): json data neccesary for commit message(msg_hash/seq_no/view). Defaults to None.
            from_node (Node, optional): node object sending the commit message. Defaults to None.
        """
        if content:
            others = from_node.get_other_nodes(self.nodes)
            await asyncio.gather(*(self.message_handler(Message(PBFT_Message.COMMIT, from_node, content=content), val) for val in others))

    def broadcast_round_change(self):
        # TODO unfinished round changing - primary
        print(f"********************ROUND-CHANGE********************")
        for validator in self.nodes:
            self.message_handler(
                f"Validator{validator} received ROUND-CHANGE message")

    def is_verified_node(self, node):
        """
        is_verified_node verifies if given Node is verified

        Args:
            node (Node object): tested node

        Returns:
            Bool: True when is verified, otherwise False
        """
        if node in self.nodes:
            return True
        return False

    def is_leader(self, node):
        """
        is_leader checks if given node is current leader

        Args:
            node (Node object): tested node

        Returns:
            Bool: True when is primary, otherwise False
        """
        if node == self.primary_node:
            return True
        return False

    async def message_handler(self, message, recipient):
        """message execution manager function

        Args:
            message (Message object): message object being handled by the PBFT protocol
            recipient (Node object): adressee of the message being handled
        """
        # check if the message is correct
        if not message.verify():
            raise("Unsuccesful verification of the sent message!")

        # only verified nodes can participate
        if not self.is_verified_node(recipient):
            raise("Unsuccesful verification of receiving node!")

        if message.ttype == PBFT_Message.REQUEST:
            if self.verbose:
                if self.is_leader(recipient):
                    print(Fore.CYAN + Back.WHITE +
                          f'- NODE{recipient.id} (INIT) \t\t received message({json.dumps(message.ttype)})' + Style.RESET_ALL)
                else:
                    print(
                        Fore.CYAN + f'- NODE{recipient.id} (INIT) \t\t received message({json.dumps(message.ttype)})')
            # PBFT is going to validate Transaction or new Block
            if isinstance(message.content["consensus_object"], Transaction):
                transaction = message.content["consensus_object"]
                if transaction.verify_transaction():
                    msg_hash = recipient.add_request_to_log(message)
                    # only current leader can start new round by broadcasting pre prepare
                    if self.is_leader(recipient):
                        view, seq = recipient.set_seq_number(msg_hash)
                        content = {"msg_hash": msg_hash,
                                   "seq": seq, "view": view}
                        await self.broadcast_pre_prepare(content=content, from_node=recipient)
                        print(Fore.BLUE + "PBFT END".center(80, '-') +
                              Style.RESET_ALL)
                        proposed_block = recipient.create_block(transaction)
                        await self.validate_block(block=proposed_block, user=recipient)

                else:
                    raise("Unsuccesful verification of sent transaction!")
            if isinstance(message.content["consensus_object"], Block):
                block = message.content["consensus_object"]
                if block.verify_block():
                    msg_hash = recipient.add_request_to_log(message)
                    # only current leader can start new round by broadcasting pre prepare
                    if self.is_leader(recipient):
                        view, seq = recipient.set_seq_number(msg_hash)
                        content = {"msg_hash": msg_hash,
                                   "seq": seq, "view": view}
                        await self.broadcast_pre_prepare(content=content, from_node=recipient)
                        print(Fore.BLUE + "PBFT END".center(80, '-') +
                              Style.RESET_ALL)

        elif message.ttype == PBFT_Message.PRE_PREPARE:
            if self.verbose:
                print(
                    Fore.CYAN + f'- NODE{recipient.id} (PRE-PREPARING)\t received message({json.dumps(message.ttype)})')
            msg_hash = message.content["msg_hash"]
            seq = message.content["seq"]
            view = message.content["view"]
            log = recipient.search_log_msghash(msg_hash)
            # check for existence of request for receiven message hash from pre_prepare message
            if log:
                # node accepts pre prepare if there are not any other hash digests for given seq and view
                if recipient.corresponding_view_seq(view, seq):
                    if self.verbose:
                        print(
                            f"- NODE{recipient.id} (PRE-PREPARED) \t sending prepare messages")
                    await self.broadcast_prepare(content=message.content, from_node=recipient)

        elif message.ttype == PBFT_Message.PREPARE:
            msg_hash = message.content["msg_hash"]
            # received prepares counting
            log = await recipient.received_prepare(msg_hash)
            if self.verbose:
                print(f'- NODE{recipient.id} (PREPARES:{round(log.prepare_count - recipient.weight, 2)}->{round(log.prepare_count, 2)})\t received message({json.dumps(message.ttype)})')
            seq = message.content["seq"]
            view = message.content["view"]
            # wait for enough prepare messages
            if log.prepare_flag and not log.commit_sent:
                log.commit_sent = True
                if self.verbose:
                    print(
                        f"- NODE{recipient.id} (PREPARES:{log.prepare_count})\t\t sending commit messages")
                await self.broadcast_commit(content=message.content, from_node=recipient)

        elif message.ttype == PBFT_Message.COMMIT:
            msg_hash = message.content["msg_hash"]
            # received commits counting
            log = await recipient.received_commit(msg_hash)
            if self.verbose:
                print(
                    Fore.CYAN + f'- NODE{recipient.id} (COMMITS:{round(log.commit_count - recipient.weight,2)}->{round(log.commit_count, 2)})\t received message({json.dumps(message.ttype)})')
            # wait for enough commit messages, to go to another phase
            if log.commit_flag and not log.reply_sent:
                result = None
                # validation of proposed block by given peer
                if isinstance(log.message.content["consensus_object"], Block):
                    result = recipient.verify_block(
                        log.message.content["consensus_object"])
                # execution of the validated operation(feature extraction / matching)
                else:
                    result = recipient.verify_decision(
                        log.message.content["consensus_object"], log.message.content["biometrics"])

                # diferentiate coloring of the print
                if result:
                    if self.verbose:
                        print(
                            Fore.RED + f"- NODE{recipient.id} (COMMITS:{round(log.commit_count,2)})\t\t failed validation!, sending \"REPLY\" message!" + Fore.CYAN)
                    else:
                        print(
                            Fore.RED + f"- NODE{recipient.id} \t\t\t failed validation!, sending \"REPLY\" message!" + Fore.CYAN)
                else:
                    if self.verbose:
                        print(
                            Fore.LIGHTGREEN_EX + f"- NODE{recipient.id} (COMMITS:{round(log.commit_count,2)})\t\t validated!, sending \"REPLY\" message!" + Fore.CYAN)
                    else:
                        print(
                            Fore.LIGHTGREEN_EX + f"- NODE{recipient.id} \t\t\t validated!, sending \"REPLY\" message!" + Fore.CYAN)

                # transmit new message
                log.reply_sent = True
                content = message.content["msg_hash"], result
                reply = Message(PBFT_Message.REPLY, recipient, content)
                await self.message_handler(reply, log.message.sender)

        elif message.ttype == PBFT_Message.REPLY:
            msg_hash, result = message.content
            # received replies counting
            log = await recipient.received_reply(msg_hash, result)

            # diferentiate coloring of the print
            if self.verbose:
                if result:
                    print(f'- NODE{recipient.id} (NEG. REPLIES:{round(log.reply_count_disagree - recipient.weight, 2)}->{round(log.reply_count_disagree,2)})\t received message({json.dumps(message.ttype)})')
                else:
                    print(f'- NODE{recipient.id} (POS. REPLIES:{round(log.reply_count_agree - recipient.weight, 2)}->{round(log.reply_count_agree,2)})\t received message({json.dumps(message.ttype)})')

            # wait for enough reply messages, to go to another phase
            if log.reply_flag and not log.reply_operation_executed:
                print(Fore.LIGHTGREEN_EX +
                      "- Enough replies have been received!" + Style.RESET_ALL)
                recipient.execute_operation(log)
                log.reply_operation_executed = True
