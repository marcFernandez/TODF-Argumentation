import json
import comments_processing
from collective_function import *
import sys
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


if __name__ == "__main__":

    file_dict = {}
    directory = "/Users/demo/Documents/metadecidim-master/proposals/"
    f = open('total_votes.txt', 'a')

    most_voted = 0
    most_voted_proposal = ""

    total_votes = 0
    i = 0

    votes_dict = {
        "> 1000    ": 0,
        "900 - 1000": 0,
        "800 - 900": 0,
        "700 - 800": 0,
        "600 - 700": 0,
        "500 - 600": 0,
        "400 - 500": 0,
        "300 - 400": 0,
        "200 - 300": 0,
        "100 - 200": 0,
        "75 - 100 ": 0,
        "50 - 75  ": 0,
        "25 - 50  ": 0,
        "1 - 25   ": 0,
        "0        ": 0
    }

    for filename in os.listdir(directory):
        i += 1
        if filename[:5] != '03608':  # and filename[:5] != '04996' and filename[:5] != '07469':
            file_dict[filename] = proposal_reader(directory+filename)

            curr_votes = file_dict[filename]['proposal']['total_votes']

            if curr_votes > 1000:
                votes_dict["> 1000    "] += 1
            elif curr_votes > 900:
                votes_dict["900 - 1000"] += 1
            elif curr_votes > 800:
                votes_dict["800 - 900"] += 1
            elif curr_votes > 700:
                votes_dict["700 - 800"] += 1
            elif curr_votes > 600:
                votes_dict["600 - 700"] += 1
            elif curr_votes > 500:
                votes_dict["500 - 600"] += 1
            elif curr_votes > 400:
                votes_dict["400 - 500"] += 1
            elif curr_votes > 300:
                votes_dict["300 - 400"] += 1
            elif curr_votes > 200:
                votes_dict["200 - 300"] += 1
            elif curr_votes > 100:
                votes_dict["100 - 200"] += 1
            elif curr_votes > 75:
                votes_dict["75 - 100 "] += 1
            elif curr_votes > 50:
                votes_dict["50 - 75  "] += 1
            elif curr_votes > 25:
                votes_dict["25 - 50  "] += 1
            elif curr_votes > 0:
                votes_dict["1 - 25   "] += 1
            else:
                votes_dict["0        "] += 1

            total_votes += curr_votes

            if curr_votes > most_voted:
                most_voted = curr_votes
                most_voted_proposal = filename
            print >> f, "Proposal "+filename.split('.')[0]+": "+str(curr_votes)+" votes."

    print >> f, "\nMost voted prop "+most_voted_proposal+" has: "+str(most_voted)+" votes."
    print >> f, "Mean votes per proposal: "+str(total_votes/i)
    print >> f, "\nVote interval \tNum votes"
    for k in ["> 1000    ", "900 - 1000", "800 - 900", "700 - 800", "600 - 700", "500 - 600", "400 - 500", "300 - 400",
              "200 - 300", "100 - 200", "75 - 100 ", "50 - 75  ", "25 - 50  ", "1 - 25   ", "0        "]:
        print >> f, k+"\t\t\t"+str(votes_dict[k])  # +"\t\t\t"+str(100*votes_dict[k]/total_votes)+"%"
