from fastapi import FastAPI
from pyspark.sql import SparkSession
from fastapi.responses import JSONResponse

app = FastAPI()

spark = SparkSession.builder \
    .appName("IoTMetrics") \
    .config("spark.cassandra.connection.host", "127.0.0.1") \
     .config("spark.cassandra.connection.host", "127.0.0.1") \
    .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.12:3.0.0") \
    .getOrCreate()

df = spark.read.format("org.apache.spark.sql.cassandra") \
    .options(table="realtime_metrics", keyspace="iot_data_management") \
    .load()

alerts_df = spark.read.format("org.apache.spark.sql.cassandra") \
    .options(table="alerts", keyspace="iot_data_management") \
    .load()

@app.get("/get_metrics")
async def get_metrics():
    try:
        limited_df = df.limit(500)
        
        pandas_df = limited_df.toPandas()

        for column in pandas_df.select_dtypes(include=["datetime"]).columns:
            pandas_df[column] = pandas_df[column].dt.strftime('%Y-%m-%dT%H:%M:%S')

        metrics_data = pandas_df.to_dict(orient='records')
        for entry in metrics_data:
            for metric in entry['metrics']:
                metric['value'] = float(metric['value'])
                metric['alert'] = metric['alert'] == 'True'
        return JSONResponse(content={"status": "success", "data": metrics_data})

    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
    
@app.get("/get_alerts")
async def get_alerts():
    try:
        limited_alerts_df = alerts_df.limit(500)
        
        pandas_alerts_df = limited_alerts_df.toPandas()

        for column in pandas_alerts_df.select_dtypes(include=["datetime"]).columns:
            pandas_alerts_df[column] = pandas_alerts_df[column].dt.strftime('%Y-%m-%dT%H:%M:%S')

        alerts_data = pandas_alerts_df.to_dict(orient='records')

        return JSONResponse(content={"status": "success", "data": alerts_data})

    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)