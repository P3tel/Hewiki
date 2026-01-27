from igraph import Graph

# load graphml
g = Graph.Read_GraphML("hewiki_BaseGraph.graphml")

# degrees
in_deg  = g.indegree()
out_deg = g.outdegree()

# counts with degree = 1
num_in1 = sum(1 for d in in_deg if d == 1)
num_out1 = sum(1 for d in out_deg if d == 1)

print("Nodes with in-degree = 1:", num_in1)
print("Nodes with out-degree = 1:", num_out1)

# counts with degree = 0
num_in0 = sum(1 for d in in_deg if d == 0)
num_out0 = sum(1 for d in out_deg if d == 0)

print("Nodes with in-degree = 0:", num_in0)
print("Nodes with out-degree = 0:", num_out0)

# get names
names = g.vs["title"]

# top 10 in-degree nodes
top_in_idx = sorted(range(len(in_deg)), key=lambda i: in_deg[i], reverse=True)[:50]
print("\nTop 50 highest in-degree:")
for i in top_in_idx:
    print(names[i], in_deg[i])

# top 10 out-degree nodes
top_out_idx = sorted(range(len(out_deg)), key=lambda i: out_deg[i], reverse=True)[:50]
print("\nTop 50 highest out-degree:")
for i in top_out_idx:
    print(names[i], out_deg[i])
