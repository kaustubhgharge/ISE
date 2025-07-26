import requests
import time
import random

bins = [
    {"bin_id": "bin_1", "location": [51.96, 7.62]},
    {"bin_id": "bin_2", "location": [51.97, 7.63]},
    {"bin_id": "bin_3", "location": [51.95, 7.61]},
]

URL = "http://127.0.0.1:5000/sensor-data"

def simulate():
    while True:
        bin = random.choice(bins)
        fill_level = random.randint(10, 100)
        last_emptied_days = random.randint(0, 10)
        data = {
            "bin_id": bin['bin_id'],
            "location": bin['location'],
            "fill_level": fill_level,
            "last_emptied_days": last_emptied_days,
        }
        try:
            response = requests.post(URL, json=data)
            print(f"Sent update for {bin['bin_id']}: fill_level={fill_level}")
        except Exception as e:
            print(f"Error sending data: {e}")
        time.sleep(10)  # every 10 seconds

if __name__ == "__main__":
    simulate()
