import asyncio, json, ssl

async def main():
    try:
        import websockets
    except ImportError:
        import subprocess
        subprocess.check_call(['pip', 'install', 'websockets'])
        import websockets

    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjYWQxZDlhMTUzMzc0YzhiYTc3ZGU4Y2I1MGZjZmE4YiIsImlhdCI6MTc3MTYzOTkzMiwiZXhwIjoyMDg2OTk5OTMyfQ.lqdNMH1auAqt0A0-SPcJMdQFrr0i2oyUenMoknY8wls'

    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    uri = 'wss://192.168.178.54:8123/api/websocket'
    async with websockets.connect(uri, ssl=ssl_ctx) as ws:
        msg = json.loads(await ws.recv())
        print("Auth phase:", msg.get("type"))

        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        msg = json.loads(await ws.recv())
        print("Auth result:", msg.get("type"))

        if msg["type"] == "auth_ok":
            await ws.send(json.dumps({"id": 1, "type": "supervisor/api", "endpoint": "/addons", "method": "get"}))
            msg = json.loads(await ws.recv())
            print("Addons success:", msg.get("success"))
            if msg.get("success"):
                addons = msg.get("result", {}).get("addons", [])
                print("Total addons:", len(addons))
                for a in addons:
                    slug = a.get("slug", "")
                    name = a.get("name", "")
                    if "adguard" in slug.lower() or "adguard" in name.lower():
                        state = a.get("state", "unknown")
                        version = a.get("version", "unknown")
                        print("FOUND AdGuard: slug=" + slug + " name=" + name + " state=" + state + " version=" + version)
            else:
                print("Error:", json.dumps(msg)[:1000])

asyncio.run(main())
