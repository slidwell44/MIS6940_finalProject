import abc
from concurrent.futures import ThreadPoolExecutor
import logging
import os
import ssl
import socket
import threading
from typing import List

from src.utils.wikafka import WiKafka

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class McpSubBroker(abc.ABC):
    instances_lock = threading.Lock()
    instances: List["McpSubBroker"] = []

    def __init__(
            self,
            broker: str = "wihiveprodsrv01.williams-int.com",
            port: int = 8883,
            username: str = "mqttprodsuball",
            password: str = "wQcnhWdHJTCu3vGVrn9W",
            client_id: str = "base-mqtt-sub-client",
    ):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.ca_certs = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "certs", "CAChain.crt")
        )

        if not os.path.exists(self.ca_certs):
            raise FileNotFoundError(f"CA Certificate not found at {self.ca_certs}")

        self.client_id = client_id
        self.client = mqtt.Client(
            client_id=self.client_id,
            userdata=None,
            protocol=mqtt.MQTTv311,
            transport="tcp",
        )

        self.client.username_pw_set(self.username, self.password)

        self.client.tls_set(
            ca_certs=self.ca_certs,
            certfile=None,
            keyfile=None,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS,
            ciphers=None,
        )

        self.client.tls_insecure_set(False)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        try:
            self.wikafka_manager = WiKafka()
            if self.wikafka_manager.kafka_producer is None:
                logger.error("WiKafka manager's kafka_producer is None after initialization.")
        except Exception as e:
            logger.error(f"Failed to initialize WiKafka manager: {e}")
            self.wikafka_manager = None

        self.executor = ThreadPoolExecutor(max_workers=10)

        with self.instances_lock:
            self.instances.append(self)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"Connected with result code {rc}")
        else:
            logger.error(f"Connection failed with result code {rc}")

    def on_message(self, client, userdata, msg):
        self.executor.submit(self.process_message, msg)

    def connect(self):
        try:
            logger.info(f"CA Certificate: {self.ca_certs}")

            # Verify DNS resolution before attempting to connect
            try:
                resolved_ip = socket.gethostbyname(self.broker)
                logger.info(f"Resolved IP for {self.broker}: {resolved_ip}")
            except socket.gaierror as dns_error:
                logger.error(f"DNS resolution failed for {self.broker}: {dns_error}")
                raise

            rc = self.client.connect(self.broker, self.port, 60)

            if rc != 0:
                raise ConnectionError(f"Failed to connect to MQTT Broker at {self.broker}. Return code: {rc}")

            logger.info(f"Connect function returned with code {rc} (0 means success)")
            return rc
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise

    def subscribe(self, topic):
        logger.info(f"Subscribing to topic {topic}")
        self.client.subscribe(topic)

    def loop_forever(self):
        logger.debug(f"Looping mqtt process forever...")
        self.client.loop_forever()

    def loop_start(self):
        logger.debug(f"Starting mqtt loop process")
        self.client.loop_start()

    def loop_stop(self):
        logger.debug(f"Stopping mqtt loop process")
        self.client.loop_stop()

    def disconnect(self):
        logger.info(f"Disconnecting MQTT Broker")
        self.client.disconnect()
        with self.instances_lock:
            if self in self.instances:
                self.instances.remove(self)

    @abc.abstractmethod
    def process_message(self, msg):
        """Process mqtt message"""
        pass

    def shutdown(self):
        self.executor.shutdown(wait=True)
        logger.debug(f"ThreadPoolExecutor shut down for {self.client_id}")

    @classmethod
    def close_all(cls):
        with cls.instances_lock:
            for instance in cls.instances[:]:
                try:
                    instance.loop_stop()
                    instance.disconnect()
                    instance.shutdown()
                except Exception as e:
                    logger.exception(f"Error closing broker {instance.client_id}, error: {e}")
