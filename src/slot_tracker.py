from collections import defaultdict
from datetime import datetime

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
        logger.add("../logs/file_{time}.log", rotation="23:59", retention="5 days")
        logger.add(lambda msg: self._pushover_client.send_message(msg), level="ERROR")
        logger.info("starting delivery tracking")

    @logger.catch()
    def check_slots(self):
        logger.info("checking slots")

        stores = {
            "fairprice": self._api_client.get_fairprice_slots(self._postal_code),
            "cold storage": self.get_coldstorage_slots(),
            "giant": self.get_giant_slots(),
        }

        logger.info(f"availability: {stores}")
        avail_stores = {k: v for k, v in stores.items() if v}

        if avail_stores:
            message = f"Available\n : {avail_stores}"

            logger.debug(message)

            self._pushover_client.send_message(message)

    def get_coldstorage_slots(self):
        time_slots = self._api_client.get_coldstorage_slots(self._postal_code)

        return self.parse_gcs_timeslots(time_slots)

    def get_giant_slots(self):
        time_slots = self._api_client.get_giant_slots(self._postal_code)

        return self.parse_gcs_timeslots(time_slots)

    def parse_gcs_timeslots(self, time_slots):
        available_slots = defaultdict(list)
        for day, day_slots in time_slots.items():
            day = datetime.strptime(day, "%Y-%m-%d")
            day_formatted_str = day.strftime("%A , %d %B %Y")
            for hour_slot, details in day_slots.items():
                if details["available"]:
                    available_slots[day_formatted_str].append(details["label"])

        return dict(available_slots)
