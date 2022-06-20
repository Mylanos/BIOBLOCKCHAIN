#: maximum number of transactions that can be present in a block and transaction pool
TRANSACTION_THRESHOLD = 10

#: total replica count in the PBFT network
NUM_NODES = 4 # = 3f + 1

#: maximum number of faulty nodes
MAX_FAULT = (NUM_NODES - 1) // 3

#: minimum ammount of prepares needed to enter commit phase
MIN_PREPARE = 2 * MAX_FAULT #

#: minimum ammount of commits needed to enter reply phase
MIN_COMMIT = (2 * MAX_FAULT) + 1

#: minimum ammount of replies needed to respond to the request
MIN_REPLY = MAX_FAULT + 1