from confluent_kafka import Producer
import json
import random
import time
from datetime import datetime, timezone

producer = Producer({'bootstrap.servers': 'localhost:9092'})

topic_name = "car-sensors"
bootstrap_servers = "localhost:9092"

def delivery_report(err, msg):
    """Reports the delivery status of messages."""
    if err is not None:
        print(f"[Producer] : Message delivery failed: {err}")
    else:
        print(f"[Producer] : Message delivered to {msg.topic()} [{msg.partition()}]")

def generate_car_data():
    """Generates mock IoT data for multiple cars"""
    cars = [
        {"car_id": "50c7c87d-fc40-400a-928a-27868ead69c3", "car_name": "Honda CRV", "owner": "Joshua Hunter", "status": "maintenance", "category": "suv"},
        {"car_id": "31f7274e-1859-4247-823f-742705209c08", "car_name": "Toyota Camry", "owner": "Samuel Jackson", "status": "active", "category": "sedan"},
        {"car_id": "d14b8a42-829b-4a3f-b62e-e6df8e88b4a5", "car_name": "Ford Mustang", "owner": "Megan Lee", "status": "inactive", "category": "coupe"},
    ]
    
    # Random location data (latitude, longitude)
    location = {
        "latitude": round(random.uniform(-90, 90), 6),
        "longitude": round(random.uniform(-180, 180), 6)
    }

    # Define sensors with required fields (without alert, alert_cause, severity for now)
    sensors = [
        {"id": "engine_temp_sensor", "name": "Engine Temperature Sensor", "units": "C"},
        {"id": "tire_pressure_sensor", "name": "Tire Pressure Sensor", "units": "PSI"},
        {"id": "battery_level_sensor", "name": "Battery Level Sensor", "units": "%"},
        {"id": "speed_sensor", "name": "Speed Sensor", "units": "km/h"},
        {"id": "fuel_sensor", "name": "Fuel Level Sensor", "units": "liters"}
    ]

    while True:
        for car in cars:
            metrics = []
            for sensor in sensors:
                metric = {
                    "sensor_id": sensor["id"],
                    "sensor_name": sensor["name"],
                    "value": generate_sensor_value(sensor["id"]),
                    "units": sensor["units"]
                }
                metrics.append(metric)

            data = {
                "car_id": car["car_id"],
                "car_name": car["car_name"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "owner": car["owner"],
                "location": location,
                "status": car["status"],
                "category": car["category"],
                "metrics": metrics
            }

            producer.produce(topic_name, key=car["car_id"], value=json.dumps(data), callback=delivery_report)
            producer.flush()
        time.sleep(5)

def generate_sensor_value(sensor_id):
    """Generates sensor-specific metric values based on sensor type"""
    sensor_ranges = {
        "speed_sensor": (0, 240),         
        "fuel_sensor": (0, 100),          
        "engine_temp_sensor": (60, 115),  
        "tire_pressure_sensor": (10, 40), 
        "battery_level_sensor": (0, 100)
    }
    min_val, max_val = sensor_ranges.get(sensor_id, (0, 100))
    return round(random.uniform(min_val, max_val), 2)

if __name__ == "__main__":
    generate_car_data()