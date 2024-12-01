import logging
from src.utils.wikafka import McpKafkaTopics
from confluent_kafka import Consumer, KafkaError
import json
from pyravendb.store.document_store import DocumentStore
from typing import List

logger = logging.getLogger(__name__)


class RavenDbPayload:
    def __init__(self, kafka_topic, kafka_topic_key, kafka_payload):
        self.kafka_topic = kafka_topic
        self.kafka_topic_key = kafka_topic_key
        self.kafka_payload = kafka_payload


class WiKafkaImsTpmSink:
    def __init__(self):
        self.kafka_consumer: Consumer = Consumer(
            {
                "bootstrap.servers": "localhost:9092",
                "group.id": "ravendb-ims-tpm-sink",
                "auto.offset.reset": "earliest",
            }
        )

        self.consume_topic: McpKafkaTopics = McpKafkaTopics.IMS_TPM_STATUS.value

        self.urls: List[str] = ["http://localhost:8080"]
        self.db = "Mcp"
        self.ravendb_store = DocumentStore(urls=self.urls, database=self.db)

        try:
            self.ravendb_store.initialize()

            # noinspection PyProtectedMember
            if not self.ravendb_store._initialize:
                raise Exception("Failed to initialize the RavenDB store")
        except Exception as e:
            logger.error(f"RavenDB initialization failed: {e}")
            raise

        self.start()

    def workorder_ravendb_sink(self):
        self.kafka_consumer.subscribe([self.consume_topic.name])

        try:
            while True:
                msg = self.kafka_consumer.poll(1.0)
                if msg is None:
                    logger.info("Waiting...")
                    continue
                elif msg.error():
                    # noinspection PyProtectedMember
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                        continue
                else:
                    topic = msg.topic()
                    key = msg.key().decode("utf-8") if msg.key() else None
                    value = msg.value().decode("utf-8") if msg.value() else None
                    logger.info(f"Received message on topic {topic}: Key={key}, Value={value}")

                    try:
                        value_json = json.loads(value)
                        mqtt_topic = value_json.get("mqtt_topic")

                        payload = RavenDbPayload(
                            kafka_topic=topic,
                            kafka_topic_key=key,
                            kafka_payload=value_json
                        )

                        with self.ravendb_store.open_session() as session:
                            session.store(
                                entity=payload,
                                key=mqtt_topic
                            )

                            metadata = session.advanced.get_metadata_for(payload)
                            metadata["@collection"] = "kafka-ims-tpm-status"

                            session.save_changes()

                            logger.debug(f"Stored {mqtt_topic} in RavenDB")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to load MQTT payload into JSON: {e}")
                    except Exception as e:
                        logger.error(f"Failed to store to RavenDB: {e}")

        except KeyboardInterrupt:
            logger.info("Kafka consumer interrupted by user.")
        except Exception as e:
            logger.error(f"An error occurred in Kafka consumer: {e}")
        finally:
            self.kafka_consumer.close()
            logger.info("Kafka consumer closed.")

    def start(self):
        self.workorder_ravendb_sink()

    def stop(self):
        pass


if __name__ == "__main__":
    ims_tpm_status_sink = WiKafkaImsTpmSink()
