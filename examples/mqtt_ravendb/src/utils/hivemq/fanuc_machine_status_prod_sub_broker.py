import json
import logging

from .base import McpSubBroker
from src.utils.wikafka import McpKafkaTopics

logger = logging.getLogger(__name__)


class FanucMachineStatusSubBroker(McpSubBroker):
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
            site = split_topic[3]
            machine = split_topic[4]

            body = {
                "site": site,
                "machine": machine,
                "mqtt_topic": mqtt_topic,
                "mqtt_payload": payload
            }

            try:
                # self.wikafka_manager.kafka_producer.produce(
                #     topic=McpKafkaTopics.FANUC_MACHINE_STATUS.value.name,
                #     key=machine,
                #     value=json.dumps(body),
                #     callback=self.wikafka_manager.delivery_callback,
                # )
                # logger.debug(f"Message sent to kafka topic {McpKafkaTopics.FANUC_MACHINE_STATUS.value.name}")

                self.wikafka_manager.kafka_producer.produce(
                    topic=McpKafkaTopics.MACHINES.value.name,
                    key=machine,
                    value=json.dumps(body),
                    callback=self.wikafka_manager.delivery_callback,
                )
                logger.debug(f"Message sent to kafka topic {McpKafkaTopics.MACHINES.value.name}")

                self.wikafka_manager.kafka_producer.flush()
            except Exception as e:
                logger.error(f"Failed to send message to kafka: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to load mqtt payload into json: {e}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
