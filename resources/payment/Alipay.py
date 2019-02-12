import json
from base64 import encodebytes, decodebytes
from datetime import datetime
from urllib.parse import quote_plus

import requests
from Cryptodome.Hash import SHA256, SHA
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5
from django.conf import settings

from resources.payment.PayException import AlipayException, AliPayValidationException


class Alipay():
    def __init__(self, appid, app_notify_url=None, app_private_key_path=None, alipay_public_key_path=None,
                 sign_type="RSA2", debug=False):
        super(Alipay, self).__init__()
        self._support_sign_type = ["RSA", "RSA2"]
        self._app_id = str(appid)
        self._app_notify_url = app_notify_url
        self._app_private_key_path = app_private_key_path
        self._alipay_public_key_path = alipay_public_key_path
        self._app_private_key_string = ""
        self._alipay_public_key_string = ""
        if sign_type not in self._support_sign_type:
            raise AlipayException("Only support RSA and RSA2")
        self._sign_type = sign_type
        self._debug = debug
        if self._debug is True:
            self._gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self._gateway = "https://openapi.alipay.com/gateway.do"
        self._async_function = ["alipay.trade.app.pay", "alipay.trade.wap.pay", "alipay.trade.page.pay",
                                "alipay.trade.pay", "alipay.trade.precreate"]
        # load key file immediately
        self._load_key()

    def _load_key(self):
        content = self._app_private_key_string
        if not content:
            with open(self._app_private_key_path) as f:
                content = f.read()
        self._app_private_key = RSA.importKey(content)
        # load public key
        content = self._alipay_public_key_string
        if not content:
            with open(self._alipay_public_key_path) as f:
                content = f.read()
        self._alipay_public_key = RSA.importKey(content)

    def _sign(self, unsigned_string):
        key = self._app_private_key
        signer = PKCS1_v1_5.new(key)
        if self._sign_type == "RSA":
            signature = signer.sign(SHA.new(unsigned_string.encode("utf-8")))
        else:
            signature = signer.sign(SHA256.new(unsigned_string.encode("utf-8")))
            # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def _build_request_body(self, method, biz_content, append_auth_token=None, return_url=None, notify_url=None):
        data = {
            "app_id": self._app_id,
            "method": method,
            "format": "json",
            "charset": "utf-8",
            "sign_type": self._sign_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }
        if append_auth_token:
            data["app_auth_token"] = self.app_auth_token

        if return_url is not None:
            data["return_url"] = return_url

        if method in self._async_function:
            data["notify_url"] = notify_url or self._app_notify_url

        return data

    def _resort_data(self, data):
        complex_keys = [k for k, v in data.items() if isinstance(v, dict)]
        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def _sign_data(self, data):
        data.pop("sign", None)
        # 排序后的字符串
        ordered_items = self._resort_data(data)
        unsigned_string = "&".join("{}={}".format(k, v) for k, v in ordered_items)
        sign = self._sign(unsigned_string)
        quoted_string = "&".join("{}={}".format(k, quote_plus(v)) for k, v in ordered_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def _verify_and_return_sync_response(self, response, response_type):
        # raise exceptions
        result = response[response_type]
        if settings.DEBUG:
            response['sign'] = 'sign'
        if "sign" not in response.keys():
            raise AlipayException(
                msg=result.get('message')
            )
        sign = response["sign"]

        if not (self._verify(json.dumps(result), sign) or settings.DEBUG):
            raise AliPayValidationException
        result['api_name'] = response_type
        result['sign'] = sign
        result['message'] = result['msg']
        return result

    def _verify(self, raw_content, signature):
        # 开始计算签名
        key = self._alipay_public_key
        signer = PKCS1_v1_5.new(key)
        if self._sign_type == "RSA":
            digest = SHA.new()
        else:
            digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def alipay_trade_create(self, total_amount, out_trade_no, subject, **kwargs):
        if not all([out_trade_no, total_amount, subject]):
            raise AlipayException("out_trade_no, total_amount and subject are required.")
        _method = "alipay.trade.create"
        kwargs["out_trade_no"] = out_trade_no
        kwargs["total_amount"] = total_amount
        kwargs["subject"] = subject

        data = self._build_request_body(_method, kwargs)
        url = "{}?{}".format(self._gateway, self._sign_data(data))
        # raw_string = urlopen(url, timeout=15).read().decode("utf-8")
        raw_string = requests.get(url)
        return self._verify_and_return_sync_response(raw_string.json(), "alipay_trade_create_response")
