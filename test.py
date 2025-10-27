import asyncio
import websockets
import json

async def listen():
    uri =  "ws://localhost:8000/api/v1/ws/auction/live"
    headers =[("Authorization","eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiZW1haWwiOiJ1ZzIxMDIwMzBAY3NlLnBzdHUuYWMuYmQiLCJleHAiOjE3NjE1NDcyNDd9.lcLTJh9NKAf2cL1JIvT0uR9ExB08IU1rBWwOYaWnKLU")]
    async with websockets.connect(uri,additional_headers=headers) as websocket:
        
        # first status ----------------------->
        greeting = await websocket.recv()
        print(f"Received: {greeting}")

        #  live messages from our websockets
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received: {data}")

asyncio.get_event_loop().run_until_complete(listen())

