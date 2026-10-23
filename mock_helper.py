#!/usr/bin/env python3
"""Mock magled-helper for protocol testing (responds like the real daemon)."""
import os, socket, sys, threading, time

path = os.environ.get("MAGLED_SOCK", "/var/run/magled.sock")
duration = int(os.environ.get("DURATION", "20"))
allowed = {"00", "01", "03", "04", "06", "07", "19"}

try:
    os.unlink(path)
except FileNotFoundError:
    pass

srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
srv.bind(path)
srv.listen(8)

def serve():
    while True:
        c, _ = srv.accept()
        c.settimeout(5)
        data = b""
        try:
            while not data.endswith(b"\n"):
                chunk = c.recv(256)
                if not chunk:
                    break
                data += chunk
        except socket.timeout:
            pass
        req = data.decode(errors="replace").strip()
        print("MOCK got:", req, flush=True)
        if req == "ping":
            r = b"OK 1.0\n"
        elif req == "get":
            r = b"OK 01\n"
        elif req.startswith("set "):
            v = req.split()[1].lower()
            r = ("OK %s\n" % v).encode() if v in allowed else b"ERR bad-value\n"
        else:
            r = b"ERR bad-request\n"
        try:
            c.sendall(r)
        finally:
            c.close()

threading.Thread(target=serve, daemon=True).start()
time.sleep(duration)
print("mock done", flush=True)
