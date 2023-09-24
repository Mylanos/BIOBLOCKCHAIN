#: total count of replicas participating in the PBFT network
NUM_PARTICIPATING_NODES = 5 # = 3f + 1

#: maximum number of faulty nodes
MAX_FAULT = (NUM_PARTICIPATING_NODES - 1) // 3

#: minimum weight of prepares needed to enter commit phase
MIN_WEIGHT_PREPARE = 2 / 3

#: minimum weight of commits needed to enter reply phase
MIN_WEIGHT_COMMIT = 2 / 3

#: minimum weight of replies needed to respond to the request
MIN_WEIGHT_REPLY = 2 / 3
