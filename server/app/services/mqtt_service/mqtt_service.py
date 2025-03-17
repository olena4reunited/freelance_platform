from typing import Any
import time
import json

import paho.mqtt.client as mqtt

from server.app.utils.logger import logger
from server.app.utils.operations import time_incrementing


MAX_ATTEMPTS = 5


def load_config():
    with open("server/app/services/mqtt_service/config.json") as f:
        return json.load(f)
   

class MQTTService:
    def __init__(self):
        conf = load_config()

        self.conn_config = conf["mqtt_conn"]
        self.topic = conf["mqtt_topic"]

        client_id = f"broker-mqtt-{int(time.time())}"
        self.client = mqtt.Client(client_id=client_id)

        self.client.username_pw_set(
            username=self.conn_config["username"],
            password=self.conn_config["password"]
        )

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        self._connect()
        
        self.client.loop_start()
    
    def _connect(self):
        self.client.connect(
            self.conn_config["host"],
            self.conn_config["port"],
            self.conn_config["keepalive"]
        )
    
    def _on_connect(self, client, userdata, flags, reason_code):
        if reason_code == 0:
            logger.info(
                "MQTT client-publisher was succesfully connected"
            )
        else:
            prev, sec = 0, 1
            
            for _ in range(0, MAX_ATTEMPTS, 1):
                if self.client.is_connected():
                    break

                logger.error(
                    "Error in MQTT client-publisher connection. Trying to reconnect"
                )
                prev, sec = time_incrementing(prev, sec)
                
                time.sleep(sec)
                self._connect()
            
            if not self.client.is_connected():
                logger.critical(
                    "Unsuccesfully finished \x1b[1m%s\x1b[0m attempts to process " \
                    "MQTT client reconnection!",
                    MAX_ATTEMPTS
                )

    def _on_disconnect(self, client, userdata, reason_code):
        self.client.loop_stop()

        logger.info(
            "Disconnected client from MQTT broker with reason_code: \x1b[1m%s\x1b[0m",
            reason_code
        )

        if reason_code != 0:
            logger.critical(
                "Error was ocured while client disconnection from MQTT broker! " \
                "Disconnected with reason_code: \x1b[1m%s\x1b[0m",
                reason_code
            )

    def publish_new_order(
            self,
            order_data: dict[str, Any], 
            user_data: dict[str, Any]
    ):
        message = {
            "message": "New order was created!",
            "order": {
                "order_id": order_data["id"],
                "order_name": order_data["name"],
                "order_description": order_data["description"],
                "order_customer": {
                    "user_id": user_data["id"],
                    "username": user_data["username"]
                },
            },
            "timestamp": time.time()
        }

        if not self.client.is_connected():
            self._connect()

        res = self.client.publish(
            topic=self.topic["topic"], 
            payload=json.dumps(message),
            qos=self.topic["qos"]
        )

        if res.rc != 0:
            logger.order(
                "Error was ocured while publication orders/new to MQTT broker! " \
                "Publication proceessin result reason_code: \x1b[1m%s\x1b[0m",
                res.rc
            )
            return False
        else:
            logger.info(
                "Client succesfully published new order to MQTT broker " \
                "for clients-subscribers"
            )
            return True

    def subscribe_on_orders(self):
        if not self.client.is_connected():
            self._connect()

        self.client.subscribe(self.topic["topic"], qos=self.topic["qos"])
 

mqtt = MQTTService()