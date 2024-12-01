import json
import logging

from .base import McpSubBroker
from src.utils.wikafka import McpKafkaTopics

logger = logging.getLogger(__name__)


class FacilitiesTimeSeriesSubBroker(McpSubBroker):
    def __init__(self, client_id, **kwargs):
        super().__init__(client_id=client_id, **kwargs)

    def on_message(self, client, userdata, msg):
        if self.wikafka_manager.kafka_producer is None:
            logger.error("Kafka producer is not initialized.")
            return

        mqtt_topic = msg.topic

        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            logger.debug(f"Message received on topic {mqtt_topic}: {payload}")

            split_topic = mqtt_topic.split("/")
            site = split_topic[2]

            body = {
                "site": site,
                "mqtt_topic": mqtt_topic,
                "mqtt_payload": payload
            }

            try:
                self.wikafka_manager.kafka_producer.produce(
                    topic=McpKafkaTopics.IMS_TPM_STATUS.value.name,
                    key=site,
                    value=json.dumps(body),
                    callback=self.wikafka_manager.delivery_callback,
                )
                logger.debug(f"Message sent to kafka topic {McpKafkaTopics.IMS_TPM_STATUS.value.name}")

                self.wikafka_manager.kafka_producer.flush()
            except Exception as e:
                logger.error(f"Failed to send message to kafka: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to load mqtt payload into json: {e}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
