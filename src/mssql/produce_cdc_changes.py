import json
import logging
import time

from sqlalchemy import text, LABEL_STYLE_NONE
from sqlalchemy.engine.cursor import ResultFetchStrategy

from src.db import get_connection, WiDatabases
from src.wikafka import McpKafkaTopics, WiKafka

logger = logging.getLogger(__name__)


def convert_bytes_to_strings(records):
    """
    Converts all bytes objects in the records to hexadecimal strings.
    """
    converted = []
    for record in records:
        new_record = {}
        for key, value in record.items():
            if isinstance(value, bytes):
                new_record[key] = value.hex()  # Convert bytes to hex string
                # Alternatively, use value.decode('utf-8', errors='replace') if applicable
            else:
                new_record[key] = value
        converted.append(new_record)
    return converted


class WorkOrderChangesProducer:
    def __init__(self):
        self.last_lsn = None
        try:
            self.wikafka_manager = WiKafka()
            if self.wikafka_manager.kafka_producer is None:
                logger.error("WiKafka manager's kafka_producer is None after initialization.")
        except Exception as e:
            logger.error(f"Failed to initialize WiKafka manager: {e}")
            self.wikafka_manager = None

    def fetch_cdc_changes(self):
        conn = get_connection(WiDatabases.LOCALDB)
        with conn.session_scope() as session:
            lsn = session.execute()
            result = session.execute(
                text(
                    """EXEC dbo.Get_CDC_Changes"""
                )
            )
            columns = result.keys()
            rows = result.fetchall()

        if not rows:
            logger.info("No CDC changes found.")
            return

        db_changes = [dict(zip(columns, row)) for row in rows]

        db_changes = convert_bytes_to_strings(db_changes)

        try:
            for record in db_changes:
                key = record.get('id')
                self.wikafka_manager.kafka_producer.produce(
                    topic=McpKafkaTopics.WORKORDER.value.name,
                    key=str(key),
                    value=json.dumps(record),
                    callback=self.wikafka_manager.delivery_callback,
                )
            self.wikafka_manager.kafka_producer.flush()
            logger.debug(f"Messages sent to Kafka topic {McpKafkaTopics.WORKORDER.value.name}")
        except Exception as e:
            logger.error(f"Failed to send messages to Kafka: {e}")


if __name__ == "__main__":
    changes = WorkOrderChangesProducer()
    try:
        while True:
            changes.fetch_cdc_changes()
            time.sleep(5)
    except KeyboardInterrupt:
        logger.debug("Exiting...")
