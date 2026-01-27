import networkx as nx
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt

# -------- parameters --------
GPICKLE_PATH = "hewiki_BaseGraph.gpickle"
BINS = 20
# ----------------------------

def log_binned_distribution_from_degrees(degrees, bins=20):
    degrees = np.array([d for d in degrees if d > 0])

    counts = Counter(degrees)
    k_vals = np.array(sorted(counts.keys()))
    n_vals = np.array([counts[k] for k in k_vals])

    log_bins = np.logspace(
        np.log10(k_vals.min()),
        np.log10(k_vals.max()),
        bins + 1
    )

    bin_idx = np.digitize(k_vals, log_bins)

    k_bin, p_bin = [], []
    N = degrees.size

    for i in range(1, len(log_bins)):
        mask = bin_idx == i
        if not np.any(mask):
            continue

        count = n_vals[mask].sum()
        width = log_bins[i] - log_bins[i - 1]
        k_center = np.sqrt(log_bins[i] * log_bins[i - 1])

        p_density = count / (N * width)

        k_bin.append(k_center)
        p_bin.append(p_density)

    return np.array(k_bin), np.array(p_bin)


def main():
    print("Loading graph...")
    G = nx.read_gpickle(GPICKLE_PATH)

    print("Computing in-degree distribution...")
    in_degrees = [d for _, d in G.in_degree()]
    k_in, p_in = log_binned_distribution_from_degrees(in_degrees, BINS)

    print("Computing out-degree distribution...")
    out_degrees = [d for _, d in G.out_degree()]
    k_out, p_out = log_binned_distribution_from_degrees(out_degrees, BINS)

    print("Plotting...")
    plt.figure()

    # line + points (same color)
    plt.loglog(k_in, p_in, '-o', linewidth=2, markersize=5,
               label="In-degree", color='tab:blue')

    plt.loglog(k_out, p_out, '-o', linewidth=2, markersize=5,
               label="Out-degree", color='tab:red')

    plt.xlabel("Degree k")
    plt.ylabel("P(k)")
    plt.title("Log-binned Degree Distributions")
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
