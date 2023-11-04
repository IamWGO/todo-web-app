from flask import Flask, jsonify, request, render_template
import model

app = Flask(__name__)
# #################### BACKEND : TASK ##########################
# 1. GET /tasks: Retrieves all tasks. For an "VG" (Very Good) requirement, add a "completed" parameter to filter by completed or uncompleted tasks.
# 2. POST /tasks: Adds a new task. The task is initially uncompleted when first added.
@app.route("/")
@app.route("/tasks/", methods=["POST","GET"])
def tasks():
    if request.method == "POST":
        new_task = {"id": model.get_max_id(is_task=True),
                "title": request.form['title'],
                "description": request.form['description'],
                "category": request.form['category'],
                "status": "Pending"
                }
        model.add_new_task(new_task)
        
        return {"requirement": "Adds a new task. The task is initially uncompleted when first added",
                 "result": new_task}
    else:
        return {"requirement": "Retrieves all tasks",
            "result": model.task_items}

@app.route("/tasks/completed/", methods=["GET"])
def completed():
    completed_tasks = model.search_completed_tasks()
    return {"requirement": "add a 'completed' parameter to filter by completed or uncompleted tasks",
            "result": model.task_items}    

# 3. GET /tasks/{task_id}: Retrieves a task with a specific ID.
# 4. DELETE /tasks/{task_id}: Deletes a task with a specific ID.
# 5. PUT /tasks/{task_id}: Updates a task with a specific ID.
@app.route("/tasks/<int:task_id>", methods=["GET", "DELETE", "PUT"])
def get_task(task_id):
    task_info = model.get_task_info(task_id)
    if not task_info == None:
        if request.method == "GET":
            return {
                "requirement": "Retrieves a task with a specific ID",
                "taskId" :task_id,
                "result": task_info}  
        
        elif request.method == "DELETE":
            model.delete_task(task_id)
            return {
                    "requirement": "Deletes a task with a specific ID.",
                    "taskId" :task_id,
                    "result": "deleted"}  
        
        elif request.method == "PUT":
            update_task = {"id": task_id,
            "title": request.form['title'],
            "description": request.form['description'],
            "category": request.form['category'],
            "status": request.form['status']
            }

            model.update_task(task_id, update_task)
            return  {"requirement": "Updates a task with a specific ID.",
                     "taskId" :task_id,
                    "result": update_task}
    else:
            return {
            "taskId": task_id,
            "result": "Not found"
            } 
    
# 6. PUT /tasks/{task_id}/complete: Marks a task as completed.
@app.route("/tasks/<int:task_id>/complete", methods=["PUT"])
def set_task_completed(task_id):
    task_info = model.get_task_info(task_id)
    if task_info:
        task_to_update = task_info
        if not task_info["status"] == "completed":
            task_to_update["status"] = "completed"
            model.update_task(task_id, task_to_update)
            return  {
                "requirement": "Marks a task as completed",
                "taskId" :task_id,
                "result": f"set completed task: \n {task_info["description"]}"} 
        else:
            return {
                "requirement": "Marks a task as completed",
                "taskId" :task_id,
                "result": f"You already completed task: \n {task_info["description"]}"
                } 
    else:
        return {
            "taskId": task_id,
            "result": "Not found"
            }

# 7. GET /tasks/categories/: Retrieves all different categories.
@app.route("/tasks/categories", methods=["GET"])
def get_task_by_category():
    tasks_by_category = model.get_tasks_by_category(model.task_items)
    return {"requirement": "Retrieves all different categories.",
            "result": tasks_by_category} 

 # 8. GET /tasks/categories/{category_name}: Retrieves all tasks from a specific category.
@app.route("/tasks/categories/<string:category_name>")
def search_task_by_category(category_name): 
    task_by_category_name = model.search_tasks_by_category_name(category_name) 
    return {"requirement": "Retrieves all tasks from a specific category.",
            "category": category_name,
            "result": task_by_category_name} 


# #################### BACKEND : CATEGORY ##########################
@app.route("/categories/", methods=["POST","GET"])
def categories():
    if request.method == "POST":
        new_category = {"id": model.get_max_id(is_task=False),
                "title": request.form['title'],
                "status": "Active"
                }
        model.add_new_category(new_category)
        
        return {"requirement": "Adds a new category",
                 "result": new_category}
    else:
        return {"requirement": "Retrieves all categories",
            "result": model.category_items}


@app.route("/categories/<int:category_id>", methods=["GET", "DELETE", "PUT"])
def get_category(category_id):
    category_info = model.get_category_info(category_id)
    if not category_info == None:
        if request.method == "GET":
            return {
                "requirement": "Retrieves a category with a specific ID",
                "categoryId" :category_id,
                "result": category_info}  
        
        elif request.method == "DELETE":
            model.delete_category(category_id)
            return {
                    "requirement": "Deletes a category with a specific ID.",
                    "categoryId" :category_id,
                    "result": "deleted"}  
        
        elif request.method == "PUT":

            status = "Active"
            if 'status' in request.form:
                status = request.form['status']

            update_category = {"id": category_id,
            "title": request.form['title'],
            "status": status
            }

            model.update_category(category_id, update_category)
            return  {"requirement": "Updates a category with a specific ID.",
                     "categoryId" :category_id,
                    "result": update_category}
    else:
            return {
            "categoryId": category_id,
            "result": "Not found"
            } 

# #################### ERROR HANDLER ##########################
def page_404(e):
    return "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."

def page_405(e):
    return "The method is not allowed for the requested URL."

app.register_error_handler(404, page_404)
app.register_error_handler(405, page_405)


