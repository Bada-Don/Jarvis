"""
scripts/office/unpack.py
Unpack a .docx (or any Office Open XML file) into a readable directory.

Usage:
    python scripts/office/unpack.py document.docx unpacked/
    python scripts/office/unpack.py document.docx unpacked/ --merge-runs false

What it does:
  1. Extracts the ZIP archive
  2. Pretty-prints every XML file (indent=2)
  3. Merges adjacent runs in document.xml that share identical <w:rPr> (optional, on by default)
  4. Converts smart-quote Unicode chars to XML entities so they survive round-trips
"""

import argparse
import copy
import os
import shutil
import zipfile
from lxml import etree

# ── Namespaces ────────────────────────────────────────────────────────────────
W  = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}

# Characters that must survive as XML entities (smart quotes etc.)
ENTITY_MAP = {
    "\u2018": "&#x2018;",  # '
    "\u2019": "&#x2019;",  # '
    "\u201C": "&#x201C;",  # "
    "\u201D": "&#x201D;",  # "
    "\u2013": "&#x2013;",  # –
    "\u2014": "&#x2014;",  # —
}


def _pretty(tree: etree._ElementTree) -> bytes:
    """Serialize an ElementTree with 2-space indentation."""
    etree.indent(tree, space="  ")
    return etree.tostring(
        tree.getroot(),
        xml_declaration=True,
        encoding="UTF-8",
        standalone=True,
    )


def _escape_smart_quotes(xml_bytes: bytes) -> bytes:
    """Replace smart-quote chars with XML entities in the raw byte stream."""
    text = xml_bytes.decode("utf-8")
    for char, entity in ENTITY_MAP.items():
        text = text.replace(char, entity)
    return text.encode("utf-8")


def _runs_mergeable(r1: etree._Element, r2: etree._Element) -> bool:
    """Return True if two <w:r> elements have identical <w:rPr> (or both lack one)."""
    rpr1 = r1.find(f"{{{W}}}rPr")
    rpr2 = r2.find(f"{{{W}}}rPr")
    if rpr1 is None and rpr2 is None:
        return True
    if rpr1 is None or rpr2 is None:
        return False
    return etree.tostring(rpr1) == etree.tostring(rpr2)


def _merge_adjacent_runs(root: etree._Element) -> None:
    """In-place merge of adjacent <w:r> siblings that share the same <w:rPr>."""
    for para in root.iter(f"{{{W}}}p"):
        children = list(para)
        i = 0
        while i < len(children) - 1:
            cur = children[i]
            nxt = children[i + 1]
            if (
                cur.tag == f"{{{W}}}r"
                and nxt.tag == f"{{{W}}}r"
                and _runs_mergeable(cur, nxt)
            ):
                # Append text nodes from nxt into cur
                cur_t  = cur.find(f"{{{W}}}t")
                nxt_t  = nxt.find(f"{{{W}}}t")
                if cur_t is not None and nxt_t is not None:
                    combined = (cur_t.text or "") + (nxt_t.text or "")
                    cur_t.text = combined
                    if combined != combined.strip():
                        cur_t.set(
                            "{http://www.w3.org/XML/1998/namespace}space", "preserve"
                        )
                    para.remove(nxt)
                    children.pop(i + 1)
                    continue  # re-check same index
            i += 1


def unpack(src: str, dst: str, merge_runs: bool = True) -> None:
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)

    with zipfile.ZipFile(src, "r") as z:
        z.extractall(dst)

    # Pretty-print and optionally merge runs for every XML file
    for dirpath, _, filenames in os.walk(dst):
        for fname in filenames:
            if not fname.endswith(".xml") and not fname.endswith(".rels"):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                tree = etree.parse(fpath)
            except etree.XMLSyntaxError:
                print(f"  [WARN] Could not parse {fpath} — skipping")
                continue

            if merge_runs and fname == "document.xml":
                _merge_adjacent_runs(tree.getroot())

            raw = _pretty(tree)
            raw = _escape_smart_quotes(raw)
            with open(fpath, "wb") as f:
                f.write(raw)

    print(f"✅ Unpacked '{src}' → '{dst}' ({merge_runs=})")


def main():
    parser = argparse.ArgumentParser(description="Unpack a .docx to editable XML")
    parser.add_argument("src", help="Path to .docx file")
    parser.add_argument("dst", help="Output directory")
    parser.add_argument(
        "--merge-runs",
        default="true",
        choices=["true", "false"],
        help="Merge adjacent runs with identical formatting (default: true)",
    )
    args = parser.parse_args()
    unpack(args.src, args.dst, merge_runs=(args.merge_runs == "true"))


if __name__ == "__main__":
    main()
