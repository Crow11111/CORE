import asyncio
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

async def main():
    server_obj = [None]
    server_done = asyncio.Event()

    def _serve():
        server = HTTPServer(("0.0.0.0", 8003), SimpleHTTPRequestHandler)
        server_obj[0] = server
        # use loop.call_soon_threadsafe to set the event
        loop.call_soon_threadsafe(server_done.set)
        server.serve_forever()

    loop = asyncio.get_running_loop()
    t = threading.Thread(target=_serve, daemon=True)
    t.start()
    await server_done.wait()
    print("Server started")
    await asyncio.sleep(1)
    print("Shutting down")
    await asyncio.to_thread(server_obj[0].shutdown)
    print("Done")

asyncio.run(main())
