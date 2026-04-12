import hashlib
import hmac
import urllib.parse
from datetime import datetime


class VNPayGateway:
    def __init__(self, app):
        self.tmn_code = app.config.get("VNPAY_TMN_CODE", "")
        self.hash_secret = app.config.get("VNPAY_HASH_SECRET", "")
        self.payment_url = app.config.get("VNPAY_PAYMENT_URL", "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html")
        self.return_url = app.config.get("VNPAY_RETURN_URL", "")

    def create_payment_url(self, txn_ref, amount, order_info, ip_addr="127.0.0.1", return_url=None):
        amount_vnd = int(float(amount) * 100)
        resolved_return_url = return_url or self.return_url
        payment_data = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": self.tmn_code,
            "vnp_Amount": str(amount_vnd),
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": txn_ref,
            "vnp_OrderInfo": order_info,
            "vnp_OrderType": "billpayment",
            "vnp_Locale": "vn",
            "vnp_ReturnUrl": resolved_return_url,
            "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S"),
            "vnp_IpAddr": ip_addr,
        }

        sorted_data = sorted(payment_data.items())
        query = urllib.parse.urlencode(sorted_data)
        secure_hash = hmac.new(
            self.hash_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha512,
        ).hexdigest()
        return f"{self.payment_url}?{query}&vnp_SecureHash={secure_hash}"

    def verify_callback(self, callback_data):
        received_hash = callback_data.get("vnp_SecureHash")
        if not received_hash:
            return False

        data_to_verify = {
            k: v
            for k, v in callback_data.items()
            if k not in {"vnp_SecureHash", "vnp_SecureHashType"}
        }
        sorted_data = sorted(data_to_verify.items())
        query = urllib.parse.urlencode(sorted_data)
        expected_hash = hmac.new(
            self.hash_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha512,
        ).hexdigest()
        return hmac.compare_digest(received_hash, expected_hash)

