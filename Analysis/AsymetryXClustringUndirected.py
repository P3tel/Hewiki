from igraph import Graph

#load graph
g = Graph.Read_GraphML("Hewiki_BaseGraph.graphml")

# Ensure directed & unweighted
g.to_directed()
g.es["weight"] = [1] * g.ecount()

# reciprocity = fraction of mutual edges
reciprocity = g.reciprocity() 
asymmetry = 1.0 - reciprocity

print("Reciprocity:", reciprocity)
print("Asymmetry:", asymmetry)

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
print("Local clustering – mean:", sum(local_clustering)/len(local_clustering))

