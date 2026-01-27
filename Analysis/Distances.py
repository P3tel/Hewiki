#!/usr/bin/env python3
import igraph as ig
import random
import math
import statistics

GRAPH_FILE = "Hewiki_BaseGraph.graphml"

INITIAL_SAMPLES = 2000
MAX_SAMPLES = 25000
TARGET_REL_ERROR = 0.00001
BATCH_SIZE = 250

print("Loading graph...")
g = ig.Graph.Read_GraphML(GRAPH_FILE)
g.to_directed()

print(f"Nodes: {g.vcount()}, Edges: {g.ecount()}")

# -------- TRY STRONG FIRST --------
print("Extracting largest SCC...")
sccs = g.connected_components(mode="STRONG")
largest_scc = sccs[0]
print(f"Largest SCC size: {len(largest_scc)}")

# -------- IF SCC TOO SMALL → USE WCC --------
if len(largest_scc) <= 10:
    print("SCC is trivial; switching to largest WCC (directed distances within it).")
    wccs = g.connected_components(mode="WEAK")
    largest_wcc = wccs[0]
    g = g.subgraph(largest_wcc)
else:
    g = g.subgraph(largest_scc)

n = g.vcount()
print(f"Working component size: {n}")

# -------- SAMPLING --------
def sample_sources(k):
    k = min(k, n)   # avoid oversampling
    vertices = random.sample(range(n), k)
    all_d = []
    longest = 0

    for v in vertices:
        drow = g.distances(v)[0]
        for d in drow:
            if d != math.inf and d != 0:
                all_d.append(d)
                if d > longest:
                    longest = d
    return all_d, longest

print("Sampling distances...")

samples = []
best_longest = 0

# initial batch
d, L = sample_sources(INITIAL_SAMPLES)
samples.extend(d)
best_longest = max(best_longest, L)

while True:
    mean_est = statistics.mean(samples)
    sd_est = statistics.pstdev(samples)
    rse = sd_est / math.sqrt(len(samples)) / mean_est

    print(f"Samples={len(samples)}  mean≈{mean_est:.4f}  RSE≈{rse:.3%}  longest={best_longest}")

    if rse < TARGET_REL_ERROR or len(samples) >= MAX_SAMPLES:
        break

    d, L = sample_sources(BATCH_SIZE)
    samples.extend(d)
    best_longest = max(best_longest, L)

avg_path_len = statistics.mean(samples)

print("\n===== FINAL RESULTS (DIRECTED) =====")
print(f"Average directed shortest-path length (reachable pairs): {avg_path_len}")
print(f"Estimated directed diameter (longest shortest path found): {best_longest}")
print(f"Samples used: {len(samples)}")
