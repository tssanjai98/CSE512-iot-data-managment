from faker import Faker
import random
import json

faker = Faker()

def generate_data(num_devices=300):
    categories = ["sensor", "actuator", "communication", "power", "tracking"]
    alert_causes = ["Overheating", "Low Battery", "Connection Loss", "High Latency", "Sensor Malfunction"]
    data = []
    for i in range(num_devices):
        alerts = random.choice([True, False])  # Randomly decide if this device has an alert
        device = {
            "device_id": f"device_{i + 1}",
            "category": random.choice(categories),
            "device_name": faker.catch_phrase(),
            "timestamp": faker.date_time_this_year().isoformat(),
            "metrics": {
                "temperature": float(round(random.uniform(-40, 85), 2)),
                "pressure": float(round(random.uniform(950, 1050), 2)),
                "humidity": float(round(random.uniform(0, 100), 2)),
                "speed": float(round(random.uniform(0, 30000), 2)),
                "battery_level": float(round(random.uniform(0, 100), 2)),
                "latency": float(round(random.uniform(0, 500), 2)),
                "uptime": float(round(random.uniform(0, 10000), 2)),
                "signal_strength": float(round(random.uniform(-100, 0), 2)),
                "energy_consumption": float(round(random.uniform(0, 500), 2)),
            },
            "location": {
                "type": "coordinates",
                "latitude": float(faker.latitude()),
                "longitude": float(faker.longitude()),
                "region": random.choice(["Orbit A", "Orbit B", "Earth Base", "Station Alpha"]),
            },
            "status": random.choice(["active", "inactive", "maintenance", "error"]),
            "alerts": alerts,
            "alert_cause": random.choice(alert_causes) if alerts else None,  # Assign a cause if alerts=True
            "health": random.choice(["good", "warning", "critical"]),
            "owner": faker.company(),
            "last_maintenance": faker.date_this_year().isoformat(),
            "connections": random.randint(1, 100),
        }
        data.append(device)
    return data

# Generate and save to a JSON file
fake_data = generate_data(300)

# Save to file
with open("/Users/navein/Documents/DDS-Project/iot-dashboard/src/datagen/fake_data.json", "w") as f:
    json.dump(fake_data, f, indent=4)
