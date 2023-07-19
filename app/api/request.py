import aiohttp
import asyncio
import logging
import traceback
from urllib.parse import urljoin
from core.settings import AppSettings, Warning


Django_BASE_URL = f"http://{AppSettings.Django_IP}:{AppSettings.Django_PORT}"

async def query_warning_config():
    Django_BASE_URL = "http://172.28.146.46:8013"  # test mode
    request_url = urljoin(Django_BASE_URL, f"/api/warning_config/{Warning.mac_address}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(request_url, timeout=AppSettings.QUERY_REQUEST_TIMEOUT) as resp:

                if resp.status == 200:
                    res = await resp.json()
                    return res
                else:
                    error_description = await resp.text()
                    logging.error(f"[HTTP] Requests query_warning_config return : {resp.status} {error_description}")
                    return "error"

    except asyncio.TimeoutError:
        logging.error("[HTTP] Requests query_warning_config occurs timeout.")
        return "timeout"
    except Exception as e:
        logging.error(f"[HTTP] Requests query_warning_config occurs error as {str(e)}")
        logging.error(str(traceback.print_exc()))
        return "error"


async def post_warning_record(warning_record):
    Django_BASE_URL = "http://172.28.146.46:8013"
    request_url = urljoin(Django_BASE_URL, f"/api/warning_record")
    try:
        cell_info = warning_record
        async with aiohttp.ClientSession() as session:
            async with session.post(request_url, timeout=AppSettings.QUERY_REQUEST_TIMEOUT, json=cell_info) as resp:
                logging.info(f'[response status code]: {resp.status}')
                logging.info(f'[response text]: {await resp.text()}')
                if resp.status == 201:
                    return True
                else:
                    error_description = await resp.json()
                    logging.error(f"[HTTP] Requests post_warning_data return : {resp.status} {error_description}")
                    return False

    except asyncio.TimeoutError:
        logging.error("[HTTP] Requests post_warning_data occurs timeout.")
        return "timeout"
    except Exception as e:
        logging.error(f"[HTTP] Requests post_warning_data occurs error as {str(e)}")
        logging.error(str(traceback.print_exc()))
        return "error"
