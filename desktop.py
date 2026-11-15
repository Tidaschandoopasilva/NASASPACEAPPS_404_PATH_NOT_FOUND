"""Launch the complete interface in a Python-owned desktop window."""
import argparse
import os
import secrets
import socket
import threading
from contextlib import contextmanager
from pathlib import Path
from time import monotonic, sleep

import uvicorn
from fastapi.staticfiles import StaticFiles

from app.main import app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-lan", metavar="BASE_IP")
    parser.add_argument("--lan-port", type=int, default=4040)
    args = parser.parse_args()
    import webview

    root = Path(__file__).resolve().parent
    app.mount("/", StaticFiles(directory=root / "apps/web/dist", html=True))
    with socket.create_server(("127.0.0.1", 0)) as listener:
        port = listener.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
        thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
        thread.start()
        try:
            with server_ready(server, thread):
                if args.listen_lan:
                    from crew_link import start
                    token = secrets.token_hex(16)
                    with start(args.listen_lan, args.lan_port, token):
                        open_window(webview, port, f"LAN {args.listen_lan}:{args.lan_port} · code {token}")
                else:
                    open_window(webview, port, "LAN off")
        finally:
            server.should_exit = True
            thread.join(timeout=10)


def open_window(webview, port, subtitle):
    window = webview.create_window("404 | Jezero Habitat V7 · " + subtitle,
                                   f"http://127.0.0.1:{port}", width=1450, height=950,
                                   min_size=(960, 680))
    webview.settings["ALLOW_DOWNLOADS"] = True
    webview.start(gui="edgechromium" if os.name == "nt" else None)
    return window



@contextmanager
def server_ready(server, thread):
    deadline = monotonic() + 10
    while not server.started and thread.is_alive() and monotonic() < deadline:
        sleep(.05)
    if not server.started:
        raise RuntimeError("Habitat Python service could not be started")
    yield


if __name__ == "__main__":
    main()
