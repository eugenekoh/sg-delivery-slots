import pushover
from loguru import logger
from api_client import APIClient


class SlotTracker:
    def __init__(self, postal_code, api_token, user_key):
        self._pushover_client = pushover.Client(user_key, api_token=api_token)
        self._api_client = APIClient()
        self._postal_code = postal_code

        self._setup_logs()
        self._pushover_client.send_message(f"Tracking delivery slots for postal code : {self._postal_code}")

    def _setup_logs(self):
        logger.add("delivery.log")
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


