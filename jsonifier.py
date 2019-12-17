import os
import json
import sys
import json


def proposal_reader(path):
    with open(path, "r") as input_file:
        data = json.load(input_file)
        return data


if __name__ == "__main__":

    comments_dict = {}

    directory = "/Users/demo/Documents/metadecidim-master/comments/"
    prop_directory = "/Users/demo/Documents/metadecidim-master/proposals/"

    for filename in ['00400-01.json', '00400-02.json']:  # os.listdir(directory):
        curr_prop = filename[:5]
        curr_prop_json = proposal_reader(directory + filename)

        if len(curr_prop_json["comments"]) != 0:
            continue

        try:
            comments_dict[curr_prop]
        except KeyError:
            comments_dict[curr_prop] = {"comments": []}
        # if not comments_dict[curr_prop]:  # Here we already have some data inside the dictionary
        #     comments_dict[curr_prop] = {"comments": []}

        for comment in curr_prop_json["comments"]:
            comments_dict[curr_prop]["comments"].append({
                "alignment": comment["alignment"],
                "modified_alignment": 99,
                "ancestry": None,
                "body": comment["body"],
                "total_dislikes": comment["total_dislikes"],
                "total_likes": comment["total_dislikes"],
                "total_votes": comment["total_votes"]
            })

        curr_prop_metadata = proposal_reader(prop_directory + filename[:5] + '.json')

        if filename[5:8] == '-01':
            comments_dict[curr_prop]["info"] = {
                "summary": curr_prop_metadata["proposal"]["summary"],
                "title": curr_prop_metadata["proposal"]["title"],
                "total_comments": curr_prop_metadata["proposal"]["total_comments"],
                "total_negative_comments": curr_prop_metadata["proposal"]["total_negative_comments"],
                "total_neutral_comments": curr_prop_metadata["proposal"]["total_neutral_comments"],
                "total_positive_comments": curr_prop_metadata["proposal"]["total_positive_comments"],
                "total_votes": curr_prop_metadata["proposal"]["total_votes"]
            }

    output_file = 'prop_'+curr_prop+'.json'
    with open(output_file, 'w') as outfile:
        json.dump(comments_dict[curr_prop], outfile, indent=4, sort_keys=True)

        # "summary": "Prioritzar actuacions per millorar la mobilitat al barri de la Font d\u2019en Fargues.",
        # "title": "Urbanitzaci\u00f3 de la davallada de Gallecs",
        # "total_comments": 33,
        # "total_negative_comments": 0,
        # "total_neutral_comments": 4,
        # "total_positive_comments": 29,
        # "total_votes": 146,
