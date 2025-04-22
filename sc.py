import json
import os

import requests as rq

from models import Request, Conversation, Notification, Task, Worklog
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
        request_json = response.json()
        response_status = request_json.get("status")
        list_info = request_json.get("list_info")
        request = request_json.get("request")
        return Request(**request)
    except Exception as e:
        print(f"Error during request: {e}")
        return None


def list_requests(list_info):
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


def list_all_requests(page=0):
    list_info = {
        "row_count": ROW_COUNT,
        "start_index": 1 + page * ROW_COUNT,
    }
    list_info = {
        "list_info": list_info
    }
    return list_requests(list_info)


def list_technician_pending_requests(technician_id, page=0):
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
    return list_requests(list_info)


def list_technician_group_requests(technician_id, page=0):
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
    return list_requests(list_info)


def get_request_conversation(request_id):
    try:
        url = os.environ["API_URL"] + f"/requests/{request_id}/conversations"
        headers = {"authtoken" : os.environ["AUTH_TOKEN"]}
        conversations_json = rq.get(url, headers=headers, verify=False).json()
        response_status = conversations_json.get("request_status")
        list_info = conversations_json.get("list_info")
        conversations = conversations_json.get("conversations")
        for conversation in conversations:
            yield Conversation(**conversation)
    except Exception as e:
        print(f"Error during request: {e}")
        return None


def view_notification(request_id, notification_id) -> Notification:
    try:
        url = os.environ["API_URL"] + f"/requests/{request_id}/notifications/{notification_id}"
        headers = {"authtoken" : os.environ["AUTH_TOKEN"]}
        notification_json = rq.get(url, headers=headers, verify=False).json()
        notification = notification_json.get("notification")
        return Notification(**notification)
    except Exception as e:
        print(f"Error during request: {e}")
        return None


def add_task(request_id, technician, title, due_date):
    task = {
        "task": {
            "title": title,
            "owner": {
                "name": technician
            },
            "status": {
                "name": "Открыта"
            },
            "scheduled_end_time": {
                "value": due_date
            },
        }
    }
    try:
        url = os.environ["API_URL"] + f"/requests/{request_id}/tasks"
        headers = {"authtoken" : os.environ["AUTH_TOKEN"]}
        params = {"input_data": json.dumps(task)}
        response_json = rq.post(url, headers=headers, params=params, verify=False).json()
        task = response_json.get("task")
        return Task(**task)
    except Exception as e:
        print(f"Error during request: {e}")
        return None


def list_tasks(list_info):
    try:
        url = os.environ["API_URL"] + "/tasks"
        headers = {"authtoken" : os.environ["AUTH_TOKEN"]}
        params = {"input_data": json.dumps(list_info)}
        tasks_json = rq.get(url, headers=headers, params=params, verify=False).json()
        response_status = tasks_json.get("status")
        list_info = tasks_json.get("list_info")
        tasks = tasks_json.get("tasks")
        for task in tasks:
            yield Task(**task)
    except Exception as e:
        print(f"Error during request: {e}")
        return None


def list_all_tasks(page=0):
    list_info = {
        "row_count": ROW_COUNT,
        "start_index": 1 + page * ROW_COUNT,
        "sort_order": "desc",
        "sort_field": "id",
    }
    list_info = {"list_info": list_info}
    return list_tasks(list_info)


def list_my_tasks(technician_id, page=0):
    list_info = {
        "row_count": ROW_COUNT,
        "start_index": 1 + page * ROW_COUNT,
        "sort_order": "desc",
        "sort_field": "id",
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
    return list_tasks(list_info)


def get_request_task(request_id, task_id):
    try:
        url = os.environ["API_URL"]
        headers = {"authtoken" : os.environ["AUTH_TOKEN"]}
        url = url + f"/requests/{request_id}/tasks/{task_id}"
        response = rq.get(url, headers=headers, verify=False)
        task_json = response.json()
        task = task_json.get("task")
        return Task(**task)
    except Exception as e:
        print(f"Error during request: {e}")
        return None
    

def add_task_description(request_id, task_id, description):
    try:
        url = os.environ["API_URL"]
        headers = {"authtoken" : os.environ["AUTH_TOKEN"]}
        url = url + f"/requests/{request_id}/tasks/{task_id}"
        input_data = {
            "task": {
                "description": description
            }
        }
        list_info = {"input_data": json.dumps(input_data)}
        response = rq.put(url, headers=headers, data=list_info, verify=False)
        task_json = response.json()
        task = task_json.get("task")
        return Task(**task)
    except Exception as e:
        print(f"Error during request: {e}")
        return None


def list_request_worklogs(request_id, page=0):
    try:
        url = os.environ["API_URL"] + f"/requests/{request_id}/worklogs"
        headers = {"authtoken" : os.environ["AUTH_TOKEN"]}
        list_info = {
            "row_count": ROW_COUNT,
            "start_index": 1 + page * ROW_COUNT,
            "sort_order": "desc",
            "sort_field": "start_time",
        }
        list_info = {"list_info": list_info}
        params = {"input_data": json.dumps(list_info)}
        worklogs_json = rq.get(url, headers=headers, params=params, verify=False).json()
        response_status = worklogs_json.get("request_status")
        list_info = worklogs_json.get("list_info")
        worklogs = worklogs_json.get("worklogs")
        for worklog in worklogs:
            yield Worklog(**worklog)
    except Exception as e:
        print(f"Error during request: {e}")
        return None


def add_worklog(request_id, owner, description, hours, minutes):
    try:
        url = os.environ["API_URL"] + f"/requests/{request_id}/worklogs"
        headers = {"authtoken" : os.environ["AUTH_TOKEN"]}
        input_data = {
            "worklog": {
                "description": description,
                "time_spent": {
                    "hours": hours,
                    "minutes": minutes
                },
                "owner": {
                    "name": owner
                }
            }
        }
        list_info = {"input_data": json.dumps(input_data)}
        response = rq.post(url, headers=headers, data=list_info, verify=False)
        worklog_json = response.json()
        print(worklog_json)
        worklog = worklog_json.get("worklog")
        return Worklog(**worklog)
    except Exception as e:
        print(f"Error during request: {e}")
        return None