#! /usr/bin/env python3
import time
from bioblockchain.config import VIEW_SET_INTERVAL


class View:
    def __init__(self, view_number, num_nodes):
        self._view_number = view_number
        self._num_nodes = num_nodes
        self._leader = view_number % num_nodes
        # Minimum interval to set the view number
        self._min_set_interval = VIEW_SET_INTERVAL
        self._last_set_time = time.time()

    # To encode to json
    def get_view(self):
        return self._view_number 

    # Recover from json data.
    def set_view(self, view):
        '''
        Retrun True if successfully update view number
        return False otherwise.
        '''
        if time.time() - self._last_set_time < self._min_set_interval:
            return False
        self._last_set_time = time.time()
        self._view_number = view
        self._leader = view % self._num_nodes
        return True

    def get_leader(self):
        return self._leader