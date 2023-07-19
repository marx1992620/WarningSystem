from schedule.scheduler import asyncScheduler
import logging


async def start_scheduler():
    """

    """
    logging.debug("Start scheduler")
    asyncScheduler.start()


async def stop_scheduler():
    """

    """
    logging.debug("Stop scheduler")
    asyncScheduler.shutdown()
