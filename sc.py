import os

import requests as rq

from models import Request


def get_last_requests(url):
    try:
        url = url + "/requests"
        headers = {"authtoken" : os.environ["AUTH_TOKEN"]}
        response = rq.get(url, headers=headers, verify=False)
        return response.json()
    except rq.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None
    

def index():
    try:
        requests_json = get_last_requests(os.environ["API_URL"])
        response_status = requests_json.get("status")
        list_info = requests_json.get("list_info")
        requests = requests_json.get("requests")
        for request in requests:
            yield Request(**request)
    except Exception as e:
        print(f"Error during request: {e}")
        return None
        

def get_request(request_id: int):
    try:
        url = os.environ["API_URL"] + f"/requests/{request_id}"
        headers = {"authtoken" : os.environ["AUTH_TOKEN"]}
        response = rq.get(url, headers=headers, verify=False)
        return response.json()
    except:
        print("Error during request")
        return None


def show(request_id: int):
    try:
        request_json = get_request(request_id)
        response_status = request_json.get("status")
        list_info = request_json.get("list_info")
        request = request_json.get("request")
        # print(request)
        return Request(**request)
    except Exception as e:
        print(f"Error during request: {e}")
        return None


if __name__ == "__main__":
    r = show(5043)
    print(r)