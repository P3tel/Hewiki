from igraph import Graph

# ---------- LOAD YOUR GRAPH ----------
# Example if you have GraphML:
g = Graph.Read_GraphML("Hewiki_BaseGraph.graphml")

# Ensure directed & unweighted
g.to_directed()
g.es["weight"] = [1] * g.ecount()

# ---------- ASYMMETRY ----------
# reciprocity = fraction of mutual edges
reciprocity = g.reciprocity()  # igraph uses edge-based reciprocity
asymmetry = 1.0 - reciprocity

print("Reciprocity:", reciprocity)
print("Asymmetry:", asymmetry)

# ---------- CLUSTERING COEFFICIENTS ----------
# NOTE: clustering is traditionally defined for undirected graphs.
# Common practice: treat directed graph as undirected for clustering.

g_und = g.as_undirected()

# Global clustering / transitivity
global_clustering = g_und.transitivity_undirected()

# Average local clustering
avg_local_clustering = g_und.transitivity_avglocal_undirected()

# Local clustering list per node
local_clustering = g_und.transitivity_local_undirected(vertices=None, mode="zero")

print("Global clustering (transitivity):", global_clustering)
print("Average local clustering:", avg_local_clustering)
# local_clustering is a long list; print summary:
print("Local clustering – mean:", sum(local_clustering)/len(local_clustering))

# ---------- AVERAGE PATH LENGTH + LONGEST FINITE PATH ----------
#This doesnt currently work, needs checking tho

# Strongly connected components (new API)
components = g.connected_components(mode="STRONG")

# Largest SCC
largest_scc = components.giant()

# Average path length inside largest SCC
avg_path_len = largest_scc.average_path_length(directed=True)
print("Average path length on largest SCC:", avg_path_len)

# Longest finite shortest-path distance (diameter)
diameter = largest_scc.diameter(directed=True, unconn=False)
print("Longest finite shortest path (diameter of largest SCC):", diameter)

