import threading
import subprocess


def run_producer():
    subprocess.run(["python", "producer.py"])

def run_stream_processor():
    subprocess.run(["python", "stream_processor.py"])

def run_consumer():
    subprocess.run(["python", "consumer.py"])

def run_all():

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
