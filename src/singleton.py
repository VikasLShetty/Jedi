#!/usr/bin/env python

"""
Use this file for all Singleton instances that you need throughout the project
"""

# - Global variables that we will be changing through out the program
# - The structure of graph_extern looks like this
# - graph_extern = [[2, 3, 4], [1, 3, 4], [1, 2, 4], [1, 2, 3]]
graph_extern = []

# - Constants that we won't be changing
NUM_SWITCHES = 4
BANDWIDTHS = [50, 60, 70, 80, 90, 100, 110, 120, 130, 140]

# - ZooKeeper specific constants
HOST_PORT_COMBO = "127.0.0.1:2181"
LOCK_PATH = "/admins/vote"