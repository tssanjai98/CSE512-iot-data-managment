# IoT Data Management Dashboard

Requirements:

1. **Python 3.11** (Only compatible with Python3.11)
2. **Java JDK 17**
3. **Cassandra** (on docker)
4. **Hadoop** (Only for \*\*windows as it needs to be present for pySpark to run)

Backend Setup

1. If you are not using Python 3.11 you can create a virtual environment with Python3.11 as follows
   `python3.11 -m venv venv`
2. Then use the Python env created and then `pip install -r requirements.txt`
3. Once the libraries are installed, go to `CSE512-iot-data-managment/kafka_2.13-3.9.0/`.
4. Run the following commands on **SEPARATE TERMINAL WINDOWS**.

   > `bin/zookeeper-server-start.sh config/zookeeper.properties`

   > `bin/kafka-server-start.sh config/server.properties` (Make sure to start this script only after the first script starts)

5. Make sure Cassandra is already running on docker. This can be done by `docker pull cassandra` and starting the container.
6. Then go back to the project root folder in a **NEW TERMINAL WINDOW** (As the other two scripts will be running). Then navigate into `CSE512-iot-data-managment/kafka_stream_processing/` folder and run the `start_kafka.py script`:

   > `python start_kafka.py` (This will start streaming the data through kafka and push it to Cassandra)

7. Now go to a **NEW TERMINAL WINDOW** and navigate to `CSE512-iot-data-managment/backend/` folder and start the `main.py` script using the following command:

> `uvicorn main:app --reload`

This concludes the Backend. The backend will run on `http://localhost:8000/`. The endpoint are:

> GET: `/get_metrics`

> GET: `/get_alerts`

> GET: `/get_severity_counts`

> POST: `/get_query_plan`

To run the Dashboard:

2. `cd CSE512-iot-data-managment/frontend/iot-dashboard`

3. Install node:

   On Mac:

   > `brew install node`

   On Linux:

   > `sudo apt update`

   > `sudo apt install nodejs npm`

   > `npm install`

4. Check if node is installed:

   `node -v`

5. run `npm start` and the app will run on `http://localhost:3000/`

# About the Project

It is a dashboard for providing data insights about IoT-enabled cars, with the functionality of executing queries with the most efficient query plan.

![Screenshot 2024-11-30 at 12 43 56 PM](https://github.com/user-attachments/assets/90eeb454-ffee-4074-9064-edea7c449b3f)

**Filter by Category:**

![Screenshot 2024-11-30 at 12 44 49 PM](https://github.com/user-attachments/assets/0fa1363c-6cbd-49f5-82b6-a42a4a3ce18b)

**Filter by Car Model:**

![Screenshot 2024-11-30 at 12 45 09 PM](https://github.com/user-attachments/assets/35ec08a7-39aa-4f60-8503-59b4cbfd0301)

**Filter by Sensor**

![Screenshot 2024-11-30 at 1 04 47 PM](https://github.com/user-attachments/assets/5c4fa65f-f5f6-4219-a35c-5a05dfbbeb69)

**AI Summary:**

![Screenshot 2024-11-30 at 1 01 10 PM](https://github.com/user-attachments/assets/19dd5238-a0ab-47a7-be5d-868984026087)

**Query Tool**

<img width="1512" alt="Screenshot 2024-12-02 at 7 31 10 PM" src="https://github.com/user-attachments/assets/4a40c677-8a76-4439-9862-0300ca38ffd3">
