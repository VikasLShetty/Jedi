#!/usr/bin/env python

"""
Use this file for all Singleton instances that you need throughout the project
"""

import networkx as nx

# - Constants that we won't be changing
RUN_FIRSTTIME=1
NUM_SWITCHES = 5
BANDWIDTHS = [50, 60, 70, 80, 90, 100, 110, 120, 130, 140]

# - Global variables that we will be changing through out the program
# - The structure of graph_extern looks like this
# - graph_extern = [[2, 3, 4], [1, 3, 4], [1, 2, 4], [1, 2, 3]]
graph_extern = nx.Graph()
mininetswitch = [0 for i in range(NUM_SWITCHES + 1)]

# - ZooKeeper specific constants
HOST_PORT_COMBO = "127.0.0.1:2181"
LOCK_PATH = "/admins/vote"
DATA_PATH = "/admins/data"

# - Library functions used by many modules
def netshortestpath(start, end, path=[]):
    path = nx.single_source_dijkstra_path(graph_extern, start)
    return path[end]

def get_weight(path):
    weight = 10000
    for i in range(len(path)):
        if((i+1)<len(path)):
            weight +=  graph_extern[path[i]][path[i+1]]['weight']
    return weight

def convertToConfig(byte_data):
    # Start with a default path that is an empty list and a score that is 0
    path = []
    score = 0
    byte_data = str(byte_data.decode("utf-8"))

    if byte_data:
        byte_data = byte_data.replace("[", "")
        byte_data = byte_data.replace("]", "")
        byte_data = byte_data.replace("(", "")
        byte_data = byte_data.replace(")", "")

        nodes = map(str.strip, byte_data.split(","))
        score = int(nodes.pop())
        path = ", ".join(nodes)

    return (path, score)
