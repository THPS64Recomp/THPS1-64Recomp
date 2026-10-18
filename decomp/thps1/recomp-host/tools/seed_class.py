"""Seed a new THPS1 code class from v1.1 (`us11`): decomp/common/seed_class.py does the work (docs there and
in docs/internals/versions.md, "How to add a version").

usage: <python with rabbitizer> -I tools/seed_class.py CLASS ROM --src-rom baserom.z64 --src-main baserom.main.bin
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOST = os.path.dirname(HERE)
sys.path.insert(0, HOST)
import host_root  # noqa: E402  (the shared host tree: decomp/common here, host/ in a game repository)
sys.path.insert(0, host_root.ROOT)
import seed_class  # noqa: E402  (decomp/common/seed_class.py)

if __name__ == "__main__":
    seed_class.main(sys.argv[1:], HOST, "us11")
