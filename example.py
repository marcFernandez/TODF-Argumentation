import comments_processing
from collective_function import *
import sys
import os

# To use this file, you need to run:
#       file.py path [proposal] [proposal_num_files]
#
# where:
#       'path' is the path to all comment files directory
#       'proposal' is the proposal you want to analise
#       'proposal_num_files' is the number of files from the same proposal
# the last 2 parameters are optional for the case that you want to analise only a specific proposal.

if __name__ == "__main__":

    results = {}
    with open("NAM_output.txt") as sout:
        for line in sout:
            if "evaluation" in line:
                a = line.replace("\'", "")
                a = a.replace("\n\'", "")
                results[a] = None

    if len(sys.argv) != 2 and len(sys.argv) != 4:
        print "Use:\nfile.py path [proposal] [proposal_num_files]"
        exit(0)

    directory = sys.argv[1]

    if len(sys.argv) == 4:
        num_files = int(sys.argv[3])
        proposal = str(sys.argv[2])

        cp = comments_processing.CommentProcessing(str(directory), results, str(proposal))

        # directory = 'D:\INFO\metadecidim-master\metadecidim-master\comments'
        # '/home/marc/Desktop/metadecidim-master/comments'
        cp.comments_dict()

        cp.get_dictionary_v2()

        cp.show()

        calc = cp.get_graph()

        # print nx.is_tree(G)
        cp.show_stats()

        cp.get_profile()

        collective_labelling = compute_collective_labelling(cp.G, cp.profile, CF)
        decision = compute_collective_decition(collective_labelling, 0)

        cp.profile.append(collective_labelling)
        cp.titles.append('Collective decision')
        pos = nx.spring_layout(cp.G)

        drawProfile(cp.G, cp.profile, 0, cp.titles, pos)

    else:

        file_dict = {}
        avg_nan_count = 0.
        avg_todf_compare_match = 0.
        avg_todf_compare_mismatch = 0.
        wo_todf_compare_match = 0.
        wo_todf_compare_mismatch = 0.
        wo_todf_expanding = 0.
        avg_todf_expanding = 0.
        hard_mismatches = {}

        for filename in os.listdir(directory):
            if filename[:5] != '03608':  # and filename[:5] != '04996' and filename[:5] != '07469':
                if filename[:5] not in file_dict.keys():
                    file_dict[filename[:5]] = {filename: None}
                else:
                    file_dict[filename[:5]][filename] = None

        f = open('output.txt', 'a')
        f_mismatches = open('hard_mismatches.txt', 'a')

        it = 0

        for key in file_dict.keys():
            it += 1
            if file_dict[key].__len__() == 1:
                cp = comments_processing.CommentProcessing(directory, results, None, avg_nan_count,
                                                           avg_todf_compare_match, avg_todf_compare_mismatch,
                                                           wo_todf_compare_match, wo_todf_compare_mismatch,
                                                           wo_todf_expanding, avg_todf_expanding, hard_mismatches)
                # print "we are in proposal:", key
                data = cp.comments_dict(directory + '/' + file_dict[key].keys()[0])
                pdata = cp.get_dictionary_v2(data)
                # cp.show()
                G, omitted, a, d, un, calc = cp.get_graph(pdata)
                if calc:
                    profile, all_titles = cp.get_profile(pdata)
                    collective_labelling = compute_collective_labelling(cp.G, profile, CF)
                    decision = compute_collective_decition(collective_labelling, 0)
                    profile.append(collective_labelling)
                    all_titles.append('Collective decision')
                    pos = nx.spring_layout(cp.G)
                    # drawProfile(G, profile, 0, all_titles, pos)
                    print >> f, cp.write_output(key, a, d, un, cp.results, collective_labelling[0])
                else:
                    print >> f, cp.write_output(key, a, d, un, cp.results)
                # try:
                #     profile, all_titles = get_profile(pdata)
                #     collective_labelling = compute_collective_labelling(G, profile, CF)
                #     decision = compute_collective_decition(collective_labelling, 0)
                #     profile.append(collective_labelling)
                #     all_titles.append('Collective decision')
                #     pos = nx.spring_layout(G)
                #     # drawProfile(G, profile, 0, all_titles, pos)
                #     print >> f, write_output(key, a, d, un, results, collective_labelling[0])
                # except KeyError:
                #     print >> f, write_output(key, a, d, un, results)
                avg_nan_count = cp.avg_nan_count
                avg_todf_compare_match = cp.avg_todf_compare_match
                avg_todf_compare_mismatch = cp.avg_todf_compare_mismatch
                wo_todf_compare_match = cp.wo_todf_compare_match
                wo_todf_compare_mismatch = cp.wo_todf_compare_mismatch
                wo_todf_expanding = cp.wo_todf_expanding
                avg_todf_expanding = cp.avg_todf_expanding
                hard_mismatches = cp.hard_mismatches
            else:
                cp = comments_processing.CommentProcessing(directory, results, None, avg_nan_count,
                                                           avg_todf_compare_match, avg_todf_compare_mismatch,
                                                           wo_todf_compare_match, wo_todf_compare_mismatch,
                                                           wo_todf_expanding, avg_todf_expanding, hard_mismatches)
                # print "we are in proposal:", key
                data = cp.comments_dict(directory + '/' + file_dict[key].keys()[0])
                pdata = cp.get_dictionary_v2(data)
                for subKey in file_dict[key].keys()[1:]:
                    data = cp.comments_dict(directory + '/' + subKey)
                    pdata = cp.get_dictionary_v2(data, p_data=pdata)
                G, omitted, a, d, un, calc = cp.get_graph(pdata)
                if calc:
                    profile, all_titles = cp.get_profile(pdata)
                    collective_labelling = compute_collective_labelling(G, profile, CF)
                    decision = compute_collective_decition(collective_labelling, 0)
                    profile.append(collective_labelling)
                    all_titles.append('Collective decision')
                    pos = nx.spring_layout(G)
                    # drawProfile(G, profile, 0, all_titles, pos)
                    print >> f, cp.write_output(key, a, d, un, cp.results, collective_labelling[0])
                else:
                    print >> f, cp.write_output(key, a, d, un, cp.results)
                # try:
                #     profile, all_titles = get_profile(pdata)
                #     collective_labelling = compute_collective_labelling(G, profile, CF)
                #     decision = compute_collective_decition(collective_labelling, 0)
                #     profile.append(collective_labelling)
                #     all_titles.append('Collective decision')
                #     pos = nx.spring_layout(G)
                #     # drawProfile(G, profile, 0, all_titles, pos)
                #     print >> f, write_output(key, a, d, un, results, collective_labelling[0])
                # except KeyError:
                #     print >> f, write_output(key, a, d, un, results)
                avg_nan_count = cp.avg_nan_count
                avg_todf_compare_match = cp.avg_todf_compare_match
                avg_todf_compare_mismatch = cp.avg_todf_compare_mismatch
                wo_todf_compare_match = cp.wo_todf_compare_match
                wo_todf_compare_mismatch = cp.wo_todf_compare_mismatch
                wo_todf_expanding = cp.wo_todf_expanding
                avg_todf_expanding = cp.avg_todf_expanding
                hard_mismatches = cp.hard_mismatches

        cpa = it - cp.avg_nan_count

        print >> f, "Computed proposals:", it
        print >> f, "Average result NaN proposals:", cp.avg_nan_count, "(" + str(float(cp.avg_nan_count) * 100 / it), "%)"
        print >> f, "Computable proposals:", cpa, "(" + str(cpa * 100 / it), "%)"
        print >> f, "The following percents are computed over the amount of computable proposals:"
        print >> f, "WO and TODF:"
        print >> f, "\t- Matches:", cp.wo_todf_compare_match, "(" + str(float(cp.wo_todf_compare_match * 100 / cpa)), "%)"
        print >> f, "\t- Matches expanding:", cp.wo_todf_expanding, "(" + str(float(cp.wo_todf_expanding * 100 / cpa)), "%)"
        print >> f, "\t- Combined matches:", cp.wo_todf_expanding + cp.wo_todf_compare_match, "(" + str(
            float((cp.wo_todf_expanding + cp.wo_todf_compare_match) * 100 / cpa)), "%)"
        print >> f, "\t- Mismatches:", cp.wo_todf_compare_mismatch, "(" + str(
            float(cp.wo_todf_compare_mismatch * 100 / cpa)), "%)"
        print >> f, "AVG and TODF:"
        print >> f, "\t- Matches:", cp.avg_todf_compare_match, "(" + str(float(cp.avg_todf_compare_match * 100 / cpa)), "%)"
        print >> f, "\t- Matches expanding:", cp.avg_todf_expanding, "(" + str(float(cp.avg_todf_expanding * 100 / cpa)), "%)"
        print >> f, "\t- Combined matches:", cp.avg_todf_expanding + cp.avg_todf_compare_match, "(" + str(
            float((cp.avg_todf_expanding + cp.avg_todf_compare_match) * 100 / cpa)), "%)"
        print >> f, "\t- Mismatches:", cp.avg_todf_compare_mismatch, "(" + str(
            float(cp.avg_todf_compare_mismatch * 100 / cpa)), "%)"

        for prop in cp.hard_mismatches.keys():
            print >> f_mismatches, cp.hard_mismatches[prop]
