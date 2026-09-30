#!/usr/bin/env python3
"""Tiny static server WITH HTTP Range support (http.server has none) for local checks of the M4 test page.
    python scripts/m4_serve.py _site 8765
"""
import http.server
import os
import re
import sys


class H(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        rng = self.headers.get("Range")
        path = self.translate_path(self.path)
        if not rng or not os.path.isfile(path):
            return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)$", rng)
        size = os.path.getsize(path)
        start = int(m.group(1)) if m and m.group(1) else 0
        end = min(int(m.group(2)), size - 1) if m and m.group(2) else size - 1
        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        self._left = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        left = getattr(self, "_left", None)
        if left is None:
            return super().copyfile(source, outputfile)
        outputfile.write(source.read(left))


if __name__ == "__main__":
    os.chdir(sys.argv[1])
    http.server.ThreadingHTTPServer(("127.0.0.1", int(sys.argv[2])), H).serve_forever()
