import json

import comments_processing
from collective_function import *
import sys
import re
import os

# 09604, 01425, 04826, 00408, 06038

# Constructs 2 dictionaries:
#   - nam_dict = dictionary that stores the information about each comment, its votes and its alignment.
#                Here I assume that a comment
def get_graph_dict_nam(d):
    nam_dict = {}
    nam_edges = {}
    for k in d.keys():
        if k is not 0:  # and d[k]['data']['label'] != 0:
            nam_dict[k] = {
                "votes": {
                    "likes": d[k]['data']['total_likes'],
                    "dislikes": d[k]['data']['total_dislikes'],
                    "total": d[k]['data']['total_votes']
                }
            }
            if d[k]['ancestry'] is not None:
                # So here we assume that an answer comment is always attacking its target comment due to the fact
                # that we don't have further information about its alignment
                nam_edges[(k, d[k]['ancestry'])] = const.ATTACK
                ct = 0
                node = k
                while d[node]['ancestry'] is not None:
                    ct += 1
                    node = d[node]['ancestry']
                att = True if d[node]['data']['label'] == -1 else False
                if (ct % 2) != 0:  # even
                    att = not att
                nam_dict[k]["label"] = const.ATTACK if att else const.DEFENCE
            else:
                # Here I consider that a comment without alignment is attacking the proposal
                nam_dict[k]["label"] = const.DEFENCE if d[k]['data']['label'] == 1 else const.ATTACK
                nam_edges[(k, 0)] = const.ATTACK if nam_dict[k]["label"] == const.ATTACK else const.DEFENCE
    return nam_dict, nam_edges


def print_comment(d, idx):
    str_res = "\n"
    for comment in d.keys():
        str_res += str(comment) + "\n"
        for k in d[comment]:
            if k != 'data':
                str_res += str(k) + ": " + str(d[comment][k]) + "\n"
            else:
                str_res += str(k) + ":"
                for data in d[comment][k]:
                    str_res += "\t" + str(data) + " = " + str(d[comment][k][data]) + "\n"
        str_res += "&&&\n"

    print str_res.split('&&&')[idx]


def proposal_reader(path):
    with open(path, "r") as input_file:
        data = json.load(input_file)
        return data


alpha = 0.3
llindar = 5


if __name__ == "__main__":

    PAM_results = {}
    TODF_results = {}
    total_votes = {}

    with open("PAM_output.txt") as sout:
        for line in sout:
            if re.match(r"Proposal \d{5} evaluation:", line):
                spl = line.split(' ')
                prop = spl[1]
                val = -1.5 + 0.5*float(spl[3])
                PAM_results[prop] = val

    directory = "/Users/demo/Documents/metadecidim-master/proposals/"
    file_dict = {}

    for filename in os.listdir(directory):
        if filename[:5] != '08584' and filename[:5] != '10430':
            file_dict[filename] = proposal_reader(directory+filename)
            prop = filename[:5]
            curr_votes = file_dict[filename]['proposal']['total_votes']

            total_votes[prop] = curr_votes

            TODF_results[prop] = min((curr_votes/llindar)*(1+alpha)-1, 1)

    result_dict = {}
    f = open('opposite_proposals.txt', 'a')

    opp_cnt = 0
    for prop in TODF_results.keys():
        result_dict[prop] = TODF_results[prop] + PAM_results[prop]
        if result_dict[prop] == 0 and (TODF_results[prop] != 0 or PAM_results[prop] != 0):
            print >> f, "Proposal "+str(prop)+" has "+str(total_votes[prop])+" votes:"
            print >> f, "\tIO: "+str(PAM_results[prop])
            print >> f, "\tDO: " + str(TODF_results[prop])
            opp_cnt += 1

    print >> f, "\nTotal opposite proposals: "+str(opp_cnt)

    exit(0)
