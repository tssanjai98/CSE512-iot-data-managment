from fastapi import FastAPI,Request
from pyspark.sql import SparkSession
from fastapi.responses import JSONResponse
from pyspark.sql.functions import col, when, count, explode
from queryPlanning import EnhancedCassandraQueryOptimizer,CassandraQueryVisualizer
from queryPlanning2 import StreamOptimizer
import json
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

@app.get("/get_severity_counts")
async def get_severity_counts():
    try:
        exploded_df = df.withColumn("metrics", explode(col("metrics")))

        severity_counts_df = exploded_df.groupBy("metrics.sensor_id") \
            .agg(
                count(when(col("metrics.severity") == "Warning", 1)).alias("warning_count"),
                count(when(col("metrics.severity") == "Critical", 1)).alias("critical_count"),
                count(when(col("metrics.severity") == "None", 1)).alias("normal_count")
            )

        result_df = severity_counts_df.toPandas()

        severity_counts = result_df.to_dict(orient="records")

        return JSONResponse(content={"status": "success", "data": severity_counts})

    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@app.post("/get_query_plan/")
# async def receive_any_body(body):
async def receive_any_data(request: Request):
    content_type = request.headers.get("Content-Type")
    body = json.loads(await request.body())
    print(body)
    optimizer = EnhancedCassandraQueryOptimizer(["localhost"])
    query = body['query']
    optimizer1 = StreamOptimizer()
    optimizer1.generate_plans(query)
    # print("Generated Query Plans:")
    # for plan in optimizer1.plans:
    #     print(plan.graph_code)


    try:
        analysis = optimizer.analyze_query(query)
        execPlans=[
            {
                "id":1,
                "graph":analysis['mermaid_diagram']
            }
        ]
        for idx,plan in enumerate(optimizer1.plans):
            execPlans.append(
                    {
                "id":idx+2,
                "graph":plan.graph_code
            }
            )

        #     print("Generated Query Plans:")
#     for plan in optimizer.plans:
#         print(plan)

    finally:
        optimizer.close()
    return {
        "searchResult": analysis['query_result'],
        "executionPlans":execPlans,
        "selectedPlan":1
    }
    # return {
    #     "content_type": content_type,
    #     "body": json.loads(body)
    # }