import asyncio, json, ssl

async def main():
    import websockets

    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjYWQxZDlhMTUzMzc0YzhiYTc3ZGU4Y2I1MGZjZmE4YiIsImlhdCI6MTc3MTYzOTkzMiwiZXhwIjoyMDg2OTk5OTMyfQ.lqdNMH1auAqt0A0-SPcJMdQFrr0i2oyUenMoknY8wls'

    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    uri = 'wss://192.168.178.54:8123/api/websocket'
    async with websockets.connect(uri, ssl=ssl_ctx) as ws:
        msg = json.loads(await ws.recv())
        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        msg = json.loads(await ws.recv())
        print("Auth:", msg.get("type"))

        if msg["type"] == "auth_ok":
            # Get addon info
            await ws.send(json.dumps({"id": 1, "type": "supervisor/api", "endpoint": "/addons/a0d7b954_adguard/info", "method": "get"}))
            msg = json.loads(await ws.recv())
            if msg.get("success"):
                data = msg.get("result", {})
                print(json.dumps(data, indent=2))
            else:
                print("Error:", json.dumps(msg)[:2000])

asyncio.run(main())
