from confluent_kafka import Consumer, KafkaError
from cassandra.cluster import Cluster
import json
from uuid import UUID
from datetime import datetime

KEYSPACE = "iot_data_management"
CASSANDRA_HOSTS = ["127.0.0.1"]
BOOTSTRAP_SERVERS = 'localhost:9092'
INPUT_TOPIC = 'car-sensors-aggregated'

def connect_to_cassandra():
    try:
        cluster = Cluster(CASSANDRA_HOSTS)
        session = cluster.connect()
        session.set_keyspace(KEYSPACE)
        print("Connected to Cassandra.")
        return session
    except Exception as e:
        print(f"Error connecting to Cassandra: {e}")
        raise

def insert_realtime_metrics(session, data):
    """Inserts real-time metrics into the Cassandra table with metric values as text."""
    query = """
    INSERT INTO realtime_metrics (
        car_id, car_name, timestamp, owner, location, 
        status, category, metrics
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        prepared = session.prepare(query)

        
        metrics = [
            {
                "sensor_id": metric["sensor_id"],
                "sensor_name": metric["sensor_name"],
                "value": str(metric["value"]), 
                "units": metric["units"],
                "alert": str(metric["alert"]),
                "alert_cause": str(metric.get("alert_cause", None)),
                "severity": str(metric.get("severity", None))
            }
            for metric in data["metrics"]
        ]

        location = {
            "latitude": float(data["location"]["latitude"]),
            "longitude": float(data["location"]["longitude"])
        }

        params = (
            UUID(data["car_id"]),
            data["car_name"],
            datetime.fromisoformat(data["timestamp"]),
            data["owner"],
            location,  
            data["status"],
            data["category"],
            metrics
        )

        session.execute(prepared, params)
        print(f"Successfully inserted into realtime_metrics")

    except Exception as e:
        print(f"Failed to insert data into realtime_metrics: {data}")
        print(f"Error: {e}")

def insert_alert(session, alert_data, metric_data):
    """Inserts alerts into the Cassandra alerts table with metric value as float."""
    query = """
    INSERT INTO alerts (
        alert_id, car_id, sensor_id, sensor_name, alert_cause, 
        severity, metric_value, metric_unit, timestamp
    ) VALUES (uuid(), ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        prepared = session.prepare(query)

        # Prepare the alert parameters, including metric value as float
        params = (
            UUID(alert_data["car_id"]),
            alert_data["sensor_id"],
            alert_data["sensor_name"],
            alert_data.get("alert_cause", None),
            alert_data.get("severity", None),
            float(metric_data["value"]),   # Convert metric value to float
            metric_data["units"],          # Add the metric unit as a string
            datetime.fromisoformat(alert_data["timestamp"])
        )

        # Execute the prepared statement
        session.execute(prepared, params)
        print(f"Successfully inserted alert with metric value and unit")

    except Exception as e:
        print(f"Failed to insert alert with metric value and unit")
        print(f"Error: {e}")

def consume_from_kafka():
    """Consumes messages from Kafka and inserts them into Cassandra."""
    consumer_config = {
        'bootstrap.servers': BOOTSTRAP_SERVERS,
        'group.id': 'cars_aggregated_group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False
    }

    consumer = Consumer(consumer_config)
    consumer.subscribe([INPUT_TOPIC])

    session = connect_to_cassandra()

    try:
        while True:
            msg = consumer.poll(2.0)
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"End of partition: {msg.topic()} [{msg.partition()}]")
                else:
                    print(f"Error: {msg.error()}")
                continue

            try:
                data = json.loads(msg.value().decode('utf-8'))
                insert_realtime_metrics(session, data)

                # Process alerts for each metric in the data
                for metric in data["metrics"]:
                    if metric.get("alert", False):
                        alert_data = {
                            "car_id": data["car_id"],
                            "sensor_id": metric["sensor_id"],
                            "sensor_name": metric["sensor_name"],
                            "alert_cause": metric.get("alert_cause", None),
                            "severity": metric.get("severity", None),
                            "timestamp": data["timestamp"]
                        }

                        # Pass metric data (value and units) to insert_alert
                        metric_data = {
                            "value": metric["value"],
                            "units": metric["units"]
                        }

                        insert_alert(session, alert_data, metric_data)

                consumer.commit()

            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
            except Exception as e:
                print(f"Unexpected error while processing message: {e}")

    except KeyboardInterrupt:
        print("Shutting down consumer...")
    finally:
        consumer.close()
        session.cluster.shutdown()



if __name__ == "__main__":
    consume_from_kafka()