import json
import logging
from pyravendb.store.document_store import DocumentStore
from typing import Optional

from .base import McpSubBroker
from .models import SimplePayload

logger = logging.getLogger(__name__)


class RavenDevSubBroker(McpSubBroker):
    def __init__(self, client_id: Optional[str] = "raven-dev-sub-broker"):
        super().__init__(
            broker="wihivedevsrv.williams-int.com",
            username="mqttdevclientsub",
            password="Summer-2024",
            client_id=client_id
        )

        self.urls = ["http://localhost:8080"]
        self.db = "Mcp"
        self.ravendb_store = DocumentStore(urls=self.urls, database=self.db)

        try:
            self.ravendb_store.initialize()

            # noinspection PyProtectedMember
            if not self.ravendb_store._initialize:
                raise Exception("Failed to initialize the RavenDB store")
        except Exception as e:
            logger.error(e)
            raise

    def on_message(self, client, userdata, msg):
        topic = msg.topic

        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            logger.debug(f"Message received on topic {topic}: {payload}")

            message = SimplePayload(payload)

            with self.ravendb_store.open_session() as session:
                session.store(
                    entity=message,
                    key=topic
                )

                metadata = session.advanced.get_metadata_for(message)
                metadata["@collection"] = "dev"

                session.save_changes()

                logger.debug(f"Stored {topic} in RavenDB")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to load mqtt payload into json: {e}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
