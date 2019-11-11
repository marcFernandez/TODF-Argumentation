import comments_processing
from collective_function import *
import sys
import os
from networkx.drawing.nx_agraph import write_dot, graphviz_layout

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
    with open("PAM_output.txt") as sout:
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

        calc = cp.get_graph()

        cp.show_stats()

        cp.get_profile()

        for prop in cp.processed_data:
            if cp.processed_data[prop]['ancestry'] is not None:
                cp.processed_data[cp.processed_data[prop]['ancestry']]['successor'].append(prop)

        collective_labelling = compute_collective_labelling(cp.G, cp.profile, CF)

        if collective_labelling == {}:
            print "There are no comments, exiting."
            exit(0)

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

        ##############################################

        # for node in cp.G.nodes():
        # 	if cp.processed_data[node]['ancestry'] is None and node != 0:
        # 		positions[1][node] = (px-1, 0.5)
        # 		pos_fixed[1].append(node)
        # 		px += 0.5
        #
        # positions[1][0] = (-1+(px-0.5)/2, 1)
        #
        # def rec_pos(nod, lvl, i):
        # 	try:
        # 		pos_fixed[lvl].append(nod)
        # 		positions[lvl][nod] = (positions[lvl-1][cp.processed_data[nod]['ancestry']][0] + i/1.75,
        # 							   positions[lvl-1][cp.processed_data[nod]['ancestry']][1] - 0.5)
        # 	except KeyError:
        # 		pos_fixed[lvl] = [nod]
        # 		positions[lvl] = {nod: (positions[lvl-1][cp.processed_data[nod]['ancestry']][0] + i/1.75,
        # 								positions[lvl-1][cp.processed_data[nod]['ancestry']][1] - 0.5)}
        # 	ct = 0
        # 	for succ in cp.processed_data[nod]['successor']:
        # 		rec_pos(succ, lvl + 1, ct)
        # 		ct += 1
        #
        # for node in pos_fixed[1]:
        # 	cct = 0
        # 	for succ in cp.processed_data[node]['successor']:
        # 		rec_pos(succ, 2, cct)
        # 		cct += 1

        ###############################################
        final_pos = {}
        for pos_dict in positions.values():
            final_pos.update(pos_dict)
        final_fixed = []
        for _list in pos_fixed.values():
            final_fixed += _list

        pos = nx.spring_layout(cp.G, pos=final_pos, fixed=final_fixed)

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
        print >> f, "Average result NaN proposals:", cp.avg_nan_count, "(" + str(
            float(cp.avg_nan_count) * 100 / it), "%)"
        print >> f, "Computable proposals:", cpa, "(" + str(cpa * 100 / it), "%)"
        print >> f, "The following percents are computed over the amount of computable proposals:"
        print >> f, "PAM and TODF:"
        print >> f, "\t- Matches:", cp.wo_todf_compare_match, "(" + str(
            float(cp.wo_todf_compare_match * 100 / cpa)), "%)"
        print >> f, "\t- Matches expanding:", cp.wo_todf_expanding, "(" + str(
            float(cp.wo_todf_expanding * 100 / cpa)), "%)"
        print >> f, "\t- Combined matches:", cp.wo_todf_expanding + cp.wo_todf_compare_match, "(" + str(
            float((cp.wo_todf_expanding + cp.wo_todf_compare_match) * 100 / cpa)), "%)"
        print >> f, "\t- Mismatches:", cp.wo_todf_compare_mismatch, "(" + str(
            float(cp.wo_todf_compare_mismatch * 100 / cpa)), "%)"
        print >> f, "AVG and TODF:"
        print >> f, "\t- Matches:", cp.avg_todf_compare_match, "(" + str(
            float(cp.avg_todf_compare_match * 100 / cpa)), "%)"
        print >> f, "\t- Matches expanding:", cp.avg_todf_expanding, "(" + str(
            float(cp.avg_todf_expanding * 100 / cpa)), "%)"
        print >> f, "\t- Combined matches:", cp.avg_todf_expanding + cp.avg_todf_compare_match, "(" + str(
            float((cp.avg_todf_expanding + cp.avg_todf_compare_match) * 100 / cpa)), "%)"
        print >> f, "\t- Mismatches:", cp.avg_todf_compare_mismatch, "(" + str(
            float(cp.avg_todf_compare_mismatch * 100 / cpa)), "%)"

        for prop in cp.hard_mismatches.keys():
            print >> f_mismatches, cp.hard_mismatches[prop]
