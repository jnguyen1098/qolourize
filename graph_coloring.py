# Code adapted from https://github.com/dwave-examples/graph-coloring

import networkx as nx
from dimod import DiscreteQuadraticModel
from dwave.system import LeapHybridDQMSampler

import pygraphviz
import pydot
import sys

# Command line args
if len(sys.argv) != 3:
    print('Usage: program input_graph output_name')
    exit()

output_name = sys.argv[1]

# Graph coloring with DQM solver

# The four-colour theorem states that we only need 4 colours
num_colors = 4
colors = range(num_colors)

# Initialize the DQM object
dqm = DiscreteQuadraticModel()

# Create our stuff
colours = {0: 'green', 1: 'red', 2: 'blue', 3: 'yellow'}
nodes = [0, 1, 2, 3, 4, 5, 6]
edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (0, 6)]

# nodes = [0, 1, 2, 3, 4, 5, 6, 7, 8]
# edges = [(0, 1), (0, 3), (1, 2), (1, 3), (1, 4), (1, 5), (2, 5), (3, 6), (4, 5), (4, 6), (4, 7), (4, 8), (5, 8), (7, 8)]

# Make Networkx graph of a hexagon
G = nx.Graph()
G.add_edges_from(edges)
n_edges = len(G.edges)

# initial value of Lagrange parameter
lagrange = max(colors)

# Load the DQM. Define the variables, and then set biases and weights.
# We set the linear biases to favor lower-numbered colors; this will
# have the effect of minimizing the number of colors used.
# We penalize edge connections by the Lagrange parameter, to encourage
# connected nodes to have different colors.
for p in G.nodes:
    dqm.add_variable(num_colors, label=p)
for p in G.nodes:
    dqm.set_linear(p, colors)
for p0, p1 in G.edges:
    dqm.set_quadratic(p0, p1, {(c, c): lagrange for c in colors})

# Initialize the DQM solver
sampler = LeapHybridDQMSampler()

# Solve the problem using the DQM solver
sampleset = sampler.sample_dqm(dqm)

# get the first solution, and print it
sample = sampleset.first.sample
energy = sampleset.first.energy

# check that colors are different
valid = True
for edge in G.edges:
    i, j = edge
    if sample[i] == sample[j]:
        valid = False
        break

print("Solution:", sample)
print("Solution energy:", energy)
print("Solution validity:", valid)
print()

G = pygraphviz.AGraph(directed=False)
G.layout(prog='dot')
for node in nodes:
    G.add_node(node, shape="circle", style="filled", color=colours[sample[node]])
for edge in edges:
    G.add_edge(edge[0], edge[1], dir="none")

print(f"Exporting {output_name}.gv")
G.write(f"{output_name}.gv")

graphs = pydot.graph_from_dot_file(f"{output_name}.gv")

print(f"Exporting {output_name}.svg")
graphs[0].write_svg(f"{output_name}.svg")

print(f"Exporting {output_name}.png")
graphs[0].write_png(f"{output_name}.png")
exit()

