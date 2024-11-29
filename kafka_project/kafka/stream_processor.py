from streamz import Stream
from kafka import KafkaProducer
from datetime import datetime, timezone
import json

# Kafka Configuration
BOOTSTRAP_SERVERS = 'localhost:9092'
INPUT_TOPIC = 'car-sensors'
OUTPUT_TOPIC = 'car-sensors-aggregated'

# Thresholds for various sensors
THRESHOLDS = {
    "fuel_sensor": {"low": 10},
    "speed_sensor": {"high": 200},
    "engine_temp_sensor": {"high": 110},
    "tire_pressure_sensor": {"low": 32},
    "battery_level_sensor": {"low": 20}
}

# Kafka Producer to send enriched data
producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Function to generate alerts based on the metric value and thresholds
def get_alert(sensor_id, metric_value):
    """Generates alerts based on the sensor ID and metric value."""
    if sensor_id in THRESHOLDS:
        if "low" in THRESHOLDS[sensor_id] and metric_value < THRESHOLDS[sensor_id]["low"]:
            return True, f"Low {sensor_id.replace('_', ' ').title()}", "Critical"
        if "high" in THRESHOLDS[sensor_id] and metric_value > THRESHOLDS[sensor_id]["high"]:
            return True, f"High {sensor_id.replace('_', ' ').title()}", "Warning"
    return False, None, None

# Process each message, enrich it with alert data, and prepare for sending to Kafka
def process_message(batch):
    """Processes and enriches a batch of Kafka messages."""
    enriched_batch = []
    for record in batch:
        data = json.loads(record.decode('utf-8'))

        # Enrich each metric in the metrics list
        for metric in data["metrics"]:
            sensor_id = metric["sensor_id"]
            metric_value = metric["value"]

            # Generate alerts for each sensor metric
            alert, alert_cause, severity = get_alert(sensor_id, metric_value)

            # Enrich the metric with alert data
            metric["alert"] = alert
            metric["alert_cause"] = alert_cause
            metric["severity"] = severity

        # Enrich the entire message (car data)
        enriched_data = {
            **data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": data["metrics"]
        }
        enriched_batch.append(enriched_data)

    return enriched_batch

# Send the enriched batch to Kafka
def send_to_kafka(batch):
    """Sends the enriched batch to Kafka."""
    for enriched_data in batch:
        producer.send(OUTPUT_TOPIC, value=enriched_data)
        print(f"Message sent to {OUTPUT_TOPIC}")

# Define the stream to consume data from Kafka and process it in batches
source = Stream.from_kafka_batched(
    INPUT_TOPIC,
    consumer_params={
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "group.id": "stream_processor_group",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False
    },
    max_batch_size=10
)

# Process the incoming batch and send it to Kafka
source.map(process_message).sink(send_to_kafka)

# Start processing the stream
source.start()

while True:
    pass




