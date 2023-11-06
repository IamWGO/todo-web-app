import requests
from flask import request
import model

def request_all_tasks():
    #Get Data from Backend
    request_url = request.url_root + "/tasks"
    response = requests.get(request_url)
    if response.status_code == 200:  # Check for a successful HTTP status code
        return response.json()

def request_task_by_id(task_id):
    #Get Data from Backend
    request_url = request.url_root + f"/tasks/{task_id}" 
    response = requests.get(request_url)
    if response.status_code == 200:  # Check for a successful HTTP status code
        return response.json()
    else:
        return None
    
def request_update_task(form, task_id):
    category_name = model.get_category_name_by_id(form['category'])
    if category_name:
        update_task = {"id": task_id,
        "title": form['title'],
        "description": form['description'],
        "category": category_name,
        "status": form['status']
        } 
        # Backend endpoint
        request_url = request.url_root + f"/tasks/{task_id}" 
        # Send a POST request with the form data
        return requests.put(request_url, data=update_task)
    else:
        return {"status": 201}
    
    
def add_new_task(form):
    category_name = model.get_category_name_by_id(form['category'])
    if category_name:
        new_task = {"id": model.get_max_id(is_task=True),
                "title": form['title'],
                "description": form['description'],
                "category": category_name,
                "status": "Pending"
                }
        
        # Backend endpoint
        request_url = request.url_root + f"/tasks/" 
        # Send a POST request with the form data
        return requests.post(request_url, data=new_task)
    else:
        return {"status": 201}