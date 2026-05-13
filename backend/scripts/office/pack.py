"""
scripts/office/pack.py
Repack an unpacked DOCX directory back into a valid .docx file.

Usage:
    python scripts/office/pack.py unpacked/ output.docx
    python scripts/office/pack.py unpacked/ output.docx --original document.docx
    python scripts/office/pack.py unpacked/ output.docx --validate false

What it does:
  1. Validates each XML file for well-formedness
  2. Auto-repairs known issues (durableId overflow, missing xml:space)
  3. Condenses XML (removes pretty-print whitespace between tags)
  4. Zips everything back into a valid .docx
"""

import argparse
import os
import re
import random
import zipfile
from lxml import etree

W   = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML = "http://www.w3.org/XML/1998/namespace"


# ── Auto-repair rules ────────────────────────────────────────────────────────

def _repair_durable_id(root: etree._Element) -> int:
    """Replace durableId values >= 0x7FFFFFFF with a valid random ID."""
    fixed = 0
    MAX_VALID = 0x7FFFFFFE
    for elem in root.iter():
        for attr in list(elem.attrib.keys()):
            if "durableId" in attr:
                try:
                    val = int(elem.get(attr))
                    if val >= 0x7FFFFFFF:
                        elem.set(attr, str(random.randint(1, MAX_VALID)))
                        fixed += 1
                except (ValueError, TypeError):
                    pass
    return fixed


def _repair_xml_space(root: etree._Element) -> int:
    """Add xml:space='preserve' to <w:t> elements that have leading/trailing spaces."""
    fixed = 0
    space_attr = f"{{{XML}}}space"
    for t in root.iter(f"{{{W}}}t"):
        text = t.text or ""
        if text != text.strip() and t.get(space_attr) != "preserve":
            t.set(space_attr, "preserve")
            fixed += 1
    return fixed


def _condense(tree: etree._ElementTree) -> bytes:
    """Serialize without pretty-print indentation (compact XML)."""
    return etree.tostring(
        tree.getroot(),
        xml_declaration=True,
        encoding="UTF-8",
        standalone=True,
    )


# ── Validation ───────────────────────────────────────────────────────────────

def _validate_xml(fpath: str) -> list[str]:
    """Return a list of error strings, empty if valid."""
    errors = []
    try:
        etree.parse(fpath)
    except etree.XMLSyntaxError as e:
        errors.append(str(e))
    return errors


# ── Core pack logic ──────────────────────────────────────────────────────────

def pack(src_dir: str, out_path: str, validate: bool = True) -> None:
    all_errors: dict[str, list[str]] = {}
    xml_files = []

    for dirpath, _, filenames in os.walk(src_dir):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            rel   = os.path.relpath(fpath, src_dir).replace("\\", "/")

            if fname.endswith(".xml") or fname.endswith(".rels"):
                # Parse → auto-repair → condense
                try:
                    tree = etree.parse(fpath)
                except etree.XMLSyntaxError as e:
                    if validate:
                        all_errors[rel] = [str(e)]
                    continue

                root = tree.getroot()
                n_id    = _repair_durable_id(root)
                n_space = _repair_xml_space(root)
                if n_id or n_space:
                    print(f"  [repair] {rel}: durableId={n_id}, xml:space={n_space}")

                condensed = _condense(tree)
                # Write condensed version back so zipfile reads the clean bytes
                with open(fpath, "wb") as f:
                    f.write(condensed)

                if validate:
                    errs = _validate_xml(fpath)
                    if errs:
                        all_errors[rel] = errs

            xml_files.append((fpath, rel))

    if all_errors and validate:
        print("\n❌ Validation errors found:")
        for path, errs in all_errors.items():
            for e in errs:
                print(f"  {path}: {e}")
        print("Run with --validate false to pack anyway.\n")
        raise SystemExit(1)

    # Zip everything
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for fpath, rel in xml_files:
            z.write(fpath, rel)
        # Also include non-XML files (images, fonts, etc.)
        for dirpath, _, filenames in os.walk(src_dir):
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                rel   = os.path.relpath(fpath, src_dir).replace("\\", "/")
                if not (fname.endswith(".xml") or fname.endswith(".rels")):
                    z.write(fpath, rel)

    print(f"✅ Packed '{src_dir}' → '{out_path}'")


def main():
    parser = argparse.ArgumentParser(description="Repack an unpacked DOCX directory")
    parser.add_argument("src",  help="Unpacked directory (output of unpack.py)")
    parser.add_argument("out",  help="Output .docx file path")
    parser.add_argument(
        "--original",
        default=None,
        help="Path to original .docx (unused currently, reserved for future diff)",
    )
    parser.add_argument(
        "--validate",
        default="true",
        choices=["true", "false"],
        help="Validate XML before packing (default: true)",
    )
    args = parser.parse_args()
    pack(args.src, args.out, validate=(args.validate == "true"))


if __name__ == "__main__":
    main()
