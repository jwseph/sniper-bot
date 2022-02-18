from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


async def app(scope, receive, send):
    """The simplest of ASGI apps, displaying scope."""
    headers = [(b"content-type", b"text/html")]
    body = open('index.html', 'rb').read()
    await send({"type": "http.response.start", "status": 200, "headers": headers})
    await send({"type": "http.response.body", "body": body})


app = FastAPI()
app.mount("/", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)