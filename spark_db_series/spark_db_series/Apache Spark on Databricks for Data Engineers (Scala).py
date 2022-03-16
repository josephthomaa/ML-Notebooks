# Databricks notebook source
# MAGIC %md 
# MAGIC # Apache Spark on Databricks for Data Engineers
# MAGIC 
# MAGIC ** Welcome to Databricks! **
# MAGIC 
# MAGIC This notebook intended to give a high level tour of some of the features that are available to users using Apache Spark and Databricks and to be the final step in your process to learn more about how to best use Apache Spark and Databricks together. We'll be walking you through several data sources, creating UDFs, and manipulating data all from the perspective of a data engineer. While this is not by any means exhaustive, by the end of this notebook you should be familiar with a lot of the topics and subjects that are available in Databricks. We'll be reading in some data from several sources including CSVs and raw text files. We'll then be warehousing that data in Redshift and in parquet format. 
# MAGIC 
# MAGIC First, it's worth defining Databricks. Databricks is a managed platform for running Apache Spark - that means that you do not have to learn complex cluster management concepts nor perform tedious maintenance tasks to take advantage of Apache Spark. Databricks also provides a host of features to help its users be more productive with Spark. It’s a point and click platform for those that prefer a user interface like data scientists or data analysts. This UI is accompanied by a sophisticated API for those that want to automate jobs and aspects of their data workloads. To meet the needs of enterprises, Databricks also includes features such as role-based access control and other intelligent optimizations that not only improve usability for users but also reduce costs and complexity for administrators.
# MAGIC 
# MAGIC It's worth stressing that many tools don't make it easy to prototype easily, then scale up to production workloads easily without heavy work by the operations teams. Databricks greatly simplifies these challenges by making it easy to prototype, schedule, and scale elastically all in the same environment.
# MAGIC 
# MAGIC 
# MAGIC ** The Gentle Introduction Series **
# MAGIC 
# MAGIC This notebook is a part of a series of notebooks aimed to get you up to speed with the basics of Spark quickly. This notebook is best suited for those that have very little or no experience with Apache Spark. The series also serves as a strong review for those that have some experience with Spark but aren't as familiar with some of the more sophisticated tools like UDF creation and machine learning pipelines. The other notebooks in this series are:
# MAGIC 
# MAGIC - [A Gentle Introduction to Apache Spark on Databricks](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/346304/2168141618055043/484361/latest.html)
# MAGIC - [Apache Spark on Databricks for Data Scientists](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/346304/2168141618055194/484361/latest.html)
# MAGIC - [Apache Spark on Databricks for Data Engineers](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/346304/2168141618055109/484361/latest.html)
# MAGIC 
# MAGIC ## Tutorial Overview
# MAGIC 
# MAGIC In this tutorial, we're going to play around with data source API in Apache Spark. This is going to require us to read and write using a variety of different data sources. We'll hop between different languages and different APIs to show you how to get the most out of Spark as a data engineer.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Reading in our initial dataset
# MAGIC 
# MAGIC For this first section, we're going to be working with a set of Apache log files. These log files are made available by Databricks via the `databricks-datasets` directory. This is made available right at the root directory. We'll get to reading in the data in a minute but accessing this data is a great example of what we can do inside of Databricks. We're going to use some functionality and data that Databricks provides. Firstly, we're going to use the Databricks Filesystem to list all of the [Databricks datasets](https://docs.cloud.databricks.com/docs/latest/databricks_guide/index.html#03%20Accessing%20Data/5%20Public%20Example%20Data%20Sets/1%20DBFS%20Hosted%20Datasets.html) that are available for you to use.

# COMMAND ----------

# MAGIC %fs ls dbfs:/databricks-datasets/

# COMMAND ----------

display(dbutils.fs.ls('/databricks-datasets/sample_logs/'))

# COMMAND ----------

# f = open('dbfs:/databricks-datasets/README.md', 'r')
# print(f.read())

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE default.people10m OPTIONS (PATH 'dbfs:/databricks-datasets/learning-spark-v2/people/people-10m.delta')

# COMMAND ----------

# MAGIC %sql
# MAGIC 
# MAGIC select * from people10m limit 5;

# COMMAND ----------

# MAGIC %md Inside of that folder you'll see the sample logs folder.

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC log_files = "/databricks-datasets/sample_logs"

# COMMAND ----------

dbutils.fs.head("/databricks-datasets/sample_logs/part-00000")[:200]

# COMMAND ----------

# MAGIC %md 
# MAGIC You'll see that we have a variety of other example datasets that you can access and play with. While you can simply list and checkout the datasets via the command line or via `%fs ls` it's often easier to just look at [the documentation.](https://docs.cloud.databricks.com/docs/latest/databricks_guide/index.html#03%20Accessing%20Data/5%20Public%20Example%20Data%20Sets/1%20DBFS%20Hosted%20Datasets.html)
# MAGIC 
# MAGIC Now that we've touched on Databricks datasets, let's go ahead and get started with the actual log data that we'll be using. This brings us to a unique advantage of Databricks and how easy it is to use multiple languages in the same notebook. For example, a colleague at Databricks had already written an Apache log parser that works quite well in python, rather than writing my own, I'm able to reuse that code very easily by just prefacing my cell with `%python` and copying and pasting the code. Currently this notebook has Scala cells by default as we'll see below.

# COMMAND ----------

# MAGIC %python 
# MAGIC 
# MAGIC import re
# MAGIC from pyspark.sql import Row
# MAGIC from pyspark.sql.types import *
# MAGIC APACHE_ACCESS_LOG_PATTERN = '^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+)'
# MAGIC 
# MAGIC # Returns a dictionary containing the parts of the Apache Access Log.
# MAGIC def parse_apache_log_line(logline):
# MAGIC     print(logline)
# MAGIC     match = re.search(APACHE_ACCESS_LOG_PATTERN, logline)
# MAGIC     if match is None:
# MAGIC         # Optionally, you can change this to just ignore if each line of data is not critical.
# MAGIC         # For this example, we want to ensure that the format is consistent.
# MAGIC         raise Exception("Invalid logline: %s" % logline)
# MAGIC     return Row(
# MAGIC         ipAddress    = match.group(1),
# MAGIC         clientIdentd = match.group(2),
# MAGIC         userId       = match.group(3),
# MAGIC         dateTime     = match.group(4),
# MAGIC         method       = match.group(5),
# MAGIC         endpoint     = match.group(6),
# MAGIC         protocol     = match.group(7),
# MAGIC         responseCode = int(match.group(8)),
# MAGIC         contentSize  = str(match.group(9)))

# COMMAND ----------

str

# COMMAND ----------

# MAGIC %md 
# MAGIC Now that I've defined that function, I can use it to convert my unstructured rows of data into something that is a lot more structured (like a table). I'll do that by reading in the log file as an RDD. RDD's (Resilient Distributed Datasets) are the lowest level abstraction made available to users in Databricks. In general, the best tools for users of Apache Spark are DataFrames and Datasets as they provide significant optimizations for many types of operations. However it's worth introducing the concept of an RDD. As the name suggests, these are distributed datasets that are sitting at some location and specify a logical set of steps in order to compute some end result.
# MAGIC 
# MAGIC As we had covered in the first notebook in this series, Spark is lazily evaluated. That means that even though we've specified that we want to read in a piece of data it won't be read in until we perform an action. If you're forgetting these details, please review [the first notebook in this series](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/346304/2168141618055043/484361/latest.html).

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC log_files = "/databricks-datasets/sample_logs"
# MAGIC raw_log_files = sc.textFile(log_files)

# COMMAND ----------

# raw_log_files.take(5)
# Filter all of the lines within the DataFrame
textFile = spark.read.text("/databricks-datasets/sample_logs")
linesWithuser2 = textFile.filter(textFile.value.contains("user2"))
linesWithuser2.take(5)

# COMMAND ----------

# MAGIC %md So now that we've specfied what data we would like to read in, let's go and ahead and count the number of rows. Right now we are actually reading in the data however it is not stored in memory. It's just read in, and then discarded. This is because we're calling an **action** which also came up in the first notebook in this series.

# COMMAND ----------

# MAGIC %python 
# MAGIC textFile.count()

# COMMAND ----------

# MAGIC %md This shows us that we've got a total of 100,000 records. But we've still got to parse them. To do that we'll use a map function which will apply that function to each record on the dataset. Now naturally this can happen in a distributed fashion across the cluster. This cluster is made up of executors that will execute computation when they are asked to do so by the primary master node or driver.
# MAGIC 
# MAGIC The diagram below shows an example Spark cluster, basically there exists a Driver node that communicates with executor nodes. Each of these executor nodes have slots which are logically like execution cores. 
# MAGIC 
# MAGIC ![spark-architecture](http://training.databricks.com/databricks_guide/gentle_introduction/videoss_logo.png)
# MAGIC 
# MAGIC The Driver sends Tasks to the empty slots on the Executors when work has to be done:
# MAGIC 
# MAGIC ![spark-architecture](http://training.databricks.com/databricks_guide/gentle_introduction/spark_cluster_tasks.png)
# MAGIC 
# MAGIC Note: *In the case of the Community Edition there is no Worker, and the Master, not shown in the figure, executes the entire code.*
# MAGIC 
# MAGIC ![spark-architecture](http://training.databricks.com/databricks_guide/gentle_introduction/notebook_microcluster.png)
# MAGIC 
# MAGIC You can view the details of your Apache Spark application in the Apache Spark web UI.  The web UI is accessible in Databricks by going to "Clusters" and then clicking on the "View Spark UI" link for your cluster, it is also available by clicking at the top left of this notebook where you would select the cluster to attach this notebook to. In this option will be a link to the Apache Spark Web UI.
# MAGIC 
# MAGIC At a high level, every Apache Spark application consists of a driver program that launches various parallel operations on executor Java Virtual Machines (JVMs) running either in a cluster or locally on the same machine. In Databricks, the notebook interface is the driver program.  This driver program contains the main loop for the program and creates distributed datasets on the cluster, then applies operations (transformations & actions) to those datasets.
# MAGIC 
# MAGIC Driver programs access Apache Spark through a `SparkSession` object regardless of deployment location.
# MAGIC 
# MAGIC Let's go ahead and perform a transformation by parsing the log files.

# COMMAND ----------

raw_log_files

# COMMAND ----------

# MAGIC %python
# MAGIC parsed_log_files = raw_log_files.map(parse_apache_log_line)

# COMMAND ----------

# MAGIC %md
# MAGIC Please note again that no computation has been started, we've only created a logical execution plan that has not been realized yet. In Apache Spark terminology we're specifying a **transformation**. By specifying transformations and not performing them right away, this allows Spark to do a lot of optimizations under the hood most relevantly, pipelining. Pipelining means that Spark will perform as much computation as it can in memory and in one stage as opposed to spilling to disk after each step.
# MAGIC 
# MAGIC Now that we've set up the transformation for parsing this raw text file, we want to make it available in a more structured format. We'll do this by creating a DataFrame (using `toDF()`) and then a table (using `registerTempTable()`). This will give us the added advantage of working with the same dataset in multiple languages.

# COMMAND ----------

# MAGIC %python
# MAGIC parsed_log_files.toDF().registerTempTable("log_data")

# COMMAND ----------

# MAGIC %md `RegisterTempTable` saves the data on the local cluster that we're working with. You won't find it in the `tables` button list on the left because it's not globally registered across all clusters, only this specific one. That means that if we restart, our table will have to be re-registered. Other users and notebooks that attach to this cluster however can access this table. Now let's run some quick SQL to see how our parsing performed. This is an **action**, which specifies that Spark needs to perform some computation in order to return a result to the user.

# COMMAND ----------

# MAGIC %sql select * from log_data

# COMMAND ----------

# MAGIC %md We're also able to convert it into a Scala DataFrame by just performing a select all.
# MAGIC 
# MAGIC Under the hood, Apache Spark DataFrames and SparkSQL are effectively the same. They operate with the same optimizer and have the same general functions that are made available to them.

# COMMAND ----------

# MAGIC %scala
# MAGIC val logData = sqlContext.table("log_data")

# COMMAND ----------

# MAGIC %scala
# MAGIC logData.printSchema()

# COMMAND ----------

# MAGIC %md However one thing you've likely noticed is that that DataFrame creation process is still lazy. We have a schema (that was defined during our parsing process) but we haven't kicked off any tasks yet to work with that data.
# MAGIC 
# MAGIC This is actually one of the differences between SparkSQL (using `%sql` in Databricks) and the regular DataFrames API. SparkSQL is a bit more eager with its computations so calls to cache data or select it actually end up being eagerly computed as opposed to lazy. However when we run the code via `sqlContext.sql` it's lazily evaluated. We introduced these concepts in [the gentle introduction to Apache Spark and Databricks notebook](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/346304/2168141618055043/484361/latest.html) and it's worth reviewing if this does not seem familiar.
# MAGIC 
# MAGIC Now before moving forward, let's display a bit of the data. Often times you'll want to see a bit of the data that you're working with, we can do this very easily using the `display` function that is available in all languages on a DataFrame or Dataset.

# COMMAND ----------

# MAGIC %scala
# MAGIC display(logData)

# COMMAND ----------

# MAGIC %md 
# MAGIC As mentioned DataFrames and SparkSQL take advantage of the same optimizations and while we can specify our transformations by using and importing [SparkSQL functions](http://spark.apache.org/docs/latest/api/scala/index.html#org.apache.spark.sql.functions$), I find it easier just to write the SQL to do my transformations.

# COMMAND ----------

# MAGIC %md 
# MAGIC However, there's one issue here. Our datetime is not in a format that we can parse very easily. Let's go ahead and try to cast it to a timestamp and you'll see what I mean.

# COMMAND ----------

# MAGIC %sql SELECT cast("21/Jun/2014:10:00:00 -0700" as timestamp)

# COMMAND ----------

# MAGIC %md 
# MAGIC 
# MAGIC What we get back is `null` meaning that the operation did not succeed. To convert this date format we're going to have to jump through a couple of hoops, namely we're going to have to handle the fact that [Java Simple Date Format](http://docs.oracle.com/javase/tutorial/i18n/format/simpleDateFormat.html) (which is what is used in the date time function) does not effectively handle the timezone as specified in our date formatter. Luckily this gives us an awesome way of demonstrating the creation of a UDF!
# MAGIC 
# MAGIC Creating UDFs in Spark and Scala is very simple, you just define a scala function then register it as a UDF. Now this function is a bit involved but the short of it is that we need to convert our string into a timestamp. More specifically we're going to want to define a function that takes in a string, splits on the space character. Converts the hour offset to a form that we can offset our date by and adds it to our newly created datetime.

# COMMAND ----------

# MAGIC %scala
# MAGIC def parseDate(rawDate:String):Long = {
# MAGIC   val dtParser = new java.text.SimpleDateFormat("dd/MMM/yyyy:hh:mm:ss")
# MAGIC   val splitted = rawDate.split(" ")
# MAGIC   val futureDt = splitted(0)
# MAGIC   // naturally building the offset is nice and annoying
# MAGIC   // we've got to be sure to extract minutes and 
# MAGIC   // only multiply them by 60 as opposed to the 60^2
# MAGIC   // required for hours
# MAGIC   val offset = splitted(1).asInstanceOf[String].toLong
# MAGIC   val hourOffset = (offset.toInt / 100) 
# MAGIC   val minuteOffset = (offset - hourOffset * 100).toInt
# MAGIC   val totalOffset = hourOffset * 60 * 60 + minuteOffset * 60
# MAGIC   // now the time that we get here is in milliseconds
# MAGIC   // so we've got to divide by 1000 then add our offset.
# MAGIC   // SparkSQL also works at the second level when casting long types to
# MAGIC   // timestamp Types, so we've got to ensure that we are using seconds
# MAGIC   (dtParser.parse(futureDt).getTime() / 1000) + totalOffset
# MAGIC }
# MAGIC 
# MAGIC val example = "21/Jun/2014:10:00:00 -0730"
# MAGIC parseDate(example)

# COMMAND ----------

from datetime import datetime

def new_parse_date(rawDate):
  rawDate = rawDate[:-6]
  datetime_object = datetime.strptime(rawDate, '%d/%b/%Y:%H:%M:%S')
  return datetime_object

example = "21/Jun/2014:10:00:00 -0730"
new_parse_date(example)

# COMMAND ----------

# MAGIC %md Now there are two different ways to register a UDF and we'll do both of them just to be clear about how to do it. The first is by using the `udf` function from `org.apache.spark.sql.functions`. This will allow you to use it on DataFrame columns.

# COMMAND ----------

# MAGIC %scala
# MAGIC import org.apache.spark.sql.functions.udf
# MAGIC val parseDateUdf = udf(parseDate(_:String):Long)

# COMMAND ----------

# display(logData.select(parseDateUdf($"dateTime")))

# COMMAND ----------

# MAGIC %md The other way is to register it with the `sqlContext`. This will allow you to use it inside of plain SQL as opposed to operating on a DataFrame column.

# COMMAND ----------

from pyspark.sql.types import StringType
spark.udf.register("new_parse_date_udf_func", new_parse_date,StringType())

# COMMAND ----------

cleanLogFiles = sqlContext.sql("""
SELECT 
  clientIdentd, int(contentSize) as contentSize, cast(parseDate(dateTime) as timestamp) as dt, 
  endpoint, ipAddress, method, protocol, int(responseCode) as responseCode, userId 
FROM log_data
""")

# COMMAND ----------

# MAGIC %md Another way of performing the above computation is by using the `selectExpr` method with allows you to use SQL expressions on a DataFrame.

# COMMAND ----------

# %scala
# val cleanLogFiles = logData.selectExpr("clientIdentd"," int(contentSize) as contentSize"," cast(parseDate(dateTime) as timestamp) as dt","endpoint"," ipAddress"," method"," protocol"," int(responseCode) as responseCode"," userId")

# COMMAND ----------

display(cleanLogFiles)

# COMMAND ----------

# MAGIC %md What's great about this is now we've got this UDF and we can reuse it in a variety of different languages (if we register it with the `sqlContext`). Now that we've created the plan for how to create this DataFrame - let's go ahead and run the `explain` method. This will give us the entire logical (and physical) instructions for Apache Spark to recalculate that DataFrame. Notice that this goes down to the raw RDD (and text file!) that we created in python at the top of the notebook!

# COMMAND ----------

cleanLogFiles.explain()

# COMMAND ----------

# MAGIC %md 
# MAGIC Now we've covered transitioning through a couple of different of different languages and reading in unstructured data. Now let's move onto reading in some data from structured sources.
# MAGIC 
# MAGIC ## Reading in structured data
# MAGIC 
# MAGIC Apache Spark's goal is to unify all different kinds of data and data sources.
# MAGIC 
# MAGIC ![img](http://training.databricks.com/databricks_guide/gentle_introduction/spark_goal.png)
# MAGIC 
# MAGIC As a data engineer, many times you're not going to be parsing raw data, you may also be reading in more structured data formats. Apache Spark is the best tool for the job because it connects to so many different data sources - be those text files or databases.
# MAGIC 
# MAGIC For example, we'll now read in another csv from databricks-datasets, this one being the infamous diamonds dataset from R and ggplot.

# COMMAND ----------

# MAGIC %scala
# MAGIC sqlContext.read.format("csv")
# MAGIC   .option("inferSchema", "true")
# MAGIC   .load("dbfs:/databricks-datasets/Rdatasets/data-001/csv/ggplot2/diamonds.csv")

# COMMAND ----------

diamonds = sqlContext.read.format("csv").option("header", "true").option("inferSchema","true").load("dbfs:/databricks-datasets/Rdatasets/data-001/csv/ggplot2/diamonds.csv").withColumnRenamed("table", "contentSize") 
# I've renamed this column in order to 
# simplfy the join with our other table further down in the notebook.

# COMMAND ----------

display(diamonds)

# COMMAND ----------

# MAGIC %md For the sake of this example, we will join the above data with our first DataFrame in order to illustrate how you go about joining datasets. When we perform this join we will be generating a new DataFrame. In fact, you can think of it just as another transformation.

# COMMAND ----------

# MAGIC %md Let's go ahead and merge this data with our diamonds dataset. Now this is a nonsense join however it provides a nice way to simulate what it's like to run a more sophisticated pipeline.

# COMMAND ----------

# MAGIC %scala
# MAGIC val newData = diamonds.join(cleanLogFiles, diamonds("contentSize") === cleanLogFiles("contentSize"), "inner")
# MAGIC // specifying an inner join
# MAGIC val archiveReady = newData.selectExpr("x", "y", "z", "method", "userId", "year(dt) as yr", "month(dt) as mnt")
# MAGIC // selecting only some of the columns.

# COMMAND ----------

# MAGIC %md 
# MAGIC 
# MAGIC Thus far we've done a nice series of transformations - we've written a UDF to parse some pesky date formats and now we're going to complete the pipeline by pushing our new DataFrame into Redshift and into S3. In addition to being able to read from a lot of data sources. Apache Spark can also write to those as well! We recommend using Apache Parquet as it is an efficient column store for structured data however many customers use a Data Warehousing solution like Redshift for handling a high numbers of concurrent users.
# MAGIC 
# MAGIC We've created our DataFame called `archiveReady`. Right now, `archiveReady` is just a recipe, it tells Apache Spark how to generate it but we haven't stored anything in memory. Let's change that! In-memory storage is one of Apache Spark's significant benefits. It's not a panacea but if there's a dataset that we're going to do several things with, we can cache it in memory in order to efficiently access it repeatedly.

# COMMAND ----------

# MAGIC %md  However, this won't happen right away simply because Apache Spark is still lazily evaluated, meaning that we won't cache it until we've had to run that full table scan in the first place. Let's go ahead and call `count` twice. The first time will cache it, the second time will show us the speed up for accessing that data in memory. Before doing that let's check out the query plan.

# COMMAND ----------

# MAGIC %scala
# MAGIC archiveReady.explain

# COMMAND ----------

# MAGIC %md Once we see this query plan we'll see that it goes all the way back to our CSV as well as the original RDD that we created in python. This provides Apache Spark the opportunity to optimize but it also gives us great information about how we might be able to make our data workflow more efficient as well. Now let's count the data and start our caching (as well as executing that query plan).

# COMMAND ----------

# MAGIC %scala
# MAGIC archiveReady.cache()

# COMMAND ----------

# MAGIC %scala
# MAGIC archiveReady.count()

# COMMAND ----------

# MAGIC %scala
# MAGIC archiveReady.explain

# COMMAND ----------

# MAGIC %scala
# MAGIC archiveReady.count()

# COMMAND ----------

# MAGIC %md Now we can see that our query plan is entirely different, we do an in-memory table scan as opposed to going all the way back to our source data and in the process we're going to be getting a huge speed up.

# COMMAND ----------

# MAGIC %md 
# MAGIC 
# MAGIC ## Data Warehousing
# MAGIC 
# MAGIC Now let's get to data warehousing. Now often what you may need to do is use one set of AWS credentials to read in data and then use another set of API keys to write it out. What's nice about Databricks is that there is very fine grained controls over notebooks. For example, I've stored a set of my aws credentials inside of a notebook that only I have access to. I can run that notebook by specifying the `%run` command.
# MAGIC 
# MAGIC Now the reason that I'm running this is that I want to be able to use the Spark-Redshift connector in order to be able to write my data to Redshift. I want to access those credentials but don't want them to appear in a notebook available to others.

# COMMAND ----------

# MAGIC %run /Users/bill@databricks.com/credentials/redshift-scala

# COMMAND ----------

# MAGIC %md now one thing that you'll notice is that above it appears that I've not set the values correctly. However that's because I've used a little trick that I'll explain below to set them (and not have them appear in the REPL).

# COMMAND ----------

# MAGIC %scala
# MAGIC var value = "This is the old value"
# MAGIC 
# MAGIC def setValue():Unit = {
# MAGIC   value = "This is a secret value"
# MAGIC }

# COMMAND ----------

# MAGIC %md So now the value that we've defined above will be redefined by the `setValue` function above. We simply have to call that function and we'll be changing the value of value. You'll also see that that function has no output so it won't print anything to the console.

# COMMAND ----------

# MAGIC %scala
# MAGIC setValue()

# COMMAND ----------

# MAGIC %md Now that I've set up my redshift credentials (using the above printed out variables), I'm going to set up another. In another notebook, I've defined another function that, just as I did above, that mounts an s3 bucket as a Databricks file system. Here's that raw function that I've defined in that notebook.

# COMMAND ----------

# MAGIC %scala
# MAGIC def mountBucket(dstBucketName:String, dstMountName:String) {
# MAGIC   import java.lang.IllegalArgumentException
# MAGIC   val accessKey = "SOME KEY"
# MAGIC   val encodedSecretKey = "SOME SECRET".replace("/", "%2F")
# MAGIC   try {
# MAGIC     dbutils.fs.mount(s"s3a://$accessKey:$encodedSecretKey@$dstBucketName", dstMountName) 
# MAGIC     println("All done!")
# MAGIC   } catch {
# MAGIC     case e: java.rmi.RemoteException => {
# MAGIC       println("Directory is Already Mounted")
# MAGIC       dbutils.fs.unmount(dstMountName)
# MAGIC       mountBucket(dstBucketName, dstMountName)
# MAGIC     }
# MAGIC     case e: Exception => {
# MAGIC       println("There was some other error")
# MAGIC     }
# MAGIC   }
# MAGIC }

# COMMAND ----------

# MAGIC %md All I did was swap about the value of `accessKey` and `encodedSecretKey`. Now I'll just run the notebook that I had created and had replaced with my own credentials and I will have a mount created for my S3 bucket! All using secrets that only I have access to.

# COMMAND ----------

# MAGIC %run /Users/bill@databricks.com/credentials/mount-s3-bucket

# COMMAND ----------

# MAGIC %md Now I can list the contents of a "directory" inside of that bucket. This is the directory that I'll be writing to.

# COMMAND ----------

# MAGIC %scala
# MAGIC val dstBucketName = "databricks-bill"
# MAGIC val dstMountName = "/mnt/dst-bucket"
# MAGIC 
# MAGIC mountBucket(dstBucketName, dstMountName)

# COMMAND ----------

# MAGIC %md this will mount a given bucket under a certain mount name. This will allow us to treat S3 like a filesystem.

# COMMAND ----------

# MAGIC %md ### Data Warehousing Part 2: Writing the Actual Data
# MAGIC 
# MAGIC Alright! We've taken a bit of a detour to mount all of those buckets, but let's go ahead and review what where we were before and why we took that detour. We had a DataFrame of data that we were hoping to be able to put into our data warehouse. We wanted to store that data in two distinct locations. One set of data should be in Redshift for our analysts to be able to access and the other set of data should reside in Amazon S3. We had to prep some credentials in order to be able to use those services and showed how we can do that with the `%run` command to run other notebooks in our environment.
# MAGIC 
# MAGIC Now let's go ahead and write our data using Spark Redshift! This is actually going to be very simple and will seem very similar to reading in a CSV file. That's because as previously mentioned, Apache Spark has a variety of data source connectors that all use the same API format. A key difference is that Spark Redshift uses a temp directory (that is an S3 bucket directory) in order to load the directory. You should set an object lifecycle on the S3 bucket or that directory in order to delete those temp files after the data has been loaded. The details for how to do that are available on the [Spark-Redshift github repository](https://github.com/databricks/spark-redshift).
# MAGIC 
# MAGIC You'll have to use libraries functionality (click workspace, then menu, and create a library from Spark Packages) to load the Spark Redshift library.

# COMMAND ----------

# MAGIC %run /Users/bill@databricks.com/credentials/s3-credentials

# COMMAND ----------

# MAGIC %scala
# MAGIC archiveReady
# MAGIC   .write
# MAGIC   .format("com.databricks.spark.redshift")
# MAGIC     .option("url", jdbcUrl)
# MAGIC     .option("tempdir", s"s3a://$accessKey:$encodedSecretKey@$dstBucketName/temp-directory/")
# MAGIC     .option("dbtable", "example_data_warehouse")
# MAGIC   .mode(SaveMode.Overwrite) // comment this out if you don't want to overwrite the table!
# MAGIC   .save()

# COMMAND ----------

# MAGIC %md Now, due to business constraints, we also need to write a copy to S3 for backup. Let's do that now! By default Apache Spark will write data out using Parquet which is a columnar data format. I'm going to write that data to a folder on the S3 bucket that I created earlier but before doing that, I need to use `dbutils` to remove the fole that I have in there. `dbutils` has a great set of features that make working with Databricks awesome. We've seen that we can use it to mount S3 as a filesystem but it also provides the ability to create widgets and notebook utilities.
# MAGIC 
# MAGIC If you want to know more about `dbutils` you can also use `display` to see the documentation for it inline.

# COMMAND ----------

# MAGIC %scala
# MAGIC display(dbutils.widgets)

# COMMAND ----------

# MAGIC %md Now we can delete the folder.

# COMMAND ----------

# MAGIC %scala
# MAGIC dbutils.fs.rm("/mnt/dst-bucket/data-backup", true)

# COMMAND ----------

# MAGIC %md Now finally we can write out our data!

# COMMAND ----------

# MAGIC %scala
# MAGIC archiveReady.write.parquet("/mnt/dst-bucket/data-backup/")

# COMMAND ----------

# MAGIC %md ## Conclusion
# MAGIC 
# MAGIC Now we've done a ton of work in this notebook. Everything from reading and writing raw data to working with Spark-Redshift and leveraging some of the powers of Databricks notebooks. Hopefully this makes you a lot more familiar with what is capable inside of Databricks with Apache Spark!