import asyncio
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

server_obj = [None]
server_done = asyncio.Event()

def _serve():
    server = HTTPServer(("0.0.0.0", 8002), SimpleHTTPRequestHandler)
    server_obj[0] = server
    server_done.set()
    server.serve_forever()

async def main():
    t = threading.Thread(target=_serve, daemon=True)
    t.start()
    await server_done.wait()
    print("Server started")
    await asyncio.sleep(1)
    print("Shutting down")
    # This blocks!
    await asyncio.to_thread(server_obj[0].shutdown)
    print("Done")

asyncio.run(main())
