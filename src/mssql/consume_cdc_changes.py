import json
import logging
from typing import Optional, List
from uuid import UUID

from IPython.core.payload import PayloadManager
from confluent_kafka import Consumer, KafkaError
from pyravendb.store.document_store import DocumentStore
from sqlalchemy import text

from src.db import get_connection, WiDatabases
from src.wikafka import McpKafkaTopics

logger = logging.getLogger(__name__)


class RavenDbPayload:
    def __init__(self, kafka_topic, kafka_topic_key, kafka_payload):
        self.kafka_topic = kafka_topic
        self.kafka_topic_key = kafka_topic_key
        self.kafka_payload = kafka_payload


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

        self.urls: List[str] = ["http://localhost:8080"]
        self.db = "ProjectSeminar"
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

                        payload = RavenDbPayload(
                            kafka_topic=topic,
                            kafka_topic_key=key,
                            kafka_payload=data,
                        )
                        
                        with self.ravendb_store.open_session() as session:
                            session.store(
                                entity=payload,
                                key=workorderid,
                            )

                            metadata = session.advanced.get_metadata_for(payload)
                            metadata["@collection"] = "workorder-changes"

                            session.save_changes()
                            logger.debug(f"Stored {workordernumber} change in RavenDB")
                            
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
