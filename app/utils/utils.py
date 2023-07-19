import asyncio
import os
import time
import netifaces
import logging
from core.settings import AppSettings, Warning
from datetime import datetime
from json import dump, loads


async def check_reachable(local_addr: str, remote_addr: str, remote_port: int, duration: float = 3, delay: float = 0.1):
    """
    Asynchornize function to check local host addrs can reach remote host.
    """
    tmax = time.time() + duration
    while time.time() < tmax:
        try:
            fut = asyncio.open_connection(
                remote_addr, remote_port, local_addr=(local_addr, 0))
            _reader, writer = await asyncio.wait_for(fut, timeout=1)
            writer.close()
            await writer.wait_closed()

            return True
        except:
            if delay:
                await asyncio.sleep(delay)
    return False


async def get_ips():
    """
    Asynchornize function to get local ip addr
    """
    ips = []
    for nic in netifaces.interfaces():
        addrs = netifaces.ifaddresses(nic)
        try:
            ip = addrs[netifaces.AF_INET][0]["addr"]
            if ip != "127.0.0.1":
                ips.append(ip)
        except:
            pass
    return ips


def get_mac_address(ip: str):
    for nic in netifaces.interfaces():
        addrs = netifaces.ifaddresses(nic)
        try:
            if ip == addrs[netifaces.AF_INET][0]["addr"]:
                mac_addr = addrs[netifaces.AF_LINK][0]["addr"]
                return mac_addr
        except:
            pass



