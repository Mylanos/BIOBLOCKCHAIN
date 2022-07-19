#: total count of replica in the whole bioblockchain system
NUM_NODES = 4 # = 3f + 1

#: total count of replicas participating in the PBFT network
NUM_PARTICIPATING_NODES = 4 # = 3f + 1

#: maximum number of faulty nodes
MAX_FAULT = (NUM_PARTICIPATING_NODES - 1) // 3

#: minimum ammount of prepares needed to enter commit phase
MIN_PREPARE = 2 * MAX_FAULT #

#: minimum ammount of commits needed to enter reply phase
MIN_COMMIT = (2 * MAX_FAULT) + 1

#: minimum ammount of replies needed to respond to the request
MIN_REPLY = MAX_FAULT + 1

#: ammount of items in list for round robin looping
ITER_LIST_AMMOUNT = 8 * NUM_NODES

#: minimum weight of prepares needed to enter commit phase
MIN_WEIGHT_PREPARE = 2 / 3

#: minimum weight of commits needed to enter reply phase
MIN_WEIGHT_COMMIT = 2 / 3

#: minimum weight of replies needed to respond to the request
MIN_WEIGHT_REPLY = 2 / 3