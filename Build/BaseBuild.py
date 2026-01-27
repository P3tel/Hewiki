import bz2
import re
import networkx as nx
from lxml import etree
import sys
import traceback

# -------- CONFIG --------
DUMP_PATH = r"hewiki-latest-pages-articles.xml.bz2"
GRAPH_NAME = "Hewiki_BaseGraph"
REPORT_EVERY = 1000
# ------------------------

WIKI_LINK_RE = re.compile(r"\[\[([^|\]#]+)")

def is_namespace0(title: str) -> bool:
    return ":" not in title

def iter_pages(bz2_path):
    with bz2.open(bz2_path, mode="rb") as f:
        context = etree.iterparse(f, events=('end',), tag='{*}page')
        for _, elem in context:
            title_el = elem.find('.//{*}title')
            text_el = elem.find('.//{*}text')
            redirect_el = elem.find('.//{*}redirect')

            if title_el is not None and text_el is not None:
                title = (title_el.text or "").strip()
                text = text_el.text or ""
                is_redirect = redirect_el is not None
                yield title, text, is_redirect

            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

def extract_links(text):
    return [m.group(1).strip() for m in WIKI_LINK_RE.finditer(text)]

# ---------- PASS 1 ----------
print("Pass 1 – collecting real article titles…")

existing_titles = set()
pages_processed = 0
redirects = 0

for title, text, is_redirect in iter_pages(DUMP_PATH):
    if not is_namespace0(title):
        continue
    if is_redirect:
        redirects += 1
        continue

    existing_titles.add(title)

    pages_processed += 1
    if pages_processed % REPORT_EVERY == 0:
        print(f"Collected {pages_processed:,} article titles")

print(f"Articles kept: {len(existing_titles):,}")
print(f"Redirects skipped: {redirects:,}")

# ---------- PASS 2 ----------
print("Pass 2 – building directed graph with names…")

G = nx.DiGraph(name=GRAPH_NAME)

title_to_id = {}
next_id = 0
pages_processed = 0

for title, text, is_redirect in iter_pages(DUMP_PATH):
    if not is_namespace0(title) or is_redirect:
        continue
    if title not in existing_titles:
        continue

    # ensure node exists
    if title not in title_to_id:
        title_to_id[title] = next_id
        G.add_node(next_id, title=title)
        next_id += 1

    src = title_to_id[title]

    # outgoing links
    for tgt in extract_links(text):
        if not is_namespace0(tgt):
            continue
        if tgt not in existing_titles:
            continue

        if tgt not in title_to_id:
            title_to_id[tgt] = next_id
            G.add_node(next_id, title=tgt)
            next_id += 1

        G.add_edge(src, title_to_id[tgt])

    pages_processed += 1
    if pages_processed % REPORT_EVERY == 0:
        print(
            f"Processed {pages_processed:,} | "
            f"Nodes: {G.number_of_nodes():,} | "
            f"Edges: {G.number_of_edges():,}"
        )

print("Graph finished. Saving…")

# ---------- SAVE ----------
nx.write_graphml(G, GRAPH_NAME + ".graphml")
nx.write_edgelist(G, GRAPH_NAME + ".edgelist", data=False)

print("Done.")
