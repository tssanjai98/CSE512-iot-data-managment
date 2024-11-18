from confluent_kafka import Consumer, KafkaException
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import json

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Consume Kafka messages and save them to Cassandra"

    def handle(self, *args, **options):
        # Cassandra setup
        cluster = Cluster(['127.0.0.1'])  # Cassandra IP
        session = cluster.connect()
        session.set_keyspace('telemetry_data')

        # Kafka setup
        consumer = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'iot-consumer-group',
            'auto.offset.reset': 'earliest'
        })

        # Subscribe to Kafka topic
        consumer.subscribe(['telemetry_data'])

        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        continue
                    else:
                        raise KafkaException(msg.error())

                # Parse Kafka message
                try:
                    data = json.loads(msg.value().decode('utf-8'))
                    device_id = data.get('device_id')
                    metric_type = data.get('metric_type')
                    value = data.get('value')
                    location = data.get('location')

                    # Ensure all keys exist
                    if not all([device_id, metric_type, value, location]):
                        raise ValueError(f"Missing keys in data: {data}")

                    # Insert data into Cassandra
                    query = SimpleStatement("""
                        INSERT INTO telemetry (device_id, timestamp, metric_type, value, location)
                        VALUES (%s, toTimestamp(now()), %s, %s, %s)
                    """)
                    session.execute(query, (device_id, metric_type, value, location))

                    self.stdout.write(f"Saved to Cassandra: {data}")

                except json.JSONDecodeError:
                    self.stderr.write(f"Failed to parse message: {msg.value()}")
                except ValueError as e:
                    self.stderr.write(str(e))

        except KeyboardInterrupt:
            self.stdout.write("Kafka consumer stopped.")
        finally:
            consumer.close()
            cluster.shutdown()
