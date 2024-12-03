import threading
import subprocess
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException
from time import sleep
from cassandra.cluster import Cluster

CASSANDRA_HOSTS = ["127.0.0.1"]
KEYSPACE = "iot_data_management"
BOOTSTRAP_SERVERS = 'localhost:9092'
INPUT_TOPIC = 'car-sensors'
OUTPUT_TOPIC = 'car-sensors-aggregated'

def check_and_create_topics():
    admin_client = AdminClient({'bootstrap.servers': BOOTSTRAP_SERVERS})

    topics = [INPUT_TOPIC, OUTPUT_TOPIC]
    
    existing_topics = admin_client.list_topics(timeout=10).topics
    
    topics_to_create = [topic for topic in topics if topic not in existing_topics]
    
    if topics_to_create:
        new_topics = [NewTopic(topic, num_partitions=1, replication_factor=1) for topic in topics_to_create]
        try:
            admin_client.create_topics(new_topics)
            print(f"Created topics: {topics_to_create}")
        except Exception as e:
            print(f"Failed to create topics: {e}")
    else:
        print("All topics already exist.")

def connect_to_cassandra():
    try:
        cluster = Cluster(CASSANDRA_HOSTS)
        session = cluster.connect()
        print("Connected to Cassandra.")
        return session
    except Exception as e:
        print(f"Error connecting to Cassandra: {e}")
        raise

def check_and_create_keyspace(session):
    # Check if the keyspace exists
    keyspace_check_query = f"SELECT keyspace_name FROM system_schema.keyspaces WHERE keyspace_name = '{KEYSPACE}'"
    result = session.execute(keyspace_check_query)
    
    if not result:
        # Create keyspace if it doesn't exist
        create_keyspace_query = f"""
        CREATE KEYSPACE IF NOT EXISTS {KEYSPACE} 
        WITH REPLICATION = {{ 'class' : 'SimpleStrategy', 'replication_factor' : 1 }}
        """
        session.execute(create_keyspace_query)
        print(f"Keyspace '{KEYSPACE}' created.")
    else:
        print(f"Keyspace '{KEYSPACE}' already exists.")

def check_and_create_tables(session):
    # Check for 'realtime_metrics' table
    table_check_query = f"SELECT table_name FROM system_schema.tables WHERE keyspace_name = '{KEYSPACE}' AND table_name = 'realtime_metrics'"
    result = session.execute(table_check_query)
    
    if not result:
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {KEYSPACE}.realtime_metrics (
            car_id UUID,
            car_name TEXT,
            timestamp TIMESTAMP,
            owner TEXT,
            location MAP<TEXT, DOUBLE>,  
            status TEXT,
            category TEXT,
            metrics LIST<FROZEN<MAP<TEXT, TEXT>>>,
            PRIMARY KEY (car_id, timestamp)
        ) WITH CLUSTERING ORDER BY (timestamp DESC);
        """
        session.execute(create_table_query)
        print(f"Table 'realtime_metrics' created in keyspace '{KEYSPACE}'.")
    else:
        print("Table 'realtime_metrics' already exists.")

    # Check for 'alerts' table
    table_check_query = f"SELECT table_name FROM system_schema.tables WHERE keyspace_name = '{KEYSPACE}' AND table_name = 'alerts'"
    result = session.execute(table_check_query)
    
    if not result:
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {KEYSPACE}.alerts (
            car_id UUID,
            alert_id UUID,
            sensor_id TEXT,
            sensor_name TEXT,
            alert_cause TEXT,
            severity TEXT,
            metric_value FLOAT,
            metric_unit TEXT,
            timestamp TIMESTAMP,
            PRIMARY KEY (car_id, alert_id)
        );
        """
        session.execute(create_table_query)
        print(f"Table 'alerts' created in keyspace '{KEYSPACE}'.")
    else:
        print("Table 'alerts' already exists.")

def setup_cassandra():
    session = connect_to_cassandra()
    check_and_create_keyspace(session)  
    session.set_keyspace(KEYSPACE) 
    check_and_create_tables(session)
    session.shutdown()

def run_producer():
    subprocess.run(["python", "producer.py"])

def run_stream_processor():
    subprocess.run(["python", "stream_processor.py"])

def run_consumer():
    subprocess.run(["python", "consumer.py"])

def run_all():
    check_and_create_topics()
    setup_cassandra()

    producer_thread = threading.Thread(target=run_producer)
    stream_processor_thread = threading.Thread(target=run_stream_processor)
    consumer_thread = threading.Thread(target=run_consumer)
    
    producer_thread.start()
    stream_processor_thread.start()
    consumer_thread.start()

    producer_thread.join()
    stream_processor_thread.join()
    consumer_thread.join()

if __name__ == "__main__":
    run_all()
