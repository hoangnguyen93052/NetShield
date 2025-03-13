import random
import json
import time
import asyncio
import websockets
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class RealTimeDataProcessor:
    def __init__(self, buffer_size=100):
        self.buffer_size = buffer_size
        self.data_buffer = []
        self.is_running = False

    async def consume_data(self, uri):
        async with websockets.connect(uri) as websocket:
            while self.is_running:
                data = await websocket.recv()
                self.process_data(data)

    def process_data(self, data):
        try:
            data_json = json.loads(data)
            timestamp = datetime.now()
            value = data_json['value']
            self.data_buffer.append((timestamp, value))
            if len(self.data_buffer) > self.buffer_size:
                self.data_buffer.pop(0)
            self.plot_data()
        except json.JSONDecodeError:
            print("Error decoding JSON data")

    def plot_data(self):
        if len(self.data_buffer) < 2:
            return
        timestamps, values = zip(*self.data_buffer)
        plt.clf()
        plt.plot(timestamps, values, label='Real-Time Data')
        plt.xlabel('Timestamp')
        plt.ylabel('Value')
        plt.title('Real-Time Data Processing')
        plt.legend()
        plt.pause(0.1)

    def start(self):
        self.is_running = True
        plt.ion()
        plt.figure()
        plt.show()
        print("Starting the real-time data processing...")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.consume_data('ws://localhost:8765'))

    def stop(self):
        self.is_running = False
        print("Stopping the real-time data processing...")

if __name__ == "__main__":
    processor = RealTimeDataProcessor(buffer_size=100)
    try:
        processor.start()
    except KeyboardInterrupt:
        processor.stop()

# Simulated WebSocket server for testing purposes
async def data_server(websocket, path):
    while True:
        data = json.dumps({'value': random.uniform(0, 100)})
        await websocket.send(data)
        await asyncio.sleep(1)

def start_server():
    start_server = websockets.serve(data_server, "localhost", 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    server_task = asyncio.ensure_future(start_server())
    processor = RealTimeDataProcessor(buffer_size=100)

    try:
        processor.start()
    except KeyboardInterrupt:
        processor.stop()