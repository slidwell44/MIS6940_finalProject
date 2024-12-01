import json
import logging

from .base import McpSubBroker
from src.utils.wikafka import McpKafkaTopics

logger = logging.getLogger(__name__)


class WorkOrderSubBroker(McpSubBroker):
    def __init__(self, client_id, **kwargs):
        super().__init__(client_id=client_id, **kwargs)

    def process_message(self, msg):
        if self.wikafka_manager.kafka_producer is None:
            logger.error("Kafka producer is not initialized.")
            return

        mqtt_topic = msg.topic

        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            logger.debug(f"Message received on topic {mqtt_topic}: {payload}")

            split_topic = mqtt_topic.split("/")
            order_number = split_topic[3] if len(split_topic) > 3 else None
            part_number = split_topic[4] if len(split_topic) > 4 else None

            key = f"order:{order_number}"

            body = {
                "order_number": order_number,
                "part_number": part_number,
                "mqtt_topic": mqtt_topic,
                "mqtt_payload": payload,
            }

            try:
                self.wikafka_manager.kafka_producer.produce(
                    topic=McpKafkaTopics.WORKORDER.value.name,
                    key=key,
                    value=json.dumps(body),
                    callback=self.wikafka_manager.delivery_callback,
                )
                self.wikafka_manager.kafka_producer.flush()

                logger.debug(f"Message sent to Kafka topic {McpKafkaTopics.WORKORDER.value.name}")
            except Exception as e:
                logger.error(f"Failed to send message to Kafka: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MQTT payload as JSON: {e}")
        except Exception as e:
            logger.exception(f"An error occurred while processing the message: {e}")
