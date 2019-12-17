import os
import json
import sys


def proposal_reader(path):
    with open(path, "r") as input_file:
        data = json.load(input_file)
        return data


if __name__ == "__main__":

    votes_dict = {}

    directory = "/Users/demo/Documents/metadecidim-master/comments/"

    for filename in os.listdir(directory):
        curr_prop = filename[:5]
        curr_prop_json = proposal_reader(directory + filename)

        try:
            votes_dict[curr_prop]
        except KeyError:
            votes_dict[curr_prop] = 0
        finally:
            for comment in curr_prop_json["comments"]:
                votes_dict[curr_prop] += comment["total_votes"]

    prop_num = int(sys.argv[1])
    prop_votes_array = []

    for prop in votes_dict.keys():
        prop_votes_array.append((prop, votes_dict[prop]))

    prop_votes_array.sort(key=lambda tup: tup[1], reverse=True)

    print str(prop_votes_array[:prop_num])
