import asyncio
import websockets

URL = "wss://qurodesk.in/ws/dashboard/1/"

async def connect_user(i):
    try:
        async with websockets.connect(URL) as ws:
            print(f"User {i} connected")
            await asyncio.sleep(60)
    except Exception as e:
        print(f"User {i} failed: {e}")

async def main():
    users = int(input("Enter users: "))
    tasks = [connect_user(i) for i in range(users)]
    await asyncio.gather(*tasks)

asyncio.run(main())
