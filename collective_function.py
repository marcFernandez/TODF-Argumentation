import matplotlib.pyplot as plt
import networkx as nx

from settings import *


# Returns a list with the nodes from graph 'G' that are attacking the node 'argument'
def attacking(G, argument):
    return [node for node in G if node in G.predecessors(argument) and G.edges[(node, argument)]['label'] == const.ATTACK]


# Returns a list with the nodes from graph 'G' that are defending the node 'argument'
def defending(G, argument):
    return [node for node in G if node in G.predecessors(argument) and G.edges[(node, argument)]['label'] == const.DEFENCE]


# UNCOMMENTED #######################################################################################
def count_labels(G, labelling, arguments, label):
    counter = 0
    for a in arguments:
        if labelling[a] == label:
            counter += 1
    return counter


def pro(G, labelling, argument):
    d = defending(G, argument)
    a = attacking(G, argument)
    return count_labels(G, labelling, d, const.IN) + count_labels(G, labelling, a, const.OUT)


#
def con(G, labelling, argument):
    d = defending(G, argument)
    a = attacking(G, argument)
    return count_labels(G, labelling, a, const.IN) + count_labels(G, labelling, d, const.OUT)


#
def direct_support(profile, argument, label):
    support = 0
    for labeling in profile:
        if labeling[argument] == label:
            support += 1
    return support


# Returns True if the 'labeling' from graph 'G' is coherent, false otherwise
def coherent(G, labelling):
    is_coherent = True
    for argument in G:
        if labelling[argument] == const.IN:
            is_coherent = is_coherent and (pro(G, labelling, argument) >= con(G, labelling, argument))
        elif labelling[argument] == const.OUT:
            is_coherent = is_coherent and (pro(G, labelling, argument) <= con(G, labelling, argument))
        else:
            raise Exception("Argument undec or null")
    return is_coherent


# Returns True
def c_coherent(G, labelling, c):
    is_coherent = True
    for argument in G:
        if labelling[argument] == const.IN:
            is_coherent = is_coherent and (pro(G, labelling, argument) > con(G, labelling, argument) + c)
        elif labelling[argument] == const.OUT:
            is_coherent = is_coherent and (pro(G, labelling, argument) < con(G, labelling, argument) + c)
        else:
            is_coherent = abs(pro(G, labelling, argument) - con(G, labelling, argument)) <= c
    return is_coherent


def get_indirect_opinion(G, labelling, argument):
    pros = pro(G, labelling, argument)
    cons = con(G, labelling, argument)
    if pros > cons:
        return 1
    elif pros < cons:
        return -1
    else:
        return 0


def get_direct_opinion(G, profile, argument):
    direct_positive_support = direct_support(profile, argument, const.IN)
    direct_negative_support = direct_support(profile, argument, const.OUT)
    if direct_positive_support > direct_negative_support:
        return 1
    elif direct_positive_support < direct_negative_support:
        return -1
    else:
        return 0


def majority(G, profile, collective_labelling, argument):
    direct_positive_support = direct_support(profile, argument, const.IN)
    direct_negative_support = direct_support(profile, argument, const.OUT)
    if direct_positive_support > direct_negative_support:
        collective_labelling[argument] = const.IN
    elif direct_positive_support < direct_negative_support:
        collective_labelling[argument] = const.OUT
    else:
        collective_labelling[argument] = const.UNDEC


def OF(G, profile, collective_labelling, argument):
    pros = pro(G, collective_labelling, argument)
    cons = con(G, collective_labelling, argument)
    direct_positive_support = direct_support(profile, argument, const.IN)
    direct_negative_support = direct_support(profile, argument, const.OUT)
    if (direct_positive_support > direct_negative_support) or (
            (pros > cons) and (direct_positive_support == direct_negative_support)):
        collective_labelling[argument] = const.IN
    elif (direct_positive_support < direct_negative_support) or (
            (pros < cons) and (direct_positive_support == direct_negative_support)):
        collective_labelling[argument] = const.OUT
    else:
        collective_labelling[argument] = const.UNDEC


def SF(G, profile, collective_labelling, argument):
    pros = pro(G, collective_labelling, argument)
    cons = con(G, collective_labelling, argument)
    direct_positive_support = direct_support(profile, argument, const.IN)
    direct_negative_support = direct_support(profile, argument, const.OUT)
    if (pros > cons) or ((pros == cons) and (direct_positive_support > direct_negative_support)):
        collective_labelling[argument] = const.IN
    elif (pros < cons) or ((pros == cons) and (direct_positive_support < direct_negative_support)):
        collective_labelling[argument] = const.OUT
    else:
        collective_labelling[argument] = const.UNDEC


def CF(G, profile, collective_labelling, argument):
    indirect_opinion = get_indirect_opinion(G, collective_labelling, argument)
    direct_opinion = get_direct_opinion(G, profile, argument)
    aggregated_opinion = direct_opinion + indirect_opinion
    if aggregated_opinion > 0:
        collective_labelling[argument] = const.IN
    elif aggregated_opinion < 0:
        collective_labelling[argument] = const.OUT
    else:
        collective_labelling[argument] = const.UNDEC


def compute_collective_labelling(G, profile, AF):
    H = G.copy()
    collective_labelling = {}
    toVisit = []
    for n in H.nodes:
        cont = 0
        for _ in H.predecessors(n):
            cont += 1
        if cont == 0:
            toVisit.append(n)
    while toVisit:
        argument = toVisit.pop(0)
        AF(G, profile, collective_labelling, argument)
        successors_list = []
        for suc in H.successors(argument):
            successors_list.append(suc)
        for successor in successors_list:
            H.remove_edge(argument, successor)
            ct = 0
            for _ in H.predecessors(successor):
                ct += 1
            if ct == 0:
                toVisit.append(successor)
    return collective_labelling


def compute_collective_decition(collective_labelling, argument):
    return collective_labelling[argument]


def draw_labelling(G, labelling, target, title,position):

    pos = position

    inNodes = [node for node in G if labelling[node] == const.IN]
    outNodes = [node for node in G if labelling[node] == const.OUT]
    undecNodes = [node for node in G if labelling[node] == const.UNDEC]

    nx.draw_networkx_nodes(G, pos, inNodes, node_size=const.NODE_SIZE, node_color=const.IN_COLOUR)
    nx.draw_networkx_nodes(G, pos, outNodes, node_size=const.NODE_SIZE, node_color=const.OUT_COLOUR)
    nx.draw_networkx_nodes(G, pos, undecNodes, node_size=const.NODE_SIZE, node_color=const.UNDEC_COLOUR)

    nx.draw_networkx_edges(G, pos)

    attackEdges = [(u, v) for (u, v) in G.edges() if G[u][v]['color'] == const.ATTACK_COLOUR]
    nx.draw_networkx_edges(G, pos, attackEdges, width=4, alpha=0.25, edge_color=const.ATTACK_COLOUR)

    defenceEdges = [(u, v) for (u, v) in G.edges() if G[u][v]['color'] == const.DEFENCE_COLOUR]
    nx.draw_networkx_edges(G, pos, defenceEdges, width=4, alpha=0.25, edge_color=const.DEFENCE_COLOUR)


    labels={}
    noTargets = [node for node in G if not node == target]
    for node in noTargets:
        labels[node] = r'$a' + str(node) + '$'
    labels[target]=r'$\tau$'

    nx.draw_networkx_labels(G,pos,labels,font_size=const.LABEL_FONT_SIZE)

    plt.title('Labeling : ' + title)
    plt.axis('off')
    plt.show()


def drawProfile(G, profile, target, titles, position, justResult=False):

    iterTitles = iter(titles)

    if justResult:
        print "profiles: "+str(len(profile))
        profile = [profile[len(profile)-1]]

    for labelling in profile:

        inNodes = [node for node in G if labelling[node] == const.IN]
        outNodes = [node for node in G if labelling[node] == const.OUT]
        undecNodes = [node for node in G if labelling[node] == const.UNDEC]

        print inNodes

        plt.figure()

        pos = position

        nx.draw_networkx_nodes(G, pos, inNodes, node_size = const.NODE_SIZE, node_color= const.IN_COLOUR)

        nx.draw_networkx_nodes(G, pos, outNodes, node_size=const.NODE_SIZE, node_color=const.OUT_COLOUR)

        nx.draw_networkx_nodes(G, pos, undecNodes, node_size=const.NODE_SIZE, node_color= const.UNDEC_COLOUR)

        # edges
        nx.draw_networkx_edges(G, pos)

        attackEdges = [(u, v) for (u, v) in G.edges() if G[u][v]['color'] == const.ATTACK_COLOUR]
        nx.draw_networkx_edges(G, pos, attackEdges, width=4, alpha=0.25, edge_color=const.ATTACK_COLOUR)

        defenceEdges = [(u, v) for (u, v) in G.edges() if G[u][v]['color'] == const.DEFENCE_COLOUR]
        nx.draw_networkx_edges(G, pos, defenceEdges, width=4, alpha=0.25, edge_color=const.DEFENCE_COLOUR)

        labels = {}
        noTargets = [node for node in G if not node == target]
        for node in noTargets:
            labels[node] = r'$a' + str(node) + '$'
        labels[target]=r'$\tau$'

        nx.draw_networkx_labels(G, pos, labels, font_size=const.LABEL_FONT_SIZE)

        plt.title('Labeling : ' + next(iterTitles))
        plt.axis('off')
    plt.show()
