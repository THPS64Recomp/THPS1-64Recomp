"""Translate THPS1 data addresses (default source class us11) to a new code class through sigmatch's matched
function pairs: decomp/common/translate_data.py does the work (docs there).

usage: python3 -I tools/translate_data.py DST_CLASS [SRC_CLASS=us11]
Needs build/<dst game>.main.bin and build/<dst game>.sigmatch.json (tools/seed_class.py).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOST = os.path.dirname(HERE)
sys.path.insert(0, HOST)
import host_root  # noqa: E402  (the shared host tree: decomp/common here, host/ in a game repository)
sys.path.insert(0, host_root.ROOT)
import translate_data  # noqa: E402  (decomp/common/translate_data.py)

if __name__ == "__main__":
    translate_data.main(sys.argv[1:], HOST, "us11")
