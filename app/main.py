from fastapi import FastAPI
from utils import utils
from fastapi_mqtt.fast_mqtt import FastMQTT
from fastapi.middleware.cors import CORSMiddleware
from schedule.events import start_scheduler, stop_scheduler
from schedule.task import add_scheduler_task
from schedule.scheduler import asyncScheduler
from api import warning_config
from core.settings import AppSettings, Warning
import time
import logging



async def init_setting():
    logging.info("init to check connection with django and ui")
    connect_to_django = False
    connect_to_ui = False
    while connect_to_django == False or connect_to_ui == False:

        if Warning.ip is None or connect_to_django == False or connect_to_ui == False:
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
                Warning.ip = current_ip
                Warning.mac_address = current_mac_addr

                if Warning.ip != None and connect_to_django == True and connect_to_ui == True:
                    break
        time.sleep(0.1)
    if (connect_to_django != Warning.connect_to_django or connect_to_ui != Warning.connect_to_ui):
        Warning.connect_to_django = connect_to_django
        Warning.connect_to_ui = connect_to_ui
        Warning.connection = True
        Warning.save_config()


def get_application() -> FastAPI:

    application = FastAPI()
    origins = ["*"]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_event_handler("startup", init_setting)
    application.add_event_handler("startup", start_scheduler)
    application.add_event_handler("shutdown", stop_scheduler)
    add_scheduler_task(asyncScheduler)

    mqtt_service = FastMQTT(application)
    mqtt_service.add_event_handlers()

    application.include_router(warning_config.router)

    return application

app = get_application()


# Startup event
# @app.on_event("startup")
# async def startup_event():
    # current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    # with open(os.path.join(current_dir,"core","setting.json"))as f:
    #     settings = json.loads(f.read())
    # print(settings)
    # with open(settings["STATION_INFO_DIR"])as f:
    #     station_info = json.loads(f.read())
    # print(station_info)
    # print("Application started")

# # Shutdown event
# @app.on_event("shutdown")
# async def shutdown_event():
#     # Perform shutdown operations here
#     print("Application shutting down")

# # Root route
# @app.get("/")
# def read_root():
#     return {"Hello": "World"}