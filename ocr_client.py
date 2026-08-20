import time
import json
import hmac
import base64
import hashlib
import requests


class OcrInterface:

    def __init__(self):
        self.ocr_url = 'http://10.33.111.33:8080/service'
        self.request_id = 'test'
        self.uuid = 'test'
        self.appid = 'hiai'
        self.bid = 'test_focusocr_fun'
        self.flowid = 'test_focusocr_fun'
        self.language = 'AUTO'
        self.shape = 'curve_enable'

        self.sign_key = 'CB663177458347D19A07D03E7728C878D1C413811F0C4526AEDD26DDD4334980'

        self.language_map = {
            'AUTO': '0',
            'CHINESE': '1',
            'SPANISH': '2',
            'ENGLISH': '3',
            'PORTUGUESE': '4',
            'ITALIAN': '5',
            'GERMAN': '6',
            'FRENCH': '7',
            'RUSSIAN': '8',
            'JAPANESE': '9',
            'KOREAN': '10'
        }


    def get_ocr(self, image_base64):

        request_data = {
            'image': image_base64,
            'ocrLanguage': self.language_map[self.language],
            'textShape': self.shape,
            'requestId': self.request_id,
            'deviceId': 'grey',
            'timeZone': 'timeZone',
            'time': 'time',
            'language': 'language',
            'ext': 'ext',
            'resize': 'False',
            'enableFilter': 'False'
        }

        return self._ocr_post(request_data)


    def _get_sign(self):

        timestamp = int(time.time() * 1000)

        sign_str = (
            f'POST&/service&&'
            f'&appid={self.appid}'
            f'&timestamp={timestamp}'
        )

        sign = base64.b64encode(
            hmac.new(
                self.sign_key.encode("utf-8"),
                sign_str.encode("utf-8"),
                hashlib.sha256
            ).digest()
        ).decode("utf-8")

        return timestamp, sign


    def _ocr_post(self, request_data):

        timestamp, sign = self._get_sign()

        payload = {
            "data": request_data,
            "meta": {
                "subId": "2",
                "bId": self.bid,
                "flowId": self.flowid,
                "uuId": self.uuid
            },
            "version": "1.2"
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization":
                f'CLOUDSOA-HMAC-SHA256 '
                f'appid={self.appid}, '
                f'timestamp={timestamp}, '
                f'signmode=easy, '
                f'signature="{sign}"'
        }

        response = requests.post(
            self.ocr_url,
            json=payload,
            headers=headers
        )

        response.raise_for_status()

        result = response.json()

        if result["result"]["code"] != "0":
            return {}

        content = result["result"]["content"][0]

        if isinstance(content, str):
            return json.loads(content)

        return content