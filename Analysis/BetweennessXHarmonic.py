import networkx as nx
import time
import heapq
from collections import defaultdict
from networkx.algorithms.centrality.betweenness import _single_source_shortest_path_basic

GRAPH_PATH = "hewiki_basegraph.gpickle"
TIME_LIMIT = 60 * 60      # שעה
REPORT_EVERY = 5 * 60
TOP_K = 50

print("Loading graph...")
G = nx.read_gpickle(GRAPH_PATH)
nodes = list(G.nodes())
N = len(nodes)

bet = defaultdict(float)

start = time.time()
last_report = start
done = 0

print("\n=== Starting exact time-bounded betweenness ===")

for s in nodes:
    S, P, sigma, _ = _single_source_shortest_path_basic(G, s)
    delta = dict.fromkeys(S, 0.0)

    while S:
        w = S.pop()
        for v in P[w]:
            delta_v = (sigma[v] / sigma[w]) * (1 + delta[w])
            delta[v] += delta_v
        if w != s:
            bet[w] += delta[w]

    done += 1
    now = time.time()

    if now - last_report >= REPORT_EVERY:
        pct = 100 * (now - start) / TIME_LIMIT
        print(f"[Betweenness] ~{pct:.1f}% time used | sources: {done}")
        last_report = now

    if now - start >= TIME_LIMIT:
        break

# Top 50
top = heapq.nlargest(TOP_K, bet.items(), key=lambda x: x[1])

print("\nTop 50 Betweenness:\n")
for i, (v, score) in enumerate(top, 1):
    title = G.nodes[v].get("title", str(v))
    print(f"{i}. {title} — {score}")

print("\nSources processed:", done)






import networkx as nx
import time
import heapq
from collections import defaultdict

GRAPH_PATH = "hewiki_basegraph.gpickle"
TIME_LIMIT = 60 * 60      # שעה
REPORT_EVERY = 5 * 60
TOP_K = 50

print("Loading graph...")
G = nx.read_gpickle(GRAPH_PATH)
nodes = list(G.nodes())
N = len(nodes)

harmonic = defaultdict(float)

start = time.time()
last_report = start
done = 0

print("\n=== Starting exact time-bounded harmonic closeness ===")

for s in nodes:
    # exact shortest paths from s
    lengths = nx.single_source_shortest_path_length(G, s)

    for t, d in lengths.items():
        if d > 0:
            harmonic[s] += 1.0 / d

    done += 1
    now = time.time()

    if now - last_report >= REPORT_EVERY:
        pct = 100 * (now - start) / TIME_LIMIT
        print(f"[Harmonic] ~{pct:.1f}% time used | sources: {done}")
        last_report = now

    if now - start >= TIME_LIMIT:
        break

# Top 50
top = heapq.nlargest(TOP_K, harmonic.items(), key=lambda x: x[1])

print("\nTop 50 Harmonic Closeness:\n")
for i, (v, score) in enumerate(top, 1):
    title = G.nodes[v].get("title", str(v))
    print(f"{i}. {title} — {score}")

print("\nSources processed:", done)
