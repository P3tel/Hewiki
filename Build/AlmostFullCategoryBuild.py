#!/usr/bin/env python3
"""
Hewiki XML → Graph + Categories (fast, offline category extraction)

This version avoids any HTTP requests and instead extracts categories directly
from the Wikipedia XML dump text (parsing [[קטגוריה:...]] / [[Category:...]]
links). This is orders of magnitude faster and fully accurate for the dump's
state (no dependency on network or live site).

Features:
- Single-run: reads the .bz2 dump, builds directed graph from wikilinks
  (namespace 0 articles only, skips redirects)
- Extracts categories from page text using fast regex, attaches to nodes
- Reports progress every minute (thread-safe)
- Saves GraphML and prints node/edge counts and category-count histogram

Dependencies:
  pip install networkx lxml

Run:
  python hewiki_fast_build.py

Notes:
- This is much faster than doing online category fetches (no HTTP).
- If you want additional speedups, consider multiprocessing to parallelize
  parsing and graph edge emission, or using a more compact graph writer.
"""

import bz2  
import re
import time
import json
import threading
from typing import List
import numpy as np

# ---- NumPy 2.0 compatibility patch for NetworkX 2.8.x ----
if not hasattr(np, "float_"):
    np.float_ = np.float64
if not hasattr(np, "int_"):
    np.int_ = np.int64
if not hasattr(np, "bool_"):
    np.bool_ = np.bool_
# ---------------------------------------------------------

import networkx as nx
from lxml import etree

# ================= CONFIG =================
DUMP_PATH = r"hewiki-latest-pages-articles.xml.bz2"
OUTPUT_GRAPH = "Hewiki_CategoryGraph.graphml"
OUTPUT_PICKLE = "Hewiki_CategoryGraph.gpickle"
OUTPUT_EDGELIST = "Hewiki_CategoryGraph.edgelist"
STATUS_PATH = "crawler_status.json"

REPORT_INTERVAL = 60  # seconds
SLEEP_BETWEEN_PAGES = 0.001  # small pause if you want to throttle IO
WIKI_LINK_RE = re.compile(r"\[\[([^|\]#]+)")
CAT_RE = re.compile(r"\[\[(?:קטגוריה:|Category:)([^|\]#]+)", re.IGNORECASE)
# =========================================


def is_namespace0(title: str) -> bool:
    return ":" not in title


def iter_pages(bz2_path):
    """Stream pages (title, text, is_redirect) from a bz2 XML dump."""
    with bz2.open(bz2_path, mode="rb") as f:
        context = etree.iterparse(f, events=("end",), tag="{*}page")
        for _, elem in context:
            title_el = elem.find('.//{*}title')
            text_el = elem.find('.//{*}text')
            redirect_el = elem.find('.//{*}redirect')

            if title_el is not None and text_el is not None:
                title = (title_el.text or "").strip()
                text = text_el.text or ""
                is_redirect = redirect_el is not None
                yield title, text, is_redirect

            # free memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]


def extract_links(text: str) -> List[str]:
    return [m.group(1).strip() for m in WIKI_LINK_RE.finditer(text)]


def extract_categories_from_text(text: str) -> List[str]:
    # find all category links, preserve order and dedupe
    out = []
    seen = set()
    for m in CAT_RE.finditer(text):
        c = m.group(1).strip()
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def sanitize_attr_name(s: str) -> str:
    s2 = s.strip().replace(" ", "_")
    s2 = re.sub(r"[^0-9A-Za-z_\-\u0590-\u05FF]", "_", s2)
    s2 = re.sub(r"_+", "_", s2).strip("_")
    if not s2:
        s2 = "unnamed"
    return f"cat_{s2}"


def reporter(counter, G, done, lock):
    while not done.is_set():
        time.sleep(REPORT_INTERVAL)
        with lock:
            pages = counter.get("pages", 0)
            nodes = G.number_of_nodes()
            edges = G.number_of_edges()
        print(f"Processed pages: {pages:,} | Nodes: {nodes:,} | Edges: {edges:,}")
        try:
            with open(STATUS_PATH, "w", encoding="utf-8") as f:
                json.dump({
                    "pages_processed": pages,
                    "nodes": nodes,
                    "edges": edges,
                    "timestamp": time.time()
                }, f)
        except Exception:
            pass


# ================= MAIN =================

print("Pass 1 – collecting article titles (namespace 0, skipping redirects)")
existing_titles = set()
redirects = 0
pages_seen = 0

for title, text, is_redirect in iter_pages(DUMP_PATH):
    if not is_namespace0(title):
        continue
    if is_redirect:
        redirects += 1
        continue
    existing_titles.add(title)
    pages_seen += 1

print(f"Articles kept: {len(existing_titles):,}")
print(f"Redirects skipped: {redirects:,}")

print("Pass 2 – building graph and extracting categories from dump")

G = nx.DiGraph(name="Hewiki_Graph_With_Categories")
title_to_id = {}
next_id = 0

counter = {"pages": 0}
lock = threading.Lock()
done = threading.Event()
threading.Thread(target=reporter, args=(counter, G, done, lock), daemon=True).start()

for title, text, is_redirect in iter_pages(DUMP_PATH):
    if not is_namespace0(title) or is_redirect:
        continue
    if title not in existing_titles:
        continue

    # ensure node exists (under lock)
    with lock:
        if title not in title_to_id:
            title_to_id[title] = next_id
            G.add_node(next_id, title=title)
            node_id = next_id
            next_id += 1
        else:
            node_id = title_to_id[title]

    # extract categories directly from the page text (fast, offline)
    if "categories" not in G.nodes[node_id]:
        cats = extract_categories_from_text(text)
        if cats:
            with lock:
                G.nodes[node_id]["categories"] = "||".join(cats)
                for c in cats:
                    G.nodes[node_id][sanitize_attr_name(c)] = "1"
        else:
            with lock:
                G.nodes[node_id]["categories"] = ""

    # outgoing links -> edges
    for tgt in extract_links(text):
        if not is_namespace0(tgt) or tgt not in existing_titles:
            continue
        with lock:
            if tgt not in title_to_id:
                title_to_id[tgt] = next_id
                G.add_node(next_id, title=tgt)
                tgt_id = next_id
                next_id += 1
            else:
                tgt_id = title_to_id[tgt]
            G.add_edge(node_id, tgt_id)

    with lock:
        counter["pages"] += 1

    if SLEEP_BETWEEN_PAGES:
        time.sleep(SLEEP_BETWEEN_PAGES)

# finish

done.set()

print("Saving GraphML (slow, archival)…")
nx.write_graphml(G, OUTPUT_GRAPH)

print("Saving pickle (FAST reload)…")
nx.write_gpickle(G, OUTPUT_PICKLE)

print("Saving edgelist (structure only)…")
nx.write_edgelist(G, OUTPUT_EDGELIST, data=False)

# compute category histogram
cat_hist = {}
for _, data in G.nodes(data=True):
    cats = data.get("categories", "")
    k = 0 if not cats else cats.count("||") + 1
    cat_hist[k] = cat_hist.get(k, 0) + 1

print("Done.")
print(f"Final node count: {G.number_of_nodes():,}")
print(f"Final edge count: {G.number_of_edges():,}")
print("Category count distribution:")
for k in sorted(cat_hist):
    print(f"  {k}: {cat_hist[k]:,}")
