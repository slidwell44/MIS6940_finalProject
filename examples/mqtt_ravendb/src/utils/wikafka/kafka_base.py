import logging
from typing import List

from .kafka_topics import McpKafkaTopics
from .singleton_meta import SingletonMeta

from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, ClusterMetadata, KafkaException, NewTopic

logger = logging.getLogger(__name__)


class WiKafka(metaclass=SingletonMeta):
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            logger.debug("WiKafka instance already initialized.")
            return

        self.kafka_host: str = "localhost:9092"
        self.kafka_config: dict = {
            "bootstrap.servers": self.kafka_host,
            "acks": "all",
        }

        self.kafka_admin: AdminClient = AdminClient(
            self.kafka_config,
            logger=logger
        )

        try:
            self.kafka_topics: ClusterMetadata = self.kafka_admin.list_topics()
        except KafkaException as e:
            logger.error(f"Failed to load Kafka topics list: {e}")
            raise

        self.topics_to_create: List[NewTopic] = []

        self.create_topics()

        self.kafka_producer: Producer = Producer(
            self.kafka_config,
            logger=logger
        )

        if self.kafka_producer is None:
            logger.error("Failed to initialize Kafka producer.")
        else:
            logger.debug("Kafka producer initialized successfully.")

        self._initialized = True

    @staticmethod
    def delivery_callback(err, msg):
        if err:
            logger.error(f'ERROR: Message failed delivery: {err}')
        else:
            logger.debug(
                f"Produced event to topic {msg.topic()}: key = {msg.key().decode('utf-8'):12} value = {msg.value().decode('utf-8'):12}")

    def create_topics(self):
        for my_topic in McpKafkaTopics:
            topic_config = my_topic.value
            if topic_config.name not in self.kafka_topics.topics:
                new_topic = NewTopic(
                    topic=topic_config.name,
                    num_partitions=topic_config.num_partitions,
                    replication_factor=topic_config.replication_factor,
                )
                self.topics_to_create.append(new_topic)
                logger.debug(f"Added {topic_config} to the list of topics to create.")

        if self.topics_to_create:
            try:
                fs = self.kafka_admin.create_topics(self.topics_to_create)

                for topic, f in fs.items():
                    try:
                        f.result()
                        logger.info(f"Topic '{topic}' created successfully.")
                    except Exception as e:
                        logger.error(f"Failed to create topic '{topic}': {e}")
            except KafkaException as e:
                logger.error(f"Kafka exception occurred while creating topics: {e}")

    def close(self):
        """
        Close the Kafka Producer
        """
        if hasattr(self, 'kafka_producer') and self.kafka_producer:
            try:
                self.kafka_producer.flush()
                logger.debug("Kafka Producer flushed successfully.")
            except Exception as e:
                logger.error(f"Error flushing Kafka Producer: {e}")
