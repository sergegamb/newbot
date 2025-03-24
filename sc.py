import json
import os

import requests as rq

from models import Request
from admin import TECHNICIANS, GROUPS


ROW_COUNT = 7


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
        requests = requests_json.get("requests")[:ROW_COUNT]
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
        return Request(**request)
    except Exception as e:
        print(f"Error during request: {e}")
        return None


def list(list_info):
    try:
        url = os.environ["API_URL"] + "/requests"
        headers = {"authtoken" : os.environ["AUTH_TOKEN"]}
        params = {"input_data": json.dumps(list_info)}
        requests_json = rq.get(url, headers=headers, params=params, verify=False).json()
        response_status = requests_json.get("status")
        list_info = requests_json.get("list_info")
        requests = requests_json.get("requests")
        for request in requests:
            yield Request(**request)
    except Exception as e:
        print(f"Error during request: {e}")
        return None


def list_last(page=0):
    list_info = {
        "row_count": ROW_COUNT,
        "start_index": 1 + page * ROW_COUNT,
    }
    list_info = {
        "list_info": list_info
    }
    return list(list_info)


def list_technician(technician_id, page=0):
    list_info = {
        "row_count": ROW_COUNT,
        "start_index": 1 + page * ROW_COUNT,
    }
    status_not_compleate = {
        "field": "status.name",
        "condition": "is not",
        "value": "Выполнена",
        "logical_operator": "AND"
    }
    status_not_canceled = {
        "field": "status.name",
        "condition": "is not",
        "value": "Отменена",
        "logical_operator": "AND"
    }
    status_not_closed = {
        "field": "status.name",
        "condition": "is not",
        "value": "Закрыта",
        "logical_operator": "AND"
    }
    status_exclude = [status_not_closed, status_not_canceled, status_not_compleate]
    search_criteria = {
        "field": "technician.name",
        "condition": "is",
        "value": TECHNICIANS[technician_id],
        "children": status_exclude
    }
    search_criteria = {"search_criteria": search_criteria}
    list_info.update(search_criteria)
    list_info = {"list_info": list_info}
    return list(list_info)


def list_technician_group(technician_id, page=0):
    list_info = {
        "row_count": ROW_COUNT,
        "start_index": 1 + page * ROW_COUNT,
    }
    search_criteria = {
        "field": "group.name",
        "condition": "is",
        "values": GROUPS[TECHNICIANS[technician_id]]
    }
    search_criteria = {"search_criteria": search_criteria}
    list_info.update(search_criteria)
    list_info = {"list_info": list_info}
    return list(list_info)


if __name__ == "__main__":
    pass