from igraph import Graph
import numpy as np
import matplotlib.pyplot as plt

def prepare_log_binned(degrees, bins_per_decade=18):
    deg = np.asarray(degrees, dtype=np.int64)
    degpos = deg[deg > 0]

    if degpos.size == 0:
        return np.array([]), np.array([]), np.array([]), 0

    log_min = np.log10(degpos.min())
    log_max = np.log10(degpos.max())

    n_bins = max(int(np.ceil((log_max - log_min) * bins_per_decade)), 6)
    edges = np.logspace(log_min, log_max, n_bins + 1)
    edges[-1] *= 1.000001  # include max degree

    counts, _ = np.histogram(degpos, bins=edges)
    centers = np.sqrt(edges[:-1] * edges[1:])
    widths = edges[1:] - edges[:-1]
    total_pos = counts.sum()
    pk = counts / (float(total_pos) * widths)

    mask = counts > 0
    return centers[mask], counts[mask], pk[mask], total_pos

def plot_two_series(x1, y1, x2, y2, xlabel, ylabel, title, labels=('A','B'), colors=('tab:blue','tab:orange')):
    plt.figure(figsize=(9,5))
    plt.loglog(x1, y1, linewidth=2, label=labels[0], color=colors[0])
    plt.loglog(x2, y2, linewidth=2, label=labels[1], color=colors[1])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    
    # cleaner grid: very light, thin lines (or remove entirely)
    plt.grid(False)  # completely remove grid
    plt.show()

def main(graph_path):
    G = Graph.Read_GraphML(graph_path)

    indeg = np.array(G.indegree(), dtype=np.int64)
    outdeg = np.array(G.outdegree(), dtype=np.int64)

    xi, ci, pki, _ = prepare_log_binned(indeg)
    xo, co, pko, _ = prepare_log_binned(outdeg)

    # 1) P(k) density
    if xi.size > 0 and xo.size > 0:
        plot_two_series(xi, pki, xo, pko,
                        xlabel="Degree k",
                        ylabel="P(k) (density)",
                        title="Log-binned degree probability density (in vs out)",
                        labels=("in", "out"))
    
    # 2) Counts
    if xi.size > 0 and xo.size > 0:
        plot_two_series(xi, ci, xo, co,
                        xlabel="Degree k",
                        ylabel="Number of nodes (counts)",
                        title="Log-binned degree counts (in vs out)",
                        labels=("in", "out"))

if __name__ == "__main__":
    graph_file = "Hewiki_BaseGraph.graphml"
    main(graph_file)
