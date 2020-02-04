import copy
import json

import tfg_comments_processing
from tfg_collective_function import *
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


# {
#     "alignment": 1,
#     "ancestry": null,
#     "body": "blah blah",
#     "id": 1969,
#     "modified_alignment": 1,
#     "total_dislikes": 0,
#     "total_likes": 0,
#     "total_votes": 4
# },
def comments_to_dict(comments_array):
    comments_dict = dict()
    for comment_obj in comments_array:

        ancestry = str(comment_obj['ancestry']).replace("u\'", "").replace("\'", "")
        anc = ancestry.split("/")[len(ancestry.split("/")) - 1]

        comments_dict[comment_obj['id']] = {
            "alignment": comment_obj['alignment'],
            "ancestry": int(anc) if comment_obj['ancestry'] else 0,
            "successors": [],
            "body": comment_obj['body'],
            "id": comment_obj['id'],
            "modified_alignment": comment_obj['modified_alignment'],
            "total_dislikes": comment_obj['total_dislikes'],
            "total_likes": comment_obj['total_votes'] - comment_obj['total_dislikes'],
            "total_votes": comment_obj['total_votes']
        }

    comments_dict[0] = {
        'successors': [],
        'ancestry': None,
        "total_dislikes": None,
        "total_likes": None,
        "total_votes": None
    }

    return comments_dict


def save_json(filename, json_data):
    with open(filename, 'w') as outfile:
        json.dump(json_data, outfile, indent=4, sort_keys=True)
        outfile.close()
    print('''File {filename} saved!''')


PATH = 'D:\\INFO\\Projects\\TODF-Argumentation\\ProcessedProposals'
CURRENT_PROP = 'Prop_01256.json'


if __name__ == "__main__":

    # First of all we read the data from a json file
    raw_data = proposal_reader(PATH+'/'+CURRENT_PROP)

    # We then store each field in a separated variable
    proposal_info = raw_data['info']
    comments_array = raw_data['comments']

    # We then get the comments dictionary with all the relevant information we will use
    comments_dict = comments_to_dict(comments_array)

    decision_results = copy.deepcopy(comments_dict)

    # Then we define a variable for each type of comment we will convert into a PAM comment
    defending_comments = list()
    attacking_comments = list()
    undecided_comments = list()

    cp = tfg_comments_processing.CommentProcessing()

    cp.get_profile(comments_dict)

    comments_graph = cp.get_graph(comments_dict)

    collective_labelling = compute_collective_labelling(cp.G, cp.profile, CF)

    if collective_labelling == {}:
        print "There are no comments, exiting."
        exit(0)

    # print collective_labelling

    decision = compute_collective_decition(collective_labelling, 0)

    cp.profile.append(collective_labelling)
    cp.titles.append('Collective decision')

    ###############################################

    positions = {1: {0: (0.5, 1)}}
    pos_fixed = {1: [0]}
    px = 0

    for node in cp.G.nodes():
        if cp.G.has_predecessor(0, node):
            positions[1][node] = (px - 1, 0.5)
            pos_fixed[1].append(node)
            px += 0.5


    def recursive_positioning(G, node, lvl, i):
        try:
            pos_fixed[lvl].append(node)
            positions[lvl][node] = (positions[lvl - 1][G.succ[node].keys()[0]][0] + i / 1.75,
                                    positions[lvl - 1][G.succ[node].keys()[0]][1] - 0.5)
        except KeyError:
            pos_fixed[lvl] = [node]
            positions[lvl] = {node: (positions[lvl - 1][G.succ[node].keys()[0]][0] + i / 1.75,
                                     positions[lvl - 1][G.succ[node].keys()[0]][1] - 0.5)}
        ct = 0
        for succ in G.predecessors(node):
            recursive_positioning(cp.G, succ, lvl + 1, ct)
            ct += 1


    for node in pos_fixed[1]:
        cct = 0
        for succ in cp.G.predecessors(node):
            recursive_positioning(cp.G, succ, 2, cct)
            cct += 1

    positions[1][0] = (0.5 + px / 2, 1)

    final_pos = {}
    for pos_dict in positions.values():
        final_pos.update(pos_dict)
    final_fixed = []
    for _list in pos_fixed.values():
        final_fixed += _list

    pos = nx.spring_layout(cp.G, pos=final_pos, fixed=final_fixed)

    print cp.profile[len(cp.profile)-1]

    decision = cp.profile[len(cp.profile)-1]

    # drawProfile(cp.G, cp.profile, 0, cp.titles, pos)

    for comment_id in decision.keys():
        decision_results[comment_id]['result'] = decision[comment_id]

    decision_results[0]['total_likes'] = proposal_info['total_votes']

    save_json('results_'+CURRENT_PROP, decision_results)

    exit(0)
