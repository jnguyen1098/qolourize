# Code adapted from https://github.com/dwave-examples/graph-coloring

import networkx as nx
from dimod import DiscreteQuadraticModel
from dwave.system import LeapHybridDQMSampler

import pygraphviz
import pydot
import sys
import csv

# Command line args
if len(sys.argv) != 3:
    print('Usage: program input_graph output_name')
    exit()

output_name = sys.argv[2]

nodes = []
edges = []

print("Reading in edges")
with open(sys.argv[1], "r") as input_file:
    reader = csv.reader(input_file)
    for row in reader:
        edges.append((int(row[0]), int(row[1])))

print("Reading in nodes")
for edge in edges:
    if edge[0] not in nodes:
        nodes.append(edge[0])
    if edge[1] not in nodes:
        nodes.append(edge[1])

print()
print(f"Nodes: {nodes}")
print(f"Edges: {edges}")
print()

# The four-colour theorem states that we only need 4 colours
num_colors = 4
colors = range(num_colors)
colours = {0: 'green', 1: 'red', 2: 'blue', 3: 'yellow'}

print("Initializing discrete quadratic model")
dqm = DiscreteQuadraticModel()

print("Creating graph model")
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
print("Loading DQM, defining variables, and setting biases/weights")
for p in G.nodes:
    dqm.add_variable(num_colors, label=p)
for p in G.nodes:
    dqm.set_linear(p, colors)
for p0, p1 in G.edges:
    dqm.set_quadratic(p0, p1, {(c, c): lagrange for c in colors})

print("Initializing DQM solver")
sampler = LeapHybridDQMSampler()

print("Solving graph colouring")
sampleset = sampler.sample_dqm(dqm)

print("Extracting solution")
sample = sampleset.first.sample
energy = sampleset.first.energy

print("Verifying correctness of solution")
valid = True
for edge in G.edges:
    i, j = edge
    if sample[i] == sample[j]:
        valid = False
        break

print()
print("Solution:", sample)
print("Solution energy:", energy)
print("Solution validity:", valid)
print()

print("Creating Graphviz model")
G = pygraphviz.AGraph(directed=False)
G.layout(prog='dot')

print("Appending nodes")
for node in nodes:
    G.add_node(node, shape="circle", style="filled", color=colours[sample[node]])

print("Appending edges")
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

