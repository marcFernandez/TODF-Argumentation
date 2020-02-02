import json
from collective_function import *
from generator import *


class CommentProcessing:

    def __init__(self):
        self.profile = []
        self.titles = []
        self.G = nx.DiGraph()

    # This method returns the profile, which is a list of all labellings that we need to represent our data graphically
    # and its titles. Each one of this labellings are not necessary the opinion of a single target, but that's fair
    # enough for our purposes.
    def get_profile(self, data):
        d = data
        d_copy = d.copy()
        num_labels = 0
        labeling = {}

        for k in d_copy.keys():
            if num_labels < d_copy[k]['total_votes']:
                num_labels = d_copy[k]['total_votes']
            labeling[k] = const.UNDEC

        print "We need", num_labels, "labellings"
        current_label = 1

        while current_label <= num_labels:
            for k in d_copy.keys():
                if d_copy[k]['total_likes'] > 0:
                    labeling[k] = const.IN
                    d_copy[k]['total_likes'] -= 1
                elif d_copy[k]['total_dislikes'] > 0:
                    labeling[k] = const.OUT
                    d_copy[k]['total_dislikes'] -= 1
                else:
                    labeling[k] = const.UNDEC
            self.profile.append(labeling.copy())
            current_label += 1

        for i in range(1, num_labels + 1):
            self.titles.append('L' + str(i))

    # Generates the graph resulting from 'data' and returns it
    def get_graph(self, d):
        self.G.add_node(0, label=const.UNDEC)
        for k in d.keys():
            if k is not 0:
                self.G.add_node(k, label=const.UNDEC)
                if d[k]['modified_alignment'] == 1:
                    c = const.DEFENCE_COLOUR
                    l = const.DEFENCE
                elif d[k]['modified_alignment'] == -1:
                    c = const.ATTACK_COLOUR
                    l = const.ATTACK
                else:
                    c = const.UNDEC_COLOUR
                    l = const.UNDEC
                self.G.add_edge(
                    k, d[k]['ancestry'],
                    color=c,
                    label=l
                )
        return self.G

    def show_stats(self, a=None, d=None, u=None):
        attack = self.attacking if a is None else a
        defend = self.defending if d is None else d
        undec = self.undec if u is None else u
        total = attack + defend + undec
        if total != 0:
            print "Attack comments:", attack, "(" + str(attack * 100 / total), "%)"
            print "Defend comments:", defend, "(" + str(defend * 100 / total), "%)"
            print "Undec comments:", undec, "(" + str(undec * 100 / total), "%)"
            print "Total comments:", total
        else:
            print "Total comments: 0"
