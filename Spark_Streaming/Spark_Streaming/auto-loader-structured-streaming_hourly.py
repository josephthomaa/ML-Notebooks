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

# MAGIC %md [triggers]https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#triggers

# COMMAND ----------

# Trigger with processingTime='1 hour' will proccess current batch and next process will start after 1 hour
# maxFilesPerTrigger: maximum number of new files to be considered in every trigger

query = spark.readStream\
.schema(cust_schema)\
    .option("latestFirst", "true")\
    .option("maxFilesPerTrigger", 1)\
    .csv(upload_path) \
    .withColumn("closing_date", get_date_udf_func(input_file_name()))\
    .writeStream.format('parquet') \
    .trigger(processingTime='1 minutes') \
    .option('checkpointLocation', checkpoint_path) \
    .option('path', write_path) \
    .start()

# COMMAND ----------

print(query.status)

# COMMAND ----------

# ------ maxFileAge Test ------------

# Trigger with processingTime='10 minute' will proccess current batch and next process will start after 10 min
# maxFilesPerTrigger: maximum number of new files to be considered in every trigger

# spark.readStream\
# .option("maxFileAge", "1h")\
# .option("maxFilesPerTrigger", 1)\
# .option("includeExistingFiles ", "false")\
# .schema(cust_schema)\
#     .csv(upload_path) \
#     .withColumn("closing_date", get_date_udf_func(input_file_name()))\
#     .writeStream.format('parquet') \
#     .trigger(once=True) \
#     .option('checkpointLocation', checkpoint_path) \
#     .option('path', write_path) \
#     .start()

# COMMAND ----------

# Clean up
dbutils.fs.rm(write_path, True)
# dbutils.fs.rm(upload_path, True)