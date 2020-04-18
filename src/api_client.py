import requests
from loguru import logger
from fake_useragent import UserAgent

class APIClient:
    MAX_RETRIES = 5
    TIMEOUT = 10

    FAIPRICE_HOST = "website-api.omni.fairprice.com.sg"
    FAIRPRICE_STOREID_URL = f"https://{FAIPRICE_HOST}/api/serviceable-area"
    FAIRPRICE_AVAIL_URL = f"https://{FAIPRICE_HOST}/api/slot-availability"

    GIANT_HOST = "giant.sg"
    GIANT_URL = f"https://{GIANT_HOST}/checkout/cart/checkdelivery"

    COLDSTORAGE_HOST = "coldstorage.com.sg"
    COLDSTORAGE_URL = f"https://{COLDSTORAGE_HOST}/checkout/cart/checkdelivery"

    def __init__(self):
        self._ua = UserAgent()

    def _send_request(self, method, url, **kwargs):
        headers = {
            "Connection": "keep-alive",
            "Accept": "*/*",
            "Accept-Language": "en",
            "User-Agent": self._ua.random,
            "Accept-Encoding": "gzip, deflate, br"
        }

        kwargs["headers"].update(headers)
        response = requests.request(method, url, timeout=APIClient.TIMEOUT, **kwargs)
        response.raise_for_status()

        response_json = response.json()
        return response_json

    def get_fairprice_avail(self, postal_code):
        headers = {
            "Host" : APIClient.FAIPRICE_HOST
        }

        # retrieve store id
        params = {"pincode": postal_code}
        response = self._send_request("GET", APIClient.FAIRPRICE_STOREID_URL, headers=headers, params=params)

        logger.debug(f"fairprice storeid response : {response}")

        store_id = response["data"]["store"]["id"]

        # check availability of store
        params = {"storeId": store_id}
        response = self._send_request("GET", APIClient.FAIRPRICE_AVAIL_URL, headers=headers, params=params)

        logger.debug(f"fairprice availability response : {response}")

        return response["data"]["available"]

    def get_giant_avail(self, postal_code):
        headers = {
            "Host" : APIClient.GIANT_HOST
        }

        params = {"postal_code": postal_code}
        response = self._send_request("POST", APIClient.GIANT_URL, headers=headers, data=params)

        logger.debug(f"giant availability response : {response}")

        return True if response["earliest"] else False

    def get_coldstorage_avail(self, postal_code):
        headers = {
            "Host" : APIClient.COLDSTORAGE_HOST
        }

        params = {"postal_code": postal_code}
        response = self._send_request("POST", APIClient.COLDSTORAGE_URL, headers=headers, data=params)

        logger.debug(f"cold storage availability response : {response}")

        return True if response["earliest"] else False

