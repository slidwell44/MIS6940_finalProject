import json
import logging

from .base import McpSubBroker
from src.utils.wikafka import McpKafkaTopics

logger = logging.getLogger(__name__)


class DefectReportSubBroker(McpSubBroker):
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
            defect_report_number = split_topic[3]
            order_number = split_topic[4].zfill(12)
            part_number = split_topic[5]
            serial_number = split_topic[6]

            key = f"order:{order_number}" if order_number else f"part_number:{part_number}"

            body = {
                "defect_report_number": defect_report_number,
                "order_number": order_number,
                "part_number": part_number,
                "serial_number": serial_number,
                "mqtt_topic": mqtt_topic,
                "mqtt_payload": payload,
            }

            try:
                # # TODO: Combining steams is cool and all but how do I know the source system?
                # #  Infer from the MQTT topic?
                # #  Or should I create labels that contain the source systems information?
                # self.wikafka_manager.kafka_producer.produce(
                #     topic=McpKafkaTopics.DEFECT_REPORT.value.name,
                #     key=key,
                #     value=json.dumps(body),
                #     callback=self.wikafka_manager.delivery_callback,
                # )
                # logger.debug(f"Message sent to kafka topic {McpKafkaTopics.DEFECT_REPORT.value.name}")

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
            logger.error(
                f"""
                Message: Failed to load mqtt payload into json: {str(msg.payload) if msg.payload else None} into json
                Error: {e}
                """
            )
        except Exception as e:
            logger.error(f"An error occurred: {e}")
