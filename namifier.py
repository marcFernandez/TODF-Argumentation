import json

import comments_processing
from collective_function import *
import sys


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


if __name__ == "__main__":

    results = {}

    with open("PAM_output.txt") as sout:
        for line in sout:
            if "evaluation" in line:
                a = line.replace("\'", "")
                a = a.replace("\n\'", "")
                results[a] = None

    props = proposal_reader('/Users/demo/Documents/metadecidim-master/proposals/00050.json')

    print props['proposal']['total_votes']

    directory = '/Users/demo/Documents/metadecidim-master/comments'

    num_files = 1
    proposal = '00050'

    cp = comments_processing.CommentProcessing(str(directory), results, str(proposal))

    temp_path = directory + '/' + str(proposal) + '-01.json'
    data = cp.comments_dict(temp_path)
    pdata = cp.get_dictionary_v2(data)

    if num_files > 1:
        for i in range(1, num_files + 1):
            temp_path = directory + '/' + str(proposal) + '-0' + str(i) + '.json'
            data = cp.comments_dict(temp_path)
            pdata = cp.get_dictionary_v2(None, pdata)

    cp.comments_dict()

    cp.get_dictionary_v2()

    comments_dict = cp.processed_data

    # print_comment(comments_dict, 1)

    nam_dict, nam_edges = get_graph_dict_nam(comments_dict)

    nam_input = "n,,-1,1\n"

    posIdx = 1
    negIdx = 1

    for arg in nam_dict:
        nam_input += ("true,posarg"+str(posIdx)) if nam_dict[arg]['label'] == const.DEFENCE else ("false,negarg"+str(negIdx))
        if nam_dict[arg]['label'] == const.DEFENCE: posIdx += 1
        else: negIdx += 1
        for _ in range(nam_dict[arg]['votes']['likes']):
            nam_input += ',1'
        for _ in range(nam_dict[arg]['votes']['dislikes']):
            nam_input += ',-1'
        nam_input += '\n'

    if len(sys.argv) != 1:
        if sys.argv[1] == 'print':
            print nam_input

    exit(0)
