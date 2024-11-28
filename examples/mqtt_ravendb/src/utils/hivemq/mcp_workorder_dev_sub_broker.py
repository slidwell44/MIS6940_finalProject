import json
import logging

from .base import McpSubBroker
from src.utils.wikafka import McpKafkaTopics

logger = logging.getLogger(__name__)


class McpWorkOrderDevSubBroker(McpSubBroker):
    def __init__(self, client_id, **kwargs):
        broker: str = "wihivedevsrv.williams-int.com"
        username: str = "mqttdevclientsub"
        password: str = "Summer-2024"

        super().__init__(client_id=client_id,
                         broker=broker,
                         username=username,
                         password=password,
                         **kwargs)

    def process_message(self, msg):
        if self.wikafka_manager.kafka_producer is None:
            logger.error("Kafka producer is not initialized.")
            return

        mqtt_topic = msg.topic

        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            logger.debug(f"Message received on topic {mqtt_topic}: {payload}")

            split_topic = mqtt_topic.split("/")
            order_number = split_topic[3].zfill(12) if len(split_topic) > 3 else None

            key = f"order:{order_number}"

            body = {
                "order_number": order_number,
                "mqtt_topic": mqtt_topic,
                "mqtt_payload": payload,
            }

            try:
                # # TODO: Combining steams is cool and all but how do I know the source system?
                # #  Infer from the MQTT topic?
                # #  Or should I create labels that contain the source systems information?
                # self.wikafka_manager.kafka_producer.produce(
                #     topic=McpKafkaTopics.MCP.value.name,
                #     key=key,
                #     value=json.dumps(body),
                #     callback=self.wikafka_manager.delivery_callback,
                # )
                # logger.debug(f"Message sent to kafka topic {McpKafkaTopics.MCP.value.name}")

                # TODO: Why wouldn't you want to join the DR to the workorder/operation that it was created for?
                #   Like it was a requirement of MCP that an object requirement (type: defect report) have an object (operation)
                #   and a requirement (defect report requirement)
                self.wikafka_manager.kafka_producer.produce(
                    topic=McpKafkaTopics.WORKORDER.value.name,
                    key=key,
                    value=json.dumps(body),
                    callback=self.wikafka_manager.delivery_callback,
                )
                logger.debug(f"Message sent to kafka topic {McpKafkaTopics.WORKORDER.value.name}")

                self.wikafka_manager.kafka_producer.flush()
            except Exception as e:
                logger.error(f"Failed to send message to kafka: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to load mqtt payload into json: {e}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
