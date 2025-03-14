from typing import Any
import time
import json

import paho.mqtt.client as mqtt


def load_config():
    with open("server/app/services/mqtt_service/config.json") as f:
        return json.load(f)


class MQTTPub:
    def __init__(self):
        conf = load_config()

        self.conn_config = conf["mqtt_conn"]
        self.topic = conf["mqtt_topic"]

        client_id = f"server-pub-{int(time.time())}"
        self.client = mqtt.Client(client_id=client_id)

        self.client.username_pw_set(
            username=self.conn_config["username"],
            password=self.conn_config["password"]
        )

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish

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
            print("Connected succesfully")
        else:
            print(f"Connection error with rc: {reason_code}")

            time.sleep(1)
            self._connect()

    def _on_disconnect(self, client, userdata, reason_code):
        print(f"Disconnected from MQTT broker with rc: {reason_code}")
        
        if reason_code != 0:
            time.sleep(2)
            self._connect()
    
    def _on_publish(self, client, userdata, mid):
        print(f"Message {mid} was successfully published")
        
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

        print("Message: ", message, "\n")

        if not self.client.is_connected():
            self._connect()
            time.sleep(1)

        res = self.client.publish(
            topic=self.topic["topic"], 
            payload=json.dumps(message),
            qos=self.topic["qos"]
        )

        print("Result: ", res, "\n")

        if res.rc != 0:
            return False
        return True
    
    def exit(self):
        self.client.loop_stop()
        self.client.disconnect()


class MQTTSub:
    def __init__(self, admin_user):
        conf = load_config()

        self.conn_config = conf["mqtt_conn"]
        self.topic = conf["mqtt_topic"]
        
        client_id = f"admin-{admin_user['id']}-{int(time.time())}"
        self.client = mqtt.Client(client_id=client_id)

        self.client.username_pw_set(
            username=f"admin-{admin_user['id']}",
            password="password"
        )

        self._connect()

        self.client.loop_forever()

    def _connect(self):
        self.client.connect(
            self.conn_config["host"],
            self.conn_config["port"],
            self.conn_config["keepalive"]
        )

    def subscribe(self):
        try:
            if not self.client.is_connected():
                self._connect()
                time.sleep(1)

            self.client.subscribe(self.topic["topic"], qos=self.topic["qos"])
        
            return True
        except Exception as e:
            return False

    def exit(self):
        self.client.loop_stop()
        self.client.disconnect()
