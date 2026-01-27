import networkx as nx

# Load graph from gpickle
G = nx.read_gpickle("hewiki_basegraph.gpickle")

# Ensure directed
if not G.is_directed():
    G = G.to_directed()

def get_title(node):
    return G.nodes[node].get("title", str(node))

print("loaded")

# ------------------------
# PageRank
# ------------------------
pagerank = nx.pagerank(G, alpha=0.85, max_iter=1000, tol=1e-06)
avg_pr = sum(pagerank.values()) / len(pagerank)
top200_pr = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:200]

print("\n=== PageRank ===")
print("Average:", avg_pr)
print("\nTop 200 nodes:\n")
for i, (node, val) in enumerate(top200_pr, start=1):
    print(f"{i}. {get_title(node)} ({node}) — {val}")

# ------------------------
# Eigenvector Centrality
# ------------------------
eigen = nx.eigenvector_centrality(G, max_iter=1000, tol=1e-06)
avg_eigen = sum(eigen.values()) / len(eigen)
top200_eigen = sorted(eigen.items(), key=lambda x: x[1], reverse=True)[:200]

print("=== Eigenvector Centrality ===")
print("Average:", avg_eigen)
print("\nTop 200 nodes:\n")
for i, (node, val) in enumerate(top200_eigen, start=1):
    print(f"{i}. {get_title(node)} ({node}) — {val}")

# ------------------------
# Katz Centrality
# ------------------------
katz = nx.katz_centrality(G, alpha=0.1, beta=1.0, max_iter=1000, tol=1e-06)
avg_katz = sum(katz.values()) / len(katz)
top200_katz = sorted(katz.items(), key=lambda x: x[1], reverse=True)[:200]

print("\n=== Katz Centrality ===")
print("Average:", avg_katz)
print("\nTop 200 nodes:\n")
for i, (node, val) in enumerate(top200_katz, start=1):
    print(f"{i}. {get_title(node)} ({node}) — {val}")
    
