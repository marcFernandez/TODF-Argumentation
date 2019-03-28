__author__ = 'jar'

import networkx as nx
import random
import const


def generateRadomDAG(nodes, pEdgeGeneration, nodeLabel, edgeLabels):
    G = nx.gnp_random_graph(nodes, pEdgeGeneration, directed=True)
    DAG = nx.DiGraph([(u, v, {'label': random.choice(edgeLabels)}) for (u, v) in G.edges() if u < v])
    if nx.is_directed_acyclic_graph(DAG):
        targets = [n for n, d in DAG.out_degree().items() if d == 0]
        if len(targets) > 1:
            newNodeId = DAG.number_of_nodes()
            DAG.add_node(newNodeId)
            for u in targets:
                DAG.add_edge(u,newNodeId)
                DAG[u][newNodeId]['label'] = random.choice(edgeLabels)
        nx.set_node_attributes(DAG, 'label', nodeLabel)
        for (u,v) in DAG.edges():
            if DAG[u][v]['label'] == const.ATTACK:
                DAG[u][v]['label'] = const.ATTACK_COLOUR
            else:
                DAG[u][v]['label'] = const.ATTACK_COLOUR
        return DAG
    return None


def generateProfile(DAG, numberOfLabellings, labels):
    profile = []
    for i in range(numberOfLabellings):
        newProfile = {}
        for u in DAG.nodes():
            newProfile[u] = random.choice(labels)
        profile.append(newProfile)
    return profile