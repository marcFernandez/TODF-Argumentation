import json
from collective_function import *
from generator import *


class CommentProcessing:

    def __init__(self, path):
        self.path = path
        self.profile = []
        self.titles = []
        self.G = nx.DiGraph()
        self.comments_omitted = 0
        self.attacking = 0
        self.defending = 0
        self.undec = 0
        self.res = ""

    # This method returns the profile, which is a list of all labellings that we need to represent our data graphically
    # and its titles. Each one of this labellings are not necessary the opinion of a single target, but that's fair
    # enough for our purposes.
    def get_profile(self, data):
        d = data
        d_copy = d.copy()
        num_labels = 0
        labeling = {}

        for k in d_copy.keys():
            if num_labels < d_copy[k]['data']['total_votes']:
                num_labels = d_copy[k]['data']['total_votes']
            labeling[k] = const.UNDEC

        # print "We need", num_labels, "labellings"
        current_label = 1

        while current_label <= num_labels:
            for k in d_copy.keys():
                if d_copy[k]['data']['total_likes'] > 0:
                    labeling[k] = const.IN
                    d_copy[k]['data']['total_likes'] -= 1
                elif d_copy[k]['data']['total_dislikes'] > 0:
                    labeling[k] = const.OUT
                    d_copy[k]['data']['total_dislikes'] -= 1
                else:
                    labeling[k] = const.UNDEC
            self.profile.append(labeling.copy())
            current_label += 1

        for i in range(1, num_labels + 1):
            self.titles.append('L' + str(i))

        if di:
            return self.profile, self.titles

    # Shows the dictionary 'd'
    def show(self, di=None):
        d = self.processed_data if di is None else di
        for key in d.keys():
            print key, ":", d[key]

    # Generates the graph resulting from 'd' and returns it
    def get_graph(self, di=None):
        d = self.processed_data if di is None else di
        calc = False
        for k in d.keys():
            if k is not 0:  # and d[k]['data']['label'] != 0:
                self.G.add_node(k, label=const.UNDEC)
                if d[k]['ancestry'] is not None:
                    # So here we assume that an answer comment is always attacking its target comment due to the fact
                    # that we don't have further information about its alignment
                    self.G.add_edge(k, d[k]['ancestry'], color=const.ATTACK_COLOUR, label=const.ATTACK)
                    ct = 0
                    node = k
                    while d[node]['ancestry'] is not None:
                        ct += 1
                        node = d[node]['ancestry']
                    att = True if d[node]['data']['label'] == -1 else False
                    if (ct % 2) != 0:  # even
                        att = not att
                    if att:
                        # print "Comment", k, "is attacking"
                        self.attacking += 1
                    else:
                        # print "Comment", k, "is defending"
                        self.defending += 1
                else:
                    if d[k]['data']['label'] == 1:
                        c = const.DEFENCE_COLOUR
                        l = const.DEFENCE
                        self.defending += 1
                        calc = True
                    elif d[k]['data']['label'] == -1:
                        c = const.ATTACK_COLOUR
                        l = const.ATTACK
                        self.attacking += 1
                        calc = True
                    else:
                        self.comments_omitted += 1
                        self.undec += 1
                        # print "Argument", k, \
                        #     "is considered defensive against the target although it's alignment is not defined."
                    if d[k]['data']['label'] != 0:
                        self.G.add_edge(k, 0,
                                   color=const.DEFENCE_COLOUR if d[k]['data']['label'] != -1 else const.ATTACK_COLOUR,
                                   label=const.DEFENCE if d[k]['data']['label'] != -1 else const.ATTACK)
        if di:
            return self.G, self.comments_omitted, self.attacking, self.defending, self.undec, calc
        else:
            return calc

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

    def write_output(self, propo=None, a=None, d=None, u=None, r=None, result=const.UNDEC):
        # the 'result' label will only be UNDEC by default if the graph does not contain any node defending nor
        # attacking the target
        prop = self.prop if propo is None else propo
        attack = self.attacking if a is None else a
        defend = self.defending if d is None else d
        undec = self.undec if u is None else u
        results = self.results if r is None else r
        total = attack + defend + undec
        eval = 0
        avg_eval = 0
        if total != 0:
            self.res = "Proposal " + str(prop) + ":\n"
            self.res += "Attack comments: " + str(attack) + " (" + str(attack * 100 / total) + "%)\n"
            self.res += "Defend comments: " + str(defend) + " (" + str(defend * 100 / total) + "%)\n"
            self.res += "Undec comments: " + str(undec) + " (" + str(undec * 100 / total) + "%)\n"
            self.res += "Total comments: " + str(total) + "\n"
            self.res += "Proposal TODF evaluation: " + result + "\n"
            for r in results.keys():
                if "Proposal " + str(prop) + " evaluation" in r:
                    val = r.split(':', 1)
                    if 'average:NaN' not in str(r):
                        if 'average:' in str(r):
                            avg_eval = float(val[1])
                        else:
                            eval = float(val[1])
                    self.res += r
        else:
            self.res = "Proposal " + str(prop) + ":\n"
            self.res += "Attack comments: " + str(0) + "\n"
            self.res += "Defend comments: " + str(0) + "\n"
            self.res += "Undec comments: " + str(0) + "\n"
            self.res += "Total comments: " + str(0) + "\n"
            self.res += "Proposal TODF evaluation: " + result + "\n"
            for r in results.keys():
                if "Proposal " + str(prop) + " evaluation" in r:
                    self.res += r

        # if 'evaluation: NaN' in res or 'average:NaN' in res and :
        #     pass
        if 'average:NaN' in self.res:
            self.avg_nan_count += 1
        else:  # compare results with the 3 different methods
            if self.compare(1, avg_eval, eval, result, prop, self.res):
                self.res += "PAM and TODF methods: MATCH\n"
                self.wo_todf_compare_match += 1
            else:
                self.res += "PAM and TODF methods: MISMATCH\n"
                self.wo_todf_compare_mismatch += 1

            if self.compare(2, avg_eval, eval, result, prop, self.res):
                self.res += "AVG and TODF methods: MATCH\n"
                self.avg_todf_compare_match += 1
            else:
                self.res += "AVG and TODF methods: MISMATCH\n"
                self.avg_todf_compare_mismatch += 1
        if propo:
            return self.res

    def compare(self, type, avg, wo, todf, prop, res):
        if type == 1:  # WO and TODF
            if not wo or str(wo) == 'nan' or 1 <= wo <= 2 and todf == const.OUT:
                # there are some cases where avg is not NaN but wo is, so we make that this doesn't count as a mismatch
                return True
            elif 2 < wo < 4 and todf == const.UNDEC:
                return True
            elif wo >= 4 and todf == const.IN:
                return True
            else:
                if 1 <= wo <= 2.5 and todf == const.OUT:
                    self.wo_todf_expanding += 1
                elif 1.5 < wo < 4.5 and todf == const.UNDEC:
                    self.wo_todf_expanding += 1
                elif wo >= 3.5 and todf == const.IN:
                    self.wo_todf_expanding += 1
                else:
                    if prop in self.hard_mismatches.keys():
                        self.hard_mismatches[prop] += "PAM and TODF methods: MISMATCH\n"
                    else:
                        self.hard_mismatches[prop] = res + "PAM and TODF methods: MISMATCH\n"
                    return False
                return False
        elif type == 2:  # TODF and AVG
            if 1 <= avg <= 2 and todf == const.OUT:
                return True
            elif 2 < avg < 4 and todf == const.UNDEC:
                return True
            elif avg >= 4 and todf == const.IN:
                return True
            else:
                if 1 <= avg <= 2.5 and todf == const.OUT:
                    self.avg_todf_expanding += 1
                elif 1.5 < avg < 4.5 and todf == const.UNDEC:
                    self.avg_todf_expanding += 1
                elif avg >= 3.5 and todf == const.IN:
                    self.avg_todf_expanding += 1
                else:
                    if prop in self.hard_mismatches.keys():
                        self.hard_mismatches[prop] += "AVG and TODF methods: MISMATCH\n"
                    else:
                        if "PAM and TODF methods: MISMATCH" in res:
                            banana = res.split('\n')[:-2]
                            res = ""
                            for s in banana:
                                res += s + '\n'
                        self.hard_mismatches[prop] = res + "AVG and TODF methods: MISMATCH\n"
                    return False
                return False
        else:
            pass
