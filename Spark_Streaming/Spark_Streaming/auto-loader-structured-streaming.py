# Databricks notebook source
# File Path to look for
upload_path = '/FileStore/shared_uploads/joseph.thomas@simelabs.com/data'

checkpoint_path = '/tmp/delta/stocks_data/_checkpoints'
write_path = '/tmp/delta/stocks_data'

dbutils.fs.mkdirs(upload_path)
dbutils.fs.mkdirs(checkpoint_path)
dbutils.fs.mkdirs(write_path)

# COMMAND ----------

import os
from datetime import datetime
from  pyspark.sql.functions import input_file_name
from pyspark.sql.types import ArrayType, IntegerType, StructType, StructField, StringType

def get_date(value):
  f_name, _ = os.path.splitext(os.path.basename(value))
  col_date = datetime. strptime(f_name[-6:], '%d%m%y').date()
  return str(col_date)

print(get_date('file:/content/stocks/EQ041021.CSV'))

get_date_udf_func = udf(get_date,StringType()) 
# spark.udf.register("get_date_udf_func", get_date,StringType())

# COMMAND ----------

# Loading schema to use in sparkstreaming
df2 = spark.read.option("header",True).csv(upload_path)
cust_schema = df2.schema

# COMMAND ----------

# Custom load to mysql db, python function to load data

import pymysql
from sqlalchemy import create_engine
import mysql.connector

server_name = "jdbc:mysql://52.66.144.164:3306"
database_name = "sparkTest"
jdbcurl = server_name + "/" + database_name
table_name = "stockTable"
db_properties = {"user":"sa_remote", "password":""}

engine = create_engine('mysql+pymysql://asdasd:dasdas@52.66.144.164:3306/sparkTest', echo=False)
# dbConnection    = engine.connect()

def write_to_mysql(temp_df, epoch_id):
    jdbcurl = 'jdbc:mysql://52.66.144.164:3306/sparkTest'
    dfwriter = temp_df.write.mode("append")
    #dfwriter.jdbc(url=jdbcurl, table=table_name, properties=db_properties) # if this is not working use below
    temp_df.write.jdbc(url=jdbcurl, table=table_name, properties=db_properties, mode="append")
    pass

def pandas_write_to_mysql(temp_df, epoch_id):
    pd_df = temp_df.toPandas()
    pd_df.to_sql(name=table_name, con=engine, if_exists='append', index=False)

# COMMAND ----------

# jdbcHostname = "jdbc:mysql://52.66.144.164"
# jdbcDatabase = "sparkTest"
# jdbcPort = 3306

# jdbcUrl = "jdbc:mysql://{0}:{1}/{2}".format(jdbcHostname, jdbcPort, jdbcDatabase)
# connectionProperties = {
#   "user" : "",
#   "password" : "",
#   "driver" : "com.mysql.cj.jdbc.Driver"
# }

# pushdown_query = "(select * from stockTable) test"
# df = spark.read.jdbc(url=jdbcurl, table=pushdown_query, properties=connectionProperties)
# display(df)

# COMMAND ----------

# %sh nc -vz 52.66.144.164 3306

# COMMAND ----------

checkpoint_path = '/tmp/delta/stocks_data/_checkpoints'
write_path = '/tmp/delta/stocks_data'

# Set up the stream to begin reading incoming files from the
# upload_path location.
# df = spark.readStream.format('cloudFiles') \
#   .option('cloudFiles.format', 'csv') \
#   .option('header', 'true') \
#   .schema(cust_schema) \
#   .load(upload_path)

df = (
  spark
    .readStream
    .option("maxFileAge", '1s')\
    .schema(cust_schema)               # Set the schema of the JSON data
    .format("csv")
    .load("/FileStore/shared_uploads/joseph.thomas@simelabs.com/data/*")
    .withColumn("closing_date", get_date_udf_func(input_file_name()))
)

# df = (
#   spark
#     .readStream                       
#     .schema(cust_schema)               # Set the schema of the JSON data
#     #.option("maxFilesPerTrigger", 1)  # Treat a sequence of files as a stream by picking one file at a time
#     .csv(upload_path)
# )

# Start the stream.
# Use the checkpoint_path location to keep a record of all files that
# have already been uploaded to the upload_path location.
# For those that have been uploaded since the last check,
# write the newly-uploaded files' data to the write_path location.

# --- output > delta
# df.writeStream.format('delta') \
#   .option('checkpointLocation', checkpoint_path) \
#   .start(write_path)

# --- output > To Table inside databricks data section
# df.writeStream \
#     .option("checkpointLocation", checkpoint_path) \
#     .format("parquet") \
#     .toTable("stockTable")

# --- output > Output as parquet files..
df.writeStream.format('parquet') \
  .option('checkpointLocation', checkpoint_path) \
  .trigger(once=True) \
  .option('path', write_path) \
  .start()

# df.writeStream.option("checkpointLocation", checkpoint_path).toTable("stockTable")

# --- output > Custom output function on output of batch
# df.writeStream.option('checkpointLocation',checkpoint_path)\
# .outputMode("append")\
# .foreachBatch(pandas_write_to_mysql)\
# .start()

# COMMAND ----------

# MAGIC %md [triggers]https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#triggers

# COMMAND ----------

# Trigger with processingTime='10 minute' will proccess current batch and next process will start after 10 min
# maxFilesPerTrigger: maximum number of new files to be considered in every trigger

spark.readStream\
.schema(cust_schema)\
    .option("maxFilesPerTrigger", 1)\
    .csv(upload_path) \
    .writeStream.format('parquet') \
    .trigger(processingTime='10 minute') \
    .option('checkpointLocation', checkpoint_path) \
    .option('path', write_path) \
    .start()

# COMMAND ----------

# Trigger with once=True will proccess once and exit streaming..while restarting it will start with new file if available
# maxFilesPerTrigger: maximum number of new files to be considered in every trigger

spark.readStream\
.schema(cust_schema)\
    .option("maxFilesPerTrigger", 1)\
    .csv(upload_path) \
    .writeStream.format('parquet') \
    .trigger(once=True) \
    .option('checkpointLocation', checkpoint_path) \
    .option('path', write_path) \
    .start()

# COMMAND ----------

# ------ maxFileAge Test ------------

# Trigger with processingTime='10 minute' will proccess current batch and next process will start after 10 min
# maxFilesPerTrigger: maximum number of new files to be considered in every trigger

spark.readStream\
.schema(cust_schema)\
    .option("latestFirst", "true")\
    .option("maxFilesPerTrigger", 1)\
    .csv(upload_path) \
    .withColumn("closing_date", get_date_udf_func(input_file_name()))\
    .writeStream.format('parquet') \
    .trigger(processingTime='2 minute') \
    .option('checkpointLocation', checkpoint_path) \
    .option('path', write_path) \
    .start()

# COMMAND ----------

# ------ maxFileAge Test ------------

# Trigger with processingTime='10 minute' will proccess current batch and next process will start after 10 min
# maxFilesPerTrigger: maximum number of new files to be considered in every trigger

spark.readStream\
.option("latestFirst", "true")\
.option("maxFilesPerTrigger", 1)\
.schema(cust_schema)\
    .csv(upload_path) \
    .withColumn("closing_date", get_date_udf_func(input_file_name()))\
    .writeStream.format('parquet') \
    .trigger(once=True) \
    .option('checkpointLocation', checkpoint_path) \
    .option('path', write_path) \
    .start()

# COMMAND ----------

# MAGIC %sql
# MAGIC select count(*) from stockTable;

# COMMAND ----------

# MAGIC %sql
# MAGIC 
# MAGIC show create table stockTable;

# COMMAND ----------

# MAGIC %sql
# MAGIC drop table stockTable;

# COMMAND ----------

# df_temp = spark.read.format('delta').load(write_path)

# display(df_temp)

# COMMAND ----------

# df_temp = spark.read.format('delta').load(write_path)

# df_temp.count()

# COMMAND ----------

# MAGIC %fs ls /tmp/delta/stocks_data

# COMMAND ----------

df_temp = spark.read.option('header', 'true').format('parquet').load(write_path)
c = df_temp.groupBy('closing_date')
display(c.count())

# COMMAND ----------

# MAGIC %fs ls /FileStore/shared_uploads/joseph.thomas@simelabs.com/data/

# COMMAND ----------

# MAGIC %fs ls /FileStore/shared_uploads/joseph.thomas@simelabs.com/

# COMMAND ----------

# Clean up
dbutils.fs.rm(write_path, True)
dbutils.fs.rm(upload_path, True)

# COMMAND ----------

dbutils.fs.rm("/FileStore/shared_uploads/joseph.thomas@simelabs.com/stock_merge.csv", True)