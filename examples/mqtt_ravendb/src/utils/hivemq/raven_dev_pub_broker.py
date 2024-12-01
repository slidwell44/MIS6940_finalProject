import logging
from pyravendb.store.document_store import DocumentStore

from .base import McpPubBroker

logger = logging.getLogger(__name__)


class RavenDevPubBroker(McpPubBroker):
    def __init__(self):
        super().__init__(client_id="raven-dev-pub-broker")

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
