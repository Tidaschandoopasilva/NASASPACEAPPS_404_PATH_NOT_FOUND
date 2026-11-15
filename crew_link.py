"""Read-only JSON Line snapshots for crew terminals on the habitat LAN."""
import hmac
import json
import socket
import socketserver
from contextlib import contextmanager
from threading import Thread


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.request.settimeout(5)
        try:
            message = json.loads(self.rfile.readline(4097))
            token = message.get("token", "")
            if not isinstance(token, str) or not hmac.compare_digest(token, self.server.token):
                result = {"error": "Access denied"}
            elif message.get("command") != "status":
                result = {"error": "Unknown command"}
            else:
                result = self.server.read_status()
        except (AttributeError, OSError, ValueError):
            result = {"error": "Invalid request"}
        self.wfile.write(json.dumps(result, allow_nan=False).encode() + b"\n")


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address, read_status, token):
        self.read_status, self.token = read_status, token
        super().__init__(address, Handler)


def fetch(host, port, token):
    with socket.create_connection((host, port), timeout=8) as connection:
        connection.sendall(json.dumps({"command": "status", "token": token}).encode() + b"\n")
        with connection.makefile("rb") as reader:
            return json.loads(reader.readline(8_000_000))




@contextmanager
def start(host, port, token):
    from app.habitat import crew_status
    with Server((host, port), crew_status, token) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield server
        finally:
            server.shutdown()
            thread.join()


if __name__ == "__main__":
    import argparse
    import getpass
    from time import sleep
    parser = argparse.ArgumentParser(description="Read the habitat's simulated expedition report")
    parser.add_argument("host")
    parser.add_argument("--port", type=int, default=4040)
    parser.add_argument("--watch", action="store_true", help="Refresh simulated telemetry once a second")
    args = parser.parse_args()
    code = getpass.getpass("Habitat session code: ")
    if not args.watch:
        print(json.dumps(fetch(args.host, args.port, code), indent=2))
    else:
        try:
            while True:
                result = fetch(args.host, args.port, code)
                print(json.dumps(result), flush=True)
                if "error" in result:
                    break
                sleep(1)
        except KeyboardInterrupt:
            pass
