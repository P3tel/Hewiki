from igraph import Graph
import numpy as np

g = Graph.Read_GraphML("hewiki_BaseGraph.graphml")
g.to_directed()

n = g.vcount()
local_C = np.zeros(n, dtype=float)

sum_num = 0   # sum of numerators (closed ordered pairs over all nodes)
sum_den = 0   # sum of denominators (k*(k-1) over all nodes)

for v in range(n):
    # neighbors in/out (as python sets for fast intersection)
    nin = set(g.neighbors(v, mode="IN"))
    nout = set(g.neighbors(v, mode="OUT"))
    neigh = nin.union(nout)
    k = len(neigh)
    if k < 2:
        local_C[v] = 0.0
        continue

    # numerator: count ordered neighbor pairs (u->w) where both u and w are neighbors of v
    triangles = 0
    for u in neigh:
        # outgoing neighbors of u that are among v's neighbors
        out_u = set(g.neighbors(u, mode="OUT"))
        triangles += len(neigh.intersection(out_u))

    denom = k * (k - 1)   # ordered pairs among neighbors
    local = triangles / denom if denom > 0 else 0.0
    local_C[v] = local

    sum_num += triangles
    sum_den += denom

# results
avg_local = float(np.mean(local_C))
global_transitivity = (sum_num / sum_den) if sum_den > 0 else 0.0

print("Global (directed) transitivity (ratio of sums):", global_transitivity)
print("Average local directed clustering (mean of C_i):", avg_local)
