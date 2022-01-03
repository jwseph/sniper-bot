"""A barebones ASGI app that dumps scope."""

import uvicorn
from threading import Thread
import pprint

def pretty_html_bytes(obj):
    """Pretty print a Python object in <pre> tags."""
    pp = pprint.PrettyPrinter(indent=2, width=256)
    prettified = pp.pformat(obj)
    return f"<pre>{prettified}</pre>".encode()

async def app(scope, receive, send):
    """The simplest of ASGI apps, displaying scope."""
    headers = [(b"content-type", b"text/html")]
    body = pretty_html_bytes(scope)
    await send({"type": "http.response.start", "status": 200, "headers": headers})
    await send({"type": "http.response.body", "body": body})

def run():
  uvicorn.run(app, host="0.0.0.0", port=8000)

def keep_alive():
  Thread(target=run).start()
