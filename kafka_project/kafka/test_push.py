from cassandra.cluster import Cluster
from cassandra.query import PreparedStatement
from uuid import UUID
from datetime import datetime

# Cassandra connection configuration
KEYSPACE = "iot_data_management"
CASSANDRA_HOSTS = ["127.0.0.1"]

def connect_to_cassandra():
    """Connect to Cassandra and return the session."""
    cluster = Cluster(CASSANDRA_HOSTS)
    session = cluster.connect()
    session.set_keyspace(KEYSPACE)
    return session

def insert_realtime_metrics(session, data):
    """Insert data into the realtime_metrics table."""
    query = """
    INSERT INTO realtime_metrics (
        car_id, car_name, sensor_id, sensor_name, timestamp, 
        metrics_value, metrics_units, location_latitude, 
        location_longitude, status, owner, alert, 
        alert_cause, severity
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        # Prepare parameters
        params = (
            UUID(data["car_id"]),  # Ensure car_id is a UUID
            data["car_name"],
            data["sensor_id"],
            data["sensor_name"],
            datetime.fromisoformat(data["timestamp"]),  # Convert ISO string to datetime
            float(data["metrics"]["value"]),  # Ensure it's a float
            data["metrics"]["units"],
            float(data["location"]["latitude"]),  # Ensure it's a float
            float(data["location"]["longitude"]),  # Ensure it's a float
            data["status"],
            data["owner"],
            bool(data.get("alert", False)),  # Ensure it's a boolean
            data.get("alert_cause", None),  # Allow None
            data.get("severity", None)  # Allow None
        )

        # Debug the parameters
        print(f"Debug Insert Params: {params}")

        # Use a PreparedStatement to ensure proper formatting
        prepared = session.prepare(query)
        session.execute(prepared, params)

        print(f"Inserted data into realtime_metrics: {data}")
    except Exception as e:
        print(f"Failed to insert data into realtime_metrics: {data}")
        print(f"Error: {e}")

if __name__ == "__main__":
    # Connect to Cassandra
    session = connect_to_cassandra()

    # Sample data without alert
    sample_data = {
        "car_id": "31f7274e-1859-4247-823f-742705209c08",
        "car_name": "Toyota Camry",
        "sensor_id": "battery_level_sensor",
        "sensor_name": "Battery Level Sensor",
        "timestamp": "2024-11-23T11:40:19.598872+00:00",
        "metrics": {"value": 85.72, "units": "%"},
        "location": {"latitude": 40.712776, "longitude": -74.005974},
        "status": "active",
        "owner": "Samuel Jackson",
        "alert": False,
        "alert_cause": None,
        "severity": None
    }

    # Insert the sample data
    # print(sample_data)
    insert_realtime_metrics(session, sample_data)

    # # Close the Cassandra session
    session.cluster.shutdown()


# (UUID('31f7274e-1859-4247-823f-742705209c08'), 'Toyota Camry', 'battery_level_sensor', 'Battery Level Sensor', datetime.datetime(2024, 11, 25, 11, 40, 19, 598872, tzinfo=datetime.timezone.utc), 85.72, '%', 40.712776, -74.005974, 'active', 'Samuel Jackson', False, None, None)



# (UUID('31f7274e-1859-4247-823f-742705209c08'), 'Toyota Camry', 'tire_pressure_sensor', 'Tire Pressure Sensor', datetime.datetime(2024, 11, 27, 12, 11, 8, 467910, tzinfo=datetime.timezone.utc), 44.98, 'PSI', 27.881732, 147.126873, 'active', 'Samuel Jackson', False, None, None)