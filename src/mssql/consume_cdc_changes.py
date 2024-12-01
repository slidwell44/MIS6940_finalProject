import json
import logging
from typing import Optional
from uuid import UUID

from confluent_kafka import Consumer, KafkaError
from sqlalchemy import text

from src.db import get_connection, WiDatabases
from src.wikafka import McpKafkaTopics

logger = logging.getLogger(__name__)


class WorkorderChange:
    def __init__(self, operation, workorderid=None, workordernumber=None, revision=None, quantity=None):
        self.connection = get_connection(WiDatabases.LOCALDW)
        self.Operation: int = operation

        self.Id: Optional[UUID] = workorderid
        self.WorkorderNumber: Optional[str] = workordernumber
        self.Revision: Optional[str] = revision
        self.Quantity: Optional[float] = quantity

        if self.Operation == 1:  # DELETE
            self.delete_record()
        if self.Operation == 2:  # INSERT
            self.insert_record()
        if self.Operation == 3 or self.Operation == 4:  # UPDATE_BEFORE or UPDATE_AFTER
            self.update_record()

    def insert_record(self):
        with self.connection.session_scope() as session:
            session.execute(
                text(
                    """
                    EXEC dbo.sp_CreateWorkOrder
                        @Id = :workorderid,
                        @WorkorderNumber = :workordernumber,
                        @Revision = :revision,
                        @Quantity = :quantity;
                    """
                ),
                params={
                    "workorderid": self.Id,
                    "workordernumber": self.WorkorderNumber,
                    "revision": self.Revision,
                    "quantity": self.Quantity,
                }
            )

    def update_record(self):
        with self.connection.session_scope() as session:
            session.execute(
                text(
                    """
                    EXEC dbo.sp_UpdateWorkOrder
                        @Id = :workorderid,
                        @WorkorderNumber = :workordernumber,
                        @Revision = :revision,
                        @Quantity = :quantity;
                    """
                ),
                params={
                    "workorderid": self.Id,
                    "workordernumber": self.WorkorderNumber,
                    "revision": self.Revision,
                    "quantity": self.Quantity,
                }
            )

    def delete_record(self):
        with self.connection.session_scope() as session:
            session.execute(
                text(
                    """
                    EXEC dbo.sp_DeleteWorkOrder @Id = :workorderid;
                    """
                ),
                params={"workorderid": self.Id},
            )


class WorkOrderChangesConsumer:
    def __init__(self):
        self.kafka_consumer: Consumer = Consumer(
            {
                "bootstrap.servers": "localhost:9092",
                "group.id": "project-seminar-workorder-sink",
                "auto.offset.reset": "earliest",
            }
        )
        self.consume_topic: McpKafkaTopics = McpKafkaTopics.WORKORDER.value.name

        self.start()

    def consume_kafka_workorder_stream(self):
        try:
            self.kafka_consumer.subscribe([self.consume_topic])
            while True:
                msg = self.kafka_consumer.poll(1.0)

                if msg is None:
                    logger.debug("Waiting for Kafka messages...")
                    continue
                elif msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                        continue
                else:
                    topic = msg.topic()
                    key = msg.key().decode("utf-8") if msg.key() else None
                    # noinspection PyArgumentList
                    value = msg.value().decode("utf-8") if msg.value() else None
                    logger.info(f"Received message on topic {topic}: Key={key}, Value={value}")

                    try:
                        data = json.loads(value)
                        operation = data.get("__$operation")
                        workorderid = data.get("Id")
                        workordernumber = data.get("WorkorderNumber")
                        revision = data.get("Revision")
                        quantity = data.get("Quantity")

                        change = WorkorderChange(
                            operation=operation,
                            workorderid=workorderid,
                            workordernumber=workordernumber,
                            revision=revision,
                            quantity=quantity,
                        )
                        logger.info(f"Processed change: {change}")
                    except json.JSONDecodeError as jde:
                        logger.error(f"JSON decode error: {jde}")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
        except KeyboardInterrupt:
            logger.info("Kafka consumer interrupted by user.")
        except Exception as e:
            logger.error(f"An error occurred in Kafka consumer: {e}")
        finally:
            self.kafka_consumer.close()
            logger.info("Kafka consumer closed.")

    def start(self):
        self.consume_kafka_workorder_stream()


if __name__ == '__main__':
    changes_sink = WorkOrderChangesConsumer()
