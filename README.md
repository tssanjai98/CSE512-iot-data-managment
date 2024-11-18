Download Kafka from the following:

https://kafka.apache.org/downloads

Select the Binary Downloads with Scala 2.13

Needs Java Runtime

```sql
brew install openjdk@17

# Paste the following the ~/.zshrc
export JAVA_HOME="/opt/homebrew/opt/openjdk@17"
export PATH="$JAVA_HOME/bin:$PATH"

# Run the following to save the file
source ~/.zshrc

java -version
```

Extract the Kafka Package

```bash
tar -xzf kafka_2.13-3.5.0.tgz

cd kafka_2.13-3.5.0

# Start the ZooKeeper Server
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start the Kafka Broker (On a different tab)
bin/kafka-server-start.sh config/server.properties

# This creates a topic called telemetry_data. 
bin/kafka-topics.sh --create --topic telemetry_data --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Verify if the topic exists
bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# To produce data
bin/kafka-console-producer.sh --topic telemetry_data --bootstrap-server localhost:9092
> {"device_id": "spacecraft_1", "metric_type": "temperature", "value": 42.3}
> {"device_id": "spacecraft_2", "metric_type": "radiation", "value": 15.6}

# Open another terminal and consume messages from the same topic
bin/kafka-console-consumer.sh --topic telemetry_data --bootstrap-server localhost:9092 --from-beginning
```

Install Kafka for Python

```bash
pip install confluent-kafka
```

Install Cassandra and connect to it

```bash
docker pull cassandra:latest

# To start the docker container
docker run --name cassandra -d -p 9042:9042 cassandra:latest

# To check the status
docker ps
```

Connect to the Cassandra DB shell and create the table

```sql
$docker exec -it cassandra cqlsh

CREATE KEYSPACE telemetry_data WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE telemetry_data.telemetry (
    device_id TEXT,
    timestamp TIMESTAMP,
    metric_type TEXT,
    value FLOAT,
    location TEXT,
    PRIMARY KEY ((device_id), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

DESCRIBE KEYSPACE telemetry_data;
```
