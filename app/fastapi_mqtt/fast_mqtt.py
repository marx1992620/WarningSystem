import os
import asyncio
import logging
import sys
import json, time
import uuid
from datetime import datetime
from gmqtt import Client as MQTTClient
from fastapi_mqtt.method import methods
from api.request import query_warning_config, post_warning_record
from queue import Queue


class FastMQTT:

    MQTT_BROKER = '127.0.0.1'  # MQTT broker address
    MQTT_PORT = 1883  # MQTT broker port
    MQTT_USERNAME = 'account'  # MQTT broker username
    MQTT_PASSWORD = 'pwd'  # MQTT broker password
    CONNECTION = False
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),"dst")
    WARNING_CONFIG_PATH = os.path.join(DATA_DIR,"warning_config.json")
    WARNING_CONFIG = {}
    instance = ""
    topic_payload = {}
    warning_queue = Queue()
    warning_history = {}
    # screen_interval = 1

    def __init__(self, app):
        self.app = app
        client_id = uuid.uuid4().hex
        self.client = MQTTClient(client_id)
        FastMQTT.instance = self.client

        if not os.path.exists(FastMQTT.WARNING_CONFIG_PATH):
            FastMQTT.WARNING_CONFIG = {"rules":[],"subscribed":[],"connection":FastMQTT.CONNECTION}
        else:
            FastMQTT.WARNING_CONFIG = FastMQTT.read_config(FastMQTT.WARNING_CONFIG_PATH)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.monitor
            
    def read_config(file_path):
        with open(file_path, 'r') as f:
            config = json.load(f)
        return config

    def save_config():
        with open(FastMQTT.WARNING_CONFIG_PATH, 'w') as f:
            f.write(json.dumps(FastMQTT.WARNING_CONFIG, indent=4, default=str))

    def on_connect(self, client, flags, rc, properties):
        logging.info('Connected to MQTT Broker')
        FastMQTT.CONNECTION = True
        FastMQTT.WARNING_CONFIG["connection"] = FastMQTT.CONNECTION
        FastMQTT.save_config()

        # Check for new topics to subscribe
        for i in range(len(FastMQTT.WARNING_CONFIG['rules'])):
            topic = FastMQTT.WARNING_CONFIG['rules'][i]["topic"]
            # if topic not in FastMQTT.WARNING_CONFIG["subscribed"]:
            FastMQTT.instance.subscribe(topic)  # missing 3 required positional arguments: 'mid', 'qos', and 'properties'
                # print(f"Subscribed to topic: {topic}")
                # FastMQTT.WARNING_CONFIG["subscribed"].append(topic)


    def on_disconnect(self, client, packet, exc=None):
        logging.info('Disconnected to MQTT Broker')
        FastMQTT.CONNECTION = False
        FastMQTT.WARNING_CONFIG["connection"] = FastMQTT.CONNECTION
        FastMQTT.save_config()


    def on_subscribe(self, client, mid, qos, properties):
        print(f'Subscribed to topic. {client}')


    async def monitor(self, client, topic, payload, qos, properties):
        print(f'\nReceived message on topic {topic}: {payload.decode()}')
        if FastMQTT.WARNING_CONFIG == {}:
            FastMQTT.WARNING_CONFIG = FastMQTT.read_config(FastMQTT.WARNING_CONFIG_PATH)
        else:
            for i in range(len(FastMQTT.WARNING_CONFIG["rules"])):
                if topic == FastMQTT.WARNING_CONFIG["rules"][i]["topic"]:
                    rawdata = json.loads(payload)
                    for k in FastMQTT.WARNING_CONFIG["rules"][i]["monitor_key"]:
                        rawdata = rawdata[k]                  

                    result = methods(rawdata,FastMQTT.WARNING_CONFIG["rules"][i])
                    if result:
                        if topic in FastMQTT.topic_payload:
                            rawdata = FastMQTT.topic_payload[topic]
                        print("///////////////////////////////////////////\nWarning data: ",rawdata,"\ncondition: ",FastMQTT.WARNING_CONFIG["rules"][i]["condition"],"\nwarning_condition: ",FastMQTT.WARNING_CONFIG["rules"][i]["warning_condition"])
                        if type(rawdata) != list():
                            rawdata = [rawdata]
                        warning_record = {
                        "product": FastMQTT.WARNING_CONFIG["product"],
                        "project": FastMQTT.WARNING_CONFIG["project"],
                        "factory": FastMQTT.WARNING_CONFIG["factory"],
                        "floor": FastMQTT.WARNING_CONFIG["floor"],
                        "line": FastMQTT.WARNING_CONFIG["line"],
                        "cell_type": FastMQTT.WARNING_CONFIG["cell_type"],
                        "cell_id": FastMQTT.WARNING_CONFIG["cell_id"],
                        "cell_name": FastMQTT.WARNING_CONFIG["cell_name"],
                        "mac_address": FastMQTT.WARNING_CONFIG["mac_address"],
                        "ip": FastMQTT.WARNING_CONFIG["ip"],
                        "adc_daemon_port": FastMQTT.WARNING_CONFIG["adc_daemon_port"],
                        "creator": FastMQTT.WARNING_CONFIG["creator"],
                        "inform_list": FastMQTT.WARNING_CONFIG["inform_list"],
                        "rule_name": FastMQTT.WARNING_CONFIG["rules"][i]["rule_name"],
                        "create_time": FastMQTT.WARNING_CONFIG["create_time"],
                        "update_time": FastMQTT.WARNING_CONFIG["update_time"],
                        "topic": topic,
                        "warning_time": str(datetime.now()),
                        "rawdata": rawdata,
                        "silence_interval": FastMQTT.WARNING_CONFIG["rules"][i]["silence_interval"],
                        "rule": {
                            "condition": FastMQTT.WARNING_CONFIG["rules"][i]["condition"],
                            "warning_condition": FastMQTT.WARNING_CONFIG["rules"][i]["warning_condition"],
                            "monitor_key": FastMQTT.WARNING_CONFIG["rules"][i]["monitor_key"]
                            }
                        }

                        # filter warning by silence interval
                        if FastMQTT.filter_warning(FastMQTT.WARNING_CONFIG["rules"][i]["rule_name"],FastMQTT.WARNING_CONFIG["rules"][i]["silence_interval"]):

                            warning_record["records"] = FastMQTT.warning_history[FastMQTT.WARNING_CONFIG["rules"][i]["rule_name"]]["records"]
                            FastMQTT.warning_history[FastMQTT.WARNING_CONFIG["rules"][i]["rule_name"]]["records"] = 1
                            result = await post_warning_record(warning_record)
                            if result != True and FastMQTT.warning_queue.qsize() < 1000:
                                FastMQTT.warning_queue.put(warning_record)


    def filter_warning(rule_name,silence_interval):
        stamp = round(time.time())
        if silence_interval < 1:
            silence_interval = 1
        if rule_name not in FastMQTT.warning_history:
            FastMQTT.warning_history[rule_name] = {"time":stamp, "records":1}
            return True
        # elif FastMQTT.warning_history[rule_name]["times"] < 2:
        #     FastMQTT.warning_history[rule_name]["times"] += 1
        #     return False
        elif (stamp - FastMQTT.warning_history[rule_name]["time"])/60 > silence_interval:
            FastMQTT.warning_history[rule_name]["time"] = stamp
            print(True,(stamp - FastMQTT.warning_history[rule_name]["time"])/60, silence_interval)
            return True
        else:
            print(False,(stamp - FastMQTT.warning_history[rule_name]["time"])/60, silence_interval)
            FastMQTT.warning_history[rule_name]["records"] += 1
            return False


    async def check_and_update_config(): # should query db first and then read local config
        logging.info("query warning config after connection")
        # after query db for warning config
        for _ in range(3):
            try:
                res = await query_warning_config()
                if res in ["timeout", "error", None]:
                    logging.error("check station warning config from database occurs error, please check connection")
                elif res != []:
                    FastMQTT.WARNING_CONFIG = res[0]
                    FastMQTT.WARNING_CONFIG["rules"] = []
                    FastMQTT.WARNING_CONFIG["subscribed"] = []
                    FastMQTT.WARNING_CONFIG["connection"] = FastMQTT.CONNECTION
                    for i in range(len(res)):
                        for j in range(len(res[i]["rule"])):
                            tmp = res[i]["rule"][j]
                            tmp["topic"] = res[i]["topic"]
                            tmp["rule_name"] = res[i]["rule_name"]
                            tmp["silence_interval"] = res[i]["silence_interval"]
                            FastMQTT.WARNING_CONFIG["rules"].append(tmp)
                    del FastMQTT.WARNING_CONFIG["rule"]
                    del FastMQTT.WARNING_CONFIG["rule_name"]
                    del FastMQTT.WARNING_CONFIG["topic"]
                    del FastMQTT.WARNING_CONFIG["silence_interval"]
                    FastMQTT.save_config()
                    break
                elif res == []:
                    break
            except Exception as e:
                logging.error(f"request query_warning_config occurs error as: {str(e)}")
            time.sleep(1)

        logging.info(f"the latest warning config is: {FastMQTT.WARNING_CONFIG}")

        # Check for new topics to subscribe
        for i in range(len(FastMQTT.WARNING_CONFIG['rules'])):
            topic = FastMQTT.WARNING_CONFIG['rules'][i]["topic"]
            if topic not in FastMQTT.WARNING_CONFIG["subscribed"]:
                FastMQTT.instance.subscribe(topic)  # missing 3 required positional arguments: 'mid', 'qos', and 'properties'
                logging.info(f"Subscribed to topic: {topic}")
                FastMQTT.WARNING_CONFIG["subscribed"].append(topic)
        FastMQTT.save_config()
        print()


    async def reconnect():
        while FastMQTT.CONNECTION is not True:
            try:
                await FastMQTT.instance.connect(FastMQTT.MQTT_BROKER, FastMQTT.MQTT_PORT, keepalive=0)
            except Exception as e:
                logging.error(f"Can't connect to MQTT Broker:{FastMQTT.MQTT_BROKER}:{FastMQTT.MQTT_PORT} as {str(e)}")
                time.sleep(2)


    def add_event_handlers(self):
        @self.app.on_event("startup")
        async def startup_event():
            await FastMQTT.reconnect()
            ### query db for warning config
            asyncio.create_task(FastMQTT.check_and_update_config())


        @self.app.on_event("shutdown")
        async def shutdown_event():
            await self.client.disconnect()


    # def re_subscribe():
    #     while not FastMQTT.WARNING_CONFIG["connection"]:
    #         if FastMQTT.WARNING_CONFIG["connection"]:
    #             print("=================== re_subscribe")
    #             for i in range(len(FastMQTT.WARNING_CONFIG["rules"])):
    #                 topic = FastMQTT.WARNING_CONFIG["rules"][i]["topic"]
    #                 FastMQTT.instance.subscribe(topic)
    #                 if topic not in FastMQTT.WARNING_CONFIG["subscribed"]:
    #                     FastMQTT.WARNING_CONFIG["subscribed"].append(topic)
    #             FastMQTT.save_config()
    #         else:
    #             logging.error("Can't connect to MQTT broker")
    #             time.sleep(5)


    def unsubscribe(topics: list):
        if FastMQTT.WARNING_CONFIG["connection"]:
            logging.info(f"unsubscribe: {topics}")

            for topic in topics:
                FastMQTT.WARNING_CONFIG["subscribed"].remove(topic)
                FastMQTT.instance.unsubscribe(topic)
            FastMQTT.save_config()
        else:
            logging.error("can't connect to MQTT broker")