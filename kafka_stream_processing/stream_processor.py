from streamz import Stream
from kafka import KafkaProducer
from datetime import datetime, timezone
import json


BOOTSTRAP_SERVERS = 'localhost:9092'
INPUT_TOPIC = 'car-sensors'
OUTPUT_TOPIC = 'car-sensors-aggregated'


THRESHOLDS = {
    "fuel_sensor": {"low": 10, "wlow": 20},
    "speed_sensor": {"whigh": 160, "high": 200},
    "engine_temp_sensor": {"whigh": 90, "high": 110},
    "tire_pressure_sensor": {"low": 15, "wlow": 20},
    "battery_level_sensor": {"low": 20, "wlow": 35}
}

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def get_alert(sensor_id, metric_value):
    """Generates alerts based on the sensor ID and metric value."""
    if sensor_id in THRESHOLDS:
        if "low" in THRESHOLDS[sensor_id] and metric_value < THRESHOLDS[sensor_id]["wlow"] and metric_value > THRESHOLDS[sensor_id]["low"]:
            return True, f"Low {sensor_id.replace('_', ' ').title()}", "Warning"
        if "low" in THRESHOLDS[sensor_id] and metric_value < THRESHOLDS[sensor_id]["low"]:
            return True, f"Low {sensor_id.replace('_', ' ').title()}", "Critical"
        if "high" in THRESHOLDS[sensor_id] and metric_value > THRESHOLDS[sensor_id]["whigh"] and metric_value < THRESHOLDS[sensor_id]["high"]:
            return True, f"High {sensor_id.replace('_', ' ').title()}", "Warning"
        if "high" in THRESHOLDS[sensor_id] and metric_value > THRESHOLDS[sensor_id]["high"]:
            return True, f"High {sensor_id.replace('_', ' ').title()}", "Critical"
    return False, None, None


def process_message(batch):
    """Processes and enriches a batch of Kafka messages."""
    enriched_batch = []
    for record in batch:
        data = json.loads(record.decode('utf-8'))

        for metric in data["metrics"]:
            sensor_id = metric["sensor_id"]
            metric_value = metric["value"]

            alert, alert_cause, severity = get_alert(sensor_id, metric_value)

            metric["alert"] = alert
            metric["alert_cause"] = alert_cause
            metric["severity"] = severity

        enriched_data = {
            **data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": data["metrics"]
        }
        enriched_batch.append(enriched_data)

    return enriched_batch

def send_to_kafka(batch):
    """Sends the enriched batch to Kafka."""
    for enriched_data in batch:
        producer.send(OUTPUT_TOPIC, value=enriched_data)
        print(f"[Stream Processor] : Message sent to {OUTPUT_TOPIC}")

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

source.map(process_message).sink(send_to_kafka)

source.start()

while True:
    pass




