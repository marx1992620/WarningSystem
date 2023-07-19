import logging
import time
import json
from json import loads, dump
from utils import utils
from core.settings import AppSettings, Warning
from api.request import  post_warning_record
from fastapi_mqtt.fast_mqtt import FastMQTT


def add_scheduler_task(scheduler):
    @scheduler.scheduled_job(trigger="interval", seconds=15)
    async def check_mqtt_connection_schedule():
        await FastMQTT.reconnect()

    # @scheduler.scheduled_job(trigger="interval", minutes=FastMQTT.screen_interval)
    # async def clean_warning_history():
    #     FastMQTT.warning_history = {}

    @scheduler.scheduled_job(trigger="interval", seconds=20)
    async def check_network_connection_schedule():
        # try to connect to server with previous ip
        if Warning.ip:
            connect_to_django = await utils.check_reachable(Warning.ip, AppSettings.Django_IP,
                                                              AppSettings.Django_PORT)
            connect_to_ui = await utils.check_reachable(Warning.ip, AppSettings.UI_IP,
                                                                   AppSettings.UI_PORT)
        else:
            connect_to_django = False
            connect_to_ui = False

        if Warning.ip is None or connect_to_django == False or connect_to_ui == False:
            Warning.connection = False
            ips = await utils.get_ips()

            for current_ip in ips:
                # connect to django
                connect_to_django = await utils.check_reachable(current_ip, AppSettings.Django_IP,
                                                                  AppSettings.Django_PORT)
                if not connect_to_django:
                    logging.info(
                        f"Can't connect to Django: {AppSettings.Django_IP}:{AppSettings.Django_PORT} with ip: {current_ip}")
                    continue
                else:
                    logging.info(
                        f"Connect to Django: {AppSettings.Django_IP}:{AppSettings.Django_PORT} with ip: {current_ip}")
                
                # connect to ui
                connect_to_ui = await utils.check_reachable(current_ip, AppSettings.UI_IP,
                                                                   AppSettings.UI_PORT)
                if not connect_to_ui:
                    logging.info(
                        f"Can't connect to UI: {AppSettings.UI_IP}:{AppSettings.UI_PORT} with ip: {current_ip}")
                    continue
                else:
                    logging.info(
                        f"Connect to UI: {AppSettings.UI_IP}:{AppSettings.UI_PORT} with ip: {current_ip}")

                current_mac_addr = utils.get_mac_address(current_ip)

                if Warning.ip == current_ip and Warning.mac_address == current_mac_addr:
                    continue

                logging.info(f"ip address changed from {Warning.ip} to {current_ip}")
                logging.info(f"mac address {current_mac_addr}")
                Warning.ip = current_ip
                Warning.mac_address = current_mac_addr
        else:
            if Warning.connection == False:
                Warning.connection = True
                await FastMQTT.check_and_update_config()

                while FastMQTT.warning_queue.empty() is False:
                    warning_record = FastMQTT.warning_queue.get()
                    result = await post_warning_record(warning_record)
                    time.sleep(0.5)

        if (connect_to_django != Warning.connect_to_django or connect_to_ui != Warning.connect_to_ui):
            Warning.connect_to_django = connect_to_django
            Warning.connect_to_ui = connect_to_ui
            Warning.save_config()

