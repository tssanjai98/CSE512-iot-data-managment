from confluent_kafka import Producer
import json
import random
import time

producer = Producer({'bootstrap.servers': 'localhost:9092'})

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def generate_telemetry():
    metrics = ["temperature", "radiation", "oxygen", "power"]
    while True:
        data = {
            "device_id": f"spacecraft_{random.randint(1, 5)}",
            "metric_type": random.choice(metrics),
            "value": round(random.uniform(0, 100), 2),
            "location": "Orbit A"
        }
        producer.produce('telemetry_data', key=str(data['device_id']), value=json.dumps(data), callback=delivery_report)
        producer.flush()
        time.sleep(1)

if __name__ == "__main__":
    generate_telemetry()