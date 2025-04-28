import os
import uuid

from dotenv import load_dotenv
from pandas import DataFrame

# PySpark
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType, TimestampType
from pyspark.sql.functions import col

# ClickHouse Drivers
from clickhouse_driver import Client


class DataHandler:
    """
    Class for handling data transactions with ClickHouse via Spark.
    """

    def __init__(
        self,
        use_local_host=False, # TODO: Determine this using just env variables!
    ):

        load_dotenv()

        # Connection Parameters
        self.CLICKHOUSE_PORT_HTTP = os.getenv("CLICKHOUSE_PORT_HTTP")
        self.CLICKHOUSE_PORT_CONSOLE = os.getenv("CLICKHOUSE_PORT_CONSOLE")
        self.CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER")
        self.CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD")
        self.CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB")
        self.CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST_LOCAL") if use_local_host else os.getenv("CLICKHOUSE_HOST")

        self.CLICKHOUSE_URL = f"jdbc:clickhouse://{self.CLICKHOUSE_HOST}:{self.CLICKHOUSE_PORT_HTTP}/{self.CLICKHOUSE_DB}"
        self.CLICKHOUSE_DRIVER = "com.clickhouse.jdbc.ClickHouseDriver"

        self.JARS_PATH = "/opt/spark/jars/*"

        # Medium Articles Schema - Spark
        self.MEDIUM_ARTICLES_TABLE = "medium_articles"
        self.MEDIUM_ARTICLES_SCHEMA = StructType([
            StructField("id", StringType(), False),
            StructField("title", StringType(), False),
            StructField("published_date", TimestampType(), True),
            StructField("paywall", BooleanType(), True),
            StructField("claps", IntegerType(), True),
            StructField("comments", IntegerType(), True),
            StructField("link", StringType(), True),
            StructField("tag", StringType(), True),
            StructField("topic_name", StringType(), True),
            StructField("topic_type", StringType(), True),
            StructField("version", IntegerType(), True)
        ])


    # CLICKHOUSE DRIVER
    # -----------------


    def initialiseClickHouseConnection(
        self,
    ) -> bool:
        """
        Try to initialise a ClickHouse connection, and returens True if successful.
        """

        try:
            self.client = Client(
                host=self.CLICKHOUSE_HOST,
                port=self.CLICKHOUSE_PORT_CONSOLE,
                user=self.CLICKHOUSE_USER,
                password=self.CLICKHOUSE_PASSWORD,
                database=self.CLICKHOUSE_DB,
            )
        except Exception as e:
            print(f"Error with ClickHouse connection: {e}")
            return False

        return True
    

    def writeToClickhouse(
        self,
        data : list,
    ):
        """
        Writes a pandas dataframe to ClickHouse.
        """
        
        for record in data: record["id"] = str(uuid.uuid4())

        try:
            self.client.execute(
                f"INSERT INTO {self.MEDIUM_ARTICLES_TABLE} VALUES",
                data,
            )
            return True
        except Exception as e:
            print(f"Error writing to ClickHouse: {e}")
            return False


    # SPARK
    # -----


    def initialiseClickHouseConnectionSpark(
        self,
    ) -> bool:
        """
        Try to initialise a Spark session, and returens True if successful.
        """

        # Don't think we need this line
        # .config("spark.jars", self.JARS_PATH) \

        try:
            self.spark = SparkSession.builder \
                .appName("MediumScraper") \
                .config("spark.driver.extraClassPath", self.JARS_PATH) \
                .config("spark.executor.extraClassPath", self.JARS_PATH) \
                .getOrCreate()
        except Exception as e:
            print(f"Error with ClickHouse connection: {e}")
            return False

        return True
    

    def writeToClickhouseSpark(
        self,
        data : list,
    ):
        """
        Writes a pandas dataframe to ClickHouse.
        """

        # TODO: Check for duplicate records before writing to ClickHouse!!!

        for record in data: record["id"] = str(uuid.uuid4())

        df = self.spark.createDataFrame(data, schema=self.MEDIUM_ARTICLES_SCHEMA).withColumn("id", col("id").cast("string"))

        df.write \
            .format("jdbc") \
            .option("url", self.CLICKHOUSE_URL) \
            .option("dbtable", self.MEDIUM_ARTICLES_TABLE) \
            .option("user", self.CLICKHOUSE_USER) \
            .option("password", self.CLICKHOUSE_PASSWORD) \
            .option("driver", self.CLICKHOUSE_DRIVER) \
            .mode("append") \
            .save()