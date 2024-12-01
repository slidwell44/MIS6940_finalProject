import logging
import os
import paho.mqtt.client as mqtt
import ssl

logger = logging.getLogger(__name__)


class McpPubBroker:
    def __init__(
            self,
            broker: str = "wihivedevsrv.williams-int.com",
            port: int = 8883,
            username: str = "mqttdevclientpub",
            password: str = "0rangeCamaro",
            client_id: str = "base-mqtt-pub-client",
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
        self.client.on_publish = self.on_publish

    def on_connect(self, client, userdata, flags, rc):
        if not self.client.is_connected():
            if rc == 0:
                logger.debug(f"Connected with result code {rc}")
            else:
                logger.debug(f"Connection failed with result code {rc}")

    def on_publish(self, client, userdata, mid):
        logger.debug(f"Message published with mid {mid}")

    def connect(self):
        try:
            logger.debug(f"CA Certificate: {self.ca_certs}")

            rc = self.client.connect(self.broker, self.port, 60)

            if rc != 0:
                raise ConnectionError(f"Failed to connect to MQTT Broker at {self.broker}. Return code: {rc}")

            logger.debug(f"Connect function returned with code {rc} (0 means success)")
            return rc
        except Exception as e:
            logger.debug(f"Connection error: {e}")
            raise

    def publish(self, topic, payload, qos=1, retain=True):
        logger.debug(f"Publishing to topic {topic} with QoS {qos} and retain={retain}")
        result, mid = self.client.publish(topic, payload, qos=qos, retain=retain)
        logger.debug(f"Publish result: {result}, mid: {mid}")
        return result, mid

    def loop_forever(self):
        logger.debug(f"Looping MQTT process forever...")
        self.client.loop_forever()

    def loop_start(self):
        logger.debug(f"Starting MQTT loop process")
        self.client.loop_start()

    def loop_stop(self):
        logger.debug(f"Stopping MQTT loop process")
        self.client.loop_stop()

    def disconnect(self):
        logger.debug(f"Disconnecting MQTT Broker")
        self.client.disconnect()
