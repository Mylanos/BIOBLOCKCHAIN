#maximum number of transactions that can be present in a block and transaction pool
TRANSACTION_THRESHOLD = 10

#total replica count in the network
NUM_NODES = 4 # = 3f + 1

#maximum number of  node
MAX_FAULT = (NUM_NODES - 1) // 3
MIN_PREPARE = 2 * MAX_FAULT # 
MIN_COMMIT = (2 * MAX_FAULT) + 1
MIN_REPLY = MAX_FAULT + 1