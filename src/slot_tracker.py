import time

import pushover
from settings import USER_KEY, API_TOKEN, POSTAL_CODE
import schedule
from loguru import logger
from api_client import APIClient


class SlotTracker:
    def __init__(self):

        self._pushover_client = pushover.Client(USER_KEY, api_token=API_TOKEN)
        self._postal_code = int(POSTAL_CODE)
        self._api_client = APIClient()
        self._pushover_client.send_message(f"Tracking delivery slots for postal code :{self._postal_code}")

        logger.add(f"../delivery.log")
        logger.add(lambda msg: self._pushover_client.send_message(msg), level="ERROR")
        logger.info("starting delivery tracking")

    @logger.catch()
    def check_slots(self):
        logger.info("checking slots")

        stores = {
            "fairprice": self._api_client.get_fairprice_avail(self._postal_code),
            "cold storage": self._api_client.get_coldstorage_avail(self._postal_code),
            "giant": self._api_client.get_giant_avail(self._postal_code),
        }

        logger.info(f"availability: {stores}")
        avail_stores = {k: v for k, v in stores.items() if v}

        if avail_stores:
            message = f"Delivery slots available at : {list(avail_stores.keys())}"

            logger.debug(message)

            self._pushover_client.send_message(message)


if __name__ == '__main__':

    st = SlotTracker()
    st.check_slots()

    schedule.every(5).minutes.do(st.check_slots)

    while True:
        schedule.run_pending()
        time.sleep(1)
