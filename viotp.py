import requests
from config import VIOTP_TOKEN, BASE_URL

def get_balance():
    return requests.get(f"{BASE_URL}/users/balance", params={"token": VIOTP_TOKEN}).json()

def get_services():
    return requests.get(f"{BASE_URL}/service/getv2", params={"token": VIOTP_TOKEN, "country": "vn"}).json()

def rent_sim(service_id):
    return requests.get(f"{BASE_URL}/request/getv2", params={"token": VIOTP_TOKEN, "serviceId": service_id}).json()

def get_otp(request_id):
    return requests.get(f"{BASE_URL}/session/getv2", params={"token": VIOTP_TOKEN, "requestId": request_id}).json()
