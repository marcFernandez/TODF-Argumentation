import os
import json
import sys
import json
from progressbar import ProgressBar


def proposal_reader(path):
    with open(path, "r") as input_file:
        data = json.load(input_file)
        return data


if __name__ == "__main__":

    comments_dict = {}

    it = 0

    pbar = ProgressBar()

    directory = "/Users/demo/Documents/metadecidim-master/comments/"
    prop_directory = "/Users/demo/Documents/metadecidim-master/proposals/"

    last_prop = "08584"
    changeProp = False

    most_commented_array = []

    for filename in pbar(os.listdir(directory)):
        curr_prop = filename[:5]
        curr_prop_json = proposal_reader(directory + filename)

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
        if curr_prop != '00000':
            curr_prop_metadata = proposal_reader(prop_directory + filename[:5] + '.json')

        if filename[5:8] == '-01' and curr_prop != '00000':
            comments_dict[curr_prop]["info"] = {
                "summary": curr_prop_metadata["proposal"]["summary"],
                "title": curr_prop_metadata["proposal"]["title"],
                "total_comments": curr_prop_metadata["proposal"]["total_comments"],
                "total_negative_comments": curr_prop_metadata["proposal"]["total_negative_comments"],
                "total_neutral_comments": curr_prop_metadata["proposal"]["total_neutral_comments"],
                "total_positive_comments": curr_prop_metadata["proposal"]["total_positive_comments"],
                "total_votes": curr_prop_metadata["proposal"]["total_votes"]
            }

        # if curr_prop != last_prop and curr_prop != '00000':
        #     last_prop = curr_prop
        #     if len(comments_dict[last_prop]["comments"]) > 25 and last_prop != '08584' and curr_prop != '08584':
        #         it += 1
        #         output_file = 'Prop_' + last_prop + '.json'
        #         with open(output_file, 'w') as outfile:
        #             json.dump(comments_dict[last_prop], outfile, indent=4, sort_keys=True)
        #             outfile.close()
                # last_prop = curr_prop

    amount = 0
    n = 40
    arr = []
    for k in comments_dict.keys():
        if len(comments_dict[k]["comments"]) > n:
            amount += 1
            arr.append(k)
            # print k
    arr.sort()
    for i in arr:
        print i
    print "There are "+str(amount)+" proposals with more than "+str(n)+" comments."
