from fastapi import APIRouter, status
from fastapi_mqtt.fast_mqtt import FastMQTT
from fastapi.responses import JSONResponse
import logging
import traceback


router = APIRouter()

@router.post("/create_warning", status_code=status.HTTP_201_CREATED)
async def create_warning(items: list):
    """
    To create new rule_name
    Required parameters: rule_name, rule, topic
    """
    try:
        FastMQTT.WARNING_CONFIG = {"rules":[],"subscribed":[],"connection":FastMQTT.CONNECTION}
        for item in items:

            FastMQTT.WARNING_CONFIG["product"] = item["product"]
            FastMQTT.WARNING_CONFIG["project"] = item["project"]
            FastMQTT.WARNING_CONFIG["factory"] = item["factory"]
            FastMQTT.WARNING_CONFIG["floor"] = item["floor"]
            FastMQTT.WARNING_CONFIG["line"] = item["line"]
            FastMQTT.WARNING_CONFIG["cell_type"] = item["cell_type"]
            FastMQTT.WARNING_CONFIG["cell_id"] = item["cell_id"]
            FastMQTT.WARNING_CONFIG["cell_name"] = item["cell_name"]
            FastMQTT.WARNING_CONFIG["mac_address"] = item["mac_address"]
            FastMQTT.WARNING_CONFIG["ip"] = item["ip"]
            FastMQTT.WARNING_CONFIG["adc_daemon_port"] = item["adc_daemon_port"]
            FastMQTT.WARNING_CONFIG["creator"] = item["creator"]
            FastMQTT.WARNING_CONFIG["inform_list"] = item["inform_list"]
            FastMQTT.WARNING_CONFIG["create_time"] = item["create_time"]
            FastMQTT.WARNING_CONFIG["update_time"] = item["update_time"]

            for j in range(len(item["rule"])):
                tmp = item["rule"][j]
                tmp["topic"] = item["topic"]
                tmp["rule_name"] = item["rule_name"]
                tmp["silence_interval"] = item["silence_interval"]
                FastMQTT.WARNING_CONFIG["rules"].append(tmp)

            if item["topic"] not in FastMQTT.WARNING_CONFIG["subscribed"]:
                FastMQTT.instance.subscribe(item["topic"])
                FastMQTT.WARNING_CONFIG["subscribed"].append(item["topic"])

        FastMQTT.save_config()
        status_code = status.HTTP_200_OK
        logging.info(f"create warning config: {items}")
        return JSONResponse({"message": "create warning config success"}, status_code=status_code)
    except Exception as e:
        logging.error(str(traceback.print_exc()))
        return JSONResponse({"error message": {e}})


@router.delete("/delete_warning", status_code=status.HTTP_201_CREATED)
async def delete_warning(items: list):
    """
    To delete rule_name
    Required parameters: rule_name
    """
    try:
        rm_rule_lis = []
        unsubcribe_lis = []
        for item in items:
            for each_rule in FastMQTT.WARNING_CONFIG["rules"]:
                if each_rule["rule_name"] == item["rule_name"]:
                    rm_rule_lis.append(each_rule)

        for rule in rm_rule_lis:
            FastMQTT.WARNING_CONFIG["rules"].remove(rule)
            logging.info(f"remove rule: {rule}")

        all_topics = [ rule["topic"] for rule in FastMQTT.WARNING_CONFIG["rules"]]

        for topic in FastMQTT.WARNING_CONFIG["subscribed"]:
            if topic not in all_topics:
                unsubcribe_lis.append(topic)
        if len(unsubcribe_lis) > 0 :
            FastMQTT.unsubscribe(unsubcribe_lis)

        FastMQTT.save_config()
        status_code = status.HTTP_200_OK
        logging.info(f"delete warning config: {items}")
        return JSONResponse({"message": "delete warning config success"}, status_code=status_code)
    except Exception as e:
        logging.error(str(traceback.print_exc()))
        return JSONResponse({"error message": {e}})


@router.patch("/update_warning", status_code=status.HTTP_201_CREATED)
async def tt(items: list):
    """
    To modify data of rule_name
    Required parameters: rule_name, rule, topic
    """
    try: 
        rm_rule_lis = []
        unsubcribe_lis = []
        # remove rule of config by rule_name
        for item in items:
            for each_rule in FastMQTT.WARNING_CONFIG["rules"]:
                if each_rule["rule_name"] == item["rule_name"]:
                    rm_rule_lis.append(each_rule)
        for rule in rm_rule_lis:
            FastMQTT.WARNING_CONFIG["rules"].remove(rule)
            logging.info(f"remove rule: {rule}")

        # add rule into config
        for item in items:
            FastMQTT.WARNING_CONFIG["product"] = item.get("product",FastMQTT.WARNING_CONFIG["product"])
            FastMQTT.WARNING_CONFIG["project"] = item.get("project",FastMQTT.WARNING_CONFIG["project"])
            FastMQTT.WARNING_CONFIG["factory"] = item.get("factory",FastMQTT.WARNING_CONFIG["factory"])
            FastMQTT.WARNING_CONFIG["floor"] = item.get("floor",FastMQTT.WARNING_CONFIG["floor"])
            FastMQTT.WARNING_CONFIG["line"] = item.get("line",FastMQTT.WARNING_CONFIG["line"])
            FastMQTT.WARNING_CONFIG["cell_type"] = item.get("cell_type",FastMQTT.WARNING_CONFIG["cell_type"])
            FastMQTT.WARNING_CONFIG["cell_id"] = item.get("cell_id",FastMQTT.WARNING_CONFIG["cell_id"])
            FastMQTT.WARNING_CONFIG["cell_name"] = item.get("cell_name",FastMQTT.WARNING_CONFIG["cell_name"])
            FastMQTT.WARNING_CONFIG["mac_address"] = item.get("mac_address",FastMQTT.WARNING_CONFIG["mac_address"])
            FastMQTT.WARNING_CONFIG["ip"] = item.get("ip",FastMQTT.WARNING_CONFIG["ip"])
            FastMQTT.WARNING_CONFIG["adc_daemon_port"] = item.get("adc_daemon_port",FastMQTT.WARNING_CONFIG["adc_daemon_port"])
            FastMQTT.WARNING_CONFIG["creator"] = item.get("creator",FastMQTT.WARNING_CONFIG["creator"])
            FastMQTT.WARNING_CONFIG["inform_list"] = item.get("inform_list",FastMQTT.WARNING_CONFIG["inform_list"])
            FastMQTT.WARNING_CONFIG["create_time"] = item.get("create_time",FastMQTT.WARNING_CONFIG["create_time"])
            FastMQTT.WARNING_CONFIG["update_time"] = item.get("update_time",FastMQTT.WARNING_CONFIG["update_time"])

            for j in range(len(item["rule"])):
                tmp = item["rule"][j]
                tmp["topic"] = item["topic"]
                tmp["rule_name"] = item["rule_name"]
                tmp["silence_interval"] = item["silence_interval"]
                FastMQTT.WARNING_CONFIG["rules"].append(tmp)

            if item["topic"] not in FastMQTT.WARNING_CONFIG["subscribed"]:
                FastMQTT.instance.subscribe(item["topic"])
                FastMQTT.WARNING_CONFIG["subscribed"].append(item["topic"])

        all_topics = [ rule["topic"] for rule in FastMQTT.WARNING_CONFIG["rules"]]

        for topic in FastMQTT.WARNING_CONFIG["subscribed"]:
            if topic not in all_topics:
                unsubcribe_lis.append(topic)
        if len(unsubcribe_lis) > 0 :
            FastMQTT.unsubscribe(unsubcribe_lis)

        FastMQTT.save_config()
        status_code = status.HTTP_200_OK
        logging.info(f"update warning config: {items}")
        return JSONResponse({"message": "update warning config success"}, status_code=status_code)
    except Exception as e:
        logging.error(str(traceback.print_exc()))
        return JSONResponse({"error message": {e}})


