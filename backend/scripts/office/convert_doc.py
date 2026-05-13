"""
scripts/office/convert_doc.py
Convert legacy .doc files to .docx using Microsoft Word COM Automation.

Usage:
    python scripts/office/convert_doc.py input.doc output.docx
"""

import argparse
import os
import sys

try:
    import win32com.client
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

def convert_doc_to_docx(src: str, dst: str):
    if not HAS_WIN32COM:
        print("❌ Error: pywin32 not installed.", file=sys.stderr)
        sys.exit(1)

    src_abs = os.path.abspath(src)
    dst_abs = os.path.abspath(dst)

    word = None
    doc = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False

        doc = word.Documents.Open(src_abs)
        
        # wdFormatXMLDocument = 16 (for .docx)
        doc.SaveAs2(dst_abs, FileFormat=16)
        doc.Close()
        print(f"✅ Successfully converted '{src}' to '{dst}'")
    except Exception as e:
        print(f"❌ Word COM error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if word:
            word.Quit()

def main():
    parser = argparse.ArgumentParser(description="Convert .doc to .docx using MS Word")
    parser.add_argument("src", help="Input .doc file")
    parser.add_argument("dst", help="Output .docx file")
    args = parser.parse_args()

    if not args.src.lower().endswith(".doc"):
        print("⚠️  Warning: Source file does not have .doc extension")
    
    convert_doc_to_docx(args.src, args.dst)

if __name__ == "__main__":
    main()
