import time
import random
import requests

blocks = ["Marshalltown-A", "Marshalltown-B", "Marshalltown-C"]

print("Starting PipeWatch Telemetry Simulator...")

while True:
    for block in blocks:
        # 10% chance to simulate a burst pipe (high flow, low pressure)
        is_burst = random.random() < 0.1 
        
        payload = {
            "block_id": block,
            "flow_rate": random.uniform(80.0, 100.0) if is_burst else random.uniform(10.0, 25.0),
            "pressure": random.uniform(40.0, 70.0) if is_burst else random.uniform(300.0, 400.0)
        }
        
        try:
            requests.post("http://localhost:8000/api/telemetry", json=payload)
            print(f"Transmitted: {block} | Flow: {payload['flow_rate']:.1f} | Pressure: {payload['pressure']:.1f}")
        except requests.exceptions.ConnectionError:
            print("Backend offline. Waiting for FastAPI server...")
            
    time.sleep(3) # Send new data every 3 seconds