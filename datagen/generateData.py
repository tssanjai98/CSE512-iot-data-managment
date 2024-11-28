from faker import Faker
import random
import json
from decimal import Decimal

faker = Faker()

def generate_car_data(num_cars=300):
    categories = ["sedan", "suv", "truck"]
    alert_causes = ["High Engine Temp", "Low Battery Level", "Tire Pressure Issue", "Speed Limit Exceeded", "Fuel Level Low"]
    data = []
    for i in range(num_cars):
        metrics = [
            {
                "sensor_id": "engine_temp_sensor",
                "sensor_name": "Engine Temperature Sensor",
                "value": round(random.uniform(70, 150), 2),  # Engine temp in Celsius
                "units": "C",
                "alert": random.choice([True, False]),
                "alert_cause": random.choice(alert_causes) if random.choice([True, False]) else None,
                "severity": random.choice(["Warning", "Critical"]) if random.choice([True, False]) else None
            },
            {
                "sensor_id": "tire_pressure_sensor",
                "sensor_name": "Tire Pressure Sensor",
                "value": round(random.uniform(30, 45), 2),  # Tire pressure in PSI
                "units": "PSI",
                "alert": random.choice([True, False]),
                "alert_cause": random.choice(alert_causes) if random.choice([True, False]) else None,
                "severity": random.choice(["Warning", "Critical"]) if random.choice([True, False]) else None
            },
            {
                "sensor_id": "battery_level_sensor",
                "sensor_name": "Battery Level Sensor",
                "value": round(random.uniform(5, 100), 2),  # Battery level in percentage
                "units": "%",
                "alert": random.choice([True, False]),
                "alert_cause": random.choice(alert_causes) if random.choice([True, False]) else None,
                "severity": random.choice(["Warning", "Critical"]) if random.choice([True, False]) else None
            },
            {
                "sensor_id": "speed_sensor",
                "sensor_name": "Speed Sensor",
                "value": round(random.uniform(0, 200), 2),  # Speed in km/h
                "units": "km/h",
                "alert": random.choice([True, False]),
                "alert_cause": random.choice(alert_causes) if random.choice([True, False]) else None,
                "severity": random.choice(["Warning", "Critical"]) if random.choice([True, False]) else None
            },
            {
                "sensor_id": "fuel_sensor",
                "sensor_name": "Fuel Level Sensor",
                "value": round(random.uniform(5, 70), 2),  # Fuel level in liters
                "units": "liters",
                "alert": random.choice([True, False]),
                "alert_cause": random.choice(alert_causes) if random.choice([True, False]) else None,
                "severity": random.choice(["Warning", "Critical"]) if random.choice([True, False]) else None
            }
        ]

        car = {
            "car_id": faker.uuid4(),
            "car_name": faker.random_element(["Toyota Camry", "Honda Accord", "Ford Explorer", "Tesla Model 3", "Chevrolet Silverado"]),
            "timestamp": faker.date_time_this_year().isoformat(),
            "owner": faker.name(),
            "location": {
                "latitude": round(faker.latitude(), 6),
                "longitude": round(faker.longitude(), 6)
            },
            "status": random.choice(["active", "inactive", "maintenance", "error"]),
            "category": random.choice(categories),  # Car category: sedan, SUV, truck
            "metrics": metrics  # List of sensors and their values
        }
        data.append(car)
    return data

# Generate and save to a JSON file
fake_data = generate_car_data(300)


# Custom JSON encoder to convert Decimal to float
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


# Save to file
output_path = "/Users/navein/Documents/DDS-Project/CSE512-iot-data-managment/datagen/fake_data.json"
# Save to file using the custom encoder
with open(output_path, "w") as f:
    json.dump(fake_data, f, indent=4, cls=DecimalEncoder)

print(f"Fake car data generated and saved to {output_path}")
