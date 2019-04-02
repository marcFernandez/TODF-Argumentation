# TODF-Argumentation
Marc Fernández Font (markiff@gmail.com), in collaboration with [Maite López](http://www.maia.ub.es/~maite/) and Marc Serramià.
## Overview
This python based repository is an implementation of a family of aggregation functions that allow to make collective decisions in argumentation-based debates.

It implements the aggregation functions defined in the following paper:

**J. Ganzer-Ripoll, Natalia Criado, Maite López-Sánchez, Simon Parsons, Juan A. Rodríguez-Aguilar. COMBINING SOCIAL CHOICE THEORY AND ARGUMENTATION: ENABLING COLLECTIVE DECISION MAKING. Group Decision and Negotiation. Springer. 2018**
(https://link.springer.com/article/10.1007/s10726-018-9594-6)

And then compares its result with the one obtained with another aggregation functions defined in the following paper:

**Aggregation operators to compute norm support in virtual communities. Marc Serramia (University of Barcelona), Maite Lopez-Sánchez (University of Barcelona) and Juan A. Rodríguez-Aguilar (IIIA-CSIC)** 
(http://www.mpref-2016.preflib.org/wp-content/uploads/2016/06/paper-12.pdf)

It uses Decidim Barcelona comments as input data.

## Usage

There are two ways to run the main file:
1. If you want to compute just one proposal and see it's output graph run

* python example.py path proposal proposal_num_files
* e.g. 'python example.py ~/metadecidim-master/comments 00050 1'

![](example.PNG)

As you can see, there are different colours for nodes and edges. This correspond to the representation of the labels that both nodes and edges can have (as explained in the paper).

Nodes:
* Red -> OUT
* Green -> IN
* Yellow -> UNDEC

Edges:
* Red -> Attacking
* Green -> Defending

2. If you want to compute all the comment files from a directory and get the two output files with
 some information about all computed proposals and the greater mismatches run

* python example.py path
* e.g. 'python example.py ~/metadecidim-master/comments'

![](output_example.PNG)


## Requirements
Only python 2 is required

## Sources
Argumentation for Collective Decision Making library from Juan A. Rodriguez-Aguilar (jar@iiia.csic.es):

https://bitbucket.org/jariiia/argumentation-for-collective-decision-making

Decidim Barcelona comments data:

https://github.com/elaragon/metadecidim

NAM-output is the output.txt file from commentevaluator created by Marc Serramià Amorós:

https://bitbucket.org/msamsa/commentevaluator/src
