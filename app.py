from flask import (Flask, jsonify, request, 
                   render_template,redirect, url_for, flash)

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import requests
import config
import utility
import model
import http_request

app = Flask(__name__)

model.task_items = model.load_db("task.json")
model.category_items = model.load_db("category.json")
model.categories = model.get_categories_tuples()

# #################### AUTH PROCESS ##########################
# security mechanisms used in web applications to protect against Cross-Site Request 
app.secret_key = config.JWT_SECRET_KEY
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
jwt = JWTManager(app)

def get_is_auth():
    return config.jwt_token != "" 

# the 'Authorization' header with the JWT token 
def authorized_request():
    headers = {
        'Authorization': f"Bearer {config.jwt_token}"
    }

    # Make an HTTP GET request to the API with the 'Authorization' header
    request_url = request.url_root + "/protected"
    response = requests.get(request_url, headers=headers)
    if response.status_code != 200:
        config.jwt_token = ""

    return response.status_code

# #################### DECORATOR ##########################
# Custom authentication decorator
def requires_authentication(func):
    def decorated_function(*args, **kwargs):
        auth_result = authorized_request()
        if (auth_result != 200):
            return redirect(url_for("login")) 
    
        return func(*args, **kwargs)
    return decorated_function

def is_access_from_postman():
    user_agent = request.headers.get('User-Agent')
    substring = "Postman"
    return substring in user_agent

def allow_access_only_browser(func):
    def decorated_function(*args, **kwargs): 
        if is_access_from_postman():
            return "Postman can't access to this URL"
        return func(*args, **kwargs)
    return decorated_function


# #################### ENDPOINT - AUTH PROCESS ##########################
@app.route("/protected", methods=["GET"], endpoint="protected")
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route("/login", methods=["GET","POST"], endpoint="login")
@allow_access_only_browser
def login():
    is_authen = get_is_auth()
    authForm = utility.AuthForm() 
    if not get_is_auth() :
        if request.method == "POST":
            config.jwt_token = create_access_token(identity=config.JWT_SECRET_KEY)
            flash("authorization has been successfully ", "success")
            return redirect(url_for("home"))
    
    return render_template("login.html", 
                           is_authen=is_authen, 
                           form=authForm)  

@app.route("/logout", endpoint="logout")
@allow_access_only_browser
def logout():
    config.jwt_token = ""
    flash("You have logout !! ", "success")
    return redirect(url_for("home"))

# #################### BACKEND : TASK ##########################
# 1. GET /tasks: Retrieves all tasks. For an "VG" (Very Good) requirement, add a "completed" parameter to filter by completed or uncompleted tasks.
@app.route("/tasks/", methods=["GET"])
def all_task():
    return model.task_items

# 2. POST /tasks: Adds a new task. The task is initially uncompleted when first added.
@app.route("/tasks/", methods=["POST"])
def tasks():
    new_task = {"id": model.get_max_id(is_task=True),
                "title": request.form['title'],
                "description": request.form['description'],
                "category": request.form['category'],
                "status": "Pending"
                } 
    model.add_new_task(new_task) 
    return {"status": 200, "result": "added new task"}

@app.route("/tasks/completed/", methods=["GET"])
def completed():
    completed_tasks = model.search_completed_tasks()
    return {"requirement": "add a 'completed' parameter to filter by completed or uncompleted tasks",
            "result": completed_tasks}    

# 3. GET /tasks/{task_id}: Retrieves a task with a specific ID.
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    return model.get_task_info(task_id)

# 4. DELETE /tasks/{task_id}: Deletes a task with a specific ID.
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task_info = model.get_task_info(task_id)
    if not task_info:
        return {"taskId": task_id,"result": "Not found"} 

    model.delete_task(task_id)
    return {
            "requirement": "Deletes a task with a specific ID.",
            "taskId" :task_id,
            "result": "deleted"}  

# 5. PUT /tasks/{task_id}: Updates a task with a specific ID.
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task_info = model.get_task_info(task_id)
    if not task_info:
        return {"taskId": task_id,"result": "Not found"} 
    
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
 
# 6. PUT /tasks/{task_id}/complete: Marks a task as completed.
@app.route("/tasks/<int:task_id>/complete", methods=["PUT"])
def set_task_completed(task_id):
    task_info = model.get_task_info(task_id)
    print(task_info)
    if task_info:
        task_to_update = task_info
        if not task_info["status"] == "Completed":
            task_to_update["status"] = "Completed"
            model.update_task(task_id, task_to_update)
            return  {"status": 200} 
        else:
            return {"status": 201, "msg": f"You already completed task"} 
    else:
        return {"status": 404, "msg": "Not found"}

# 7. GET /tasks/categories/: Retrieves all different categories.
@app.route("/tasks/categories", methods=["GET"])
def get_task_by_category():
    tasks_by_category = model.get_tasks_by_category(model.task_items)
    return {"requirement": "Retrieves all different categories.",
            "result": tasks_by_category} 

 # 8. GET /tasks/categories/{category_name}: Retrieves all tasks from a specific category.
@app.route("/tasks/categories/<string:category_name>")
def search_task_by_category(category_name): 
    task_by_category_name = model.search_tasks_by_category_name(model.task_items, category_name) 
    return {"requirement": "Retrieves all tasks from a specific category.",
            "category": category_name,
            "result": task_by_category_name} 


# #################### BACKEND : CATEGORY ##########################
# 9. GET /manage/category/: Retrieves all categories
# 10. POST /manage/category/: Adds a new category
@app.route("/manage/category", methods=["POST","GET"])
def new_category():
    if request.method == "POST":
        new_category = {"id": model.get_max_id(is_task=False),
                "title": request.form['title'],
                "status": "Active"
                }
        
        model.add_new_category(new_category)
        
        return {"requirement": "Adds a new category",
                 "result": new_category}
    else:
        return model.category_items

# 11. GET /manage/category/<int:category_id>: Retrieves a category with a specific ID.
# 12. DELETE /manage/category/<int:category_id>: Deletes a category with a specific ID.
# 13. PUT /manage/category/<int:category_id>: Updates a category with a specific ID.
@app.route("/manage/category/<int:category_id>", methods=["GET", "PUT", "DELETE"])
def get_category(category_id):
    category_info = model.get_category_info(category_id) 
    if request.method == "GET":
        return {
            "requirement": "Retrieves a category with a specific ID",
            "categoryId" :category_id,
            "result": category_info}  
    
    elif request.method == "DELETE":
        result = ""
        if category_info:
            model.delete_category(category_id)
            result = "deleted"
        else:
            result = "not found"
            
        return {
                "requirement": "Deletes a category with a specific ID.",
                "categoryId" :category_id,
                "result": result} 
    
    elif request.method == "PUT":
        if category_info:
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
            return  {"requirement": "Updates a category with a specific ID.",
                        "categoryId" :category_id,
                    "result": "not found"} 


# #################### ENDPOINT - FRONTEND ##########################
# -------- LIST ITEMS  ------------
@app.route("/", endpoint="home")
@allow_access_only_browser
def home(): 
    filter_items = http_request.request_all_tasks()
   
    deleteItemForm = utility.DeleteItemForm() 
    filter_form = utility.FilterForm(request.args, meta={"csrf": False})

    categories = model.categories
    if model.get_category_name_by_id(0):
        categories = categories[1:] 

    filter_title = "-"
    filter_status = "-"
    filter_category = "-"

    category_items = model.get_categories_tuples()
    category_items.insert(0, (0, "---"))   
    filter_form.category.choices = category_items

    filter_form.status.choices.insert(0, ("-", "---"))

    if filter_form.validate():  
        filter_title = filter_form.title.data
        filter_status = filter_form.status.data
        category_id = filter_form.category.data
   
        if filter_title.strip():
             filter_items = model.search_task_by_title(filter_items, filter_title)
        else:
            filter_title = "-"

        if not filter_status == "-":
             filter_items = model.search_task_by_status(filter_items, filter_status)
            
        
        if category_id > 0:
            filter_items = model.search_tasks_by_category_id(filter_items, category_id)
            filter_category = model.get_category_name_by_id(category_id)
 
    return render_template("home.html",
                           is_authen = get_is_auth(),
                            items=filter_items,
                            categories=categories,
                            form=filter_form,
                            filterTitle=filter_title,
                            filterStatus=filter_status,
                            filterCategory=filter_category,
                            deleteItemForm=deleteItemForm)

# -------- ITEM DETAIL  ------------
@app.route("/todo/<int:task_id>/detail", methods=["GET"] ,endpoint="detail_tasks")
@allow_access_only_browser
def item(task_id): 
    task_info = http_request.request_task_by_id(task_id) 

    deleteItemForm = utility.DeleteItemForm() 
    task_info = model.get_task_info(task_id)
    if task_info:
        return render_template("item.html", 
                                is_authen = get_is_auth(),
                                item=task_info, 
                                deleteItemForm=deleteItemForm) 
    else: 
        flash("This item does not exist.", "danger")

    return redirect(url_for("home"))

# -------- NEW ITEM  ------------
@app.route("/todo/new", methods=["GET", "POST"], endpoint="new_tasks")
@allow_access_only_browser
#@requires_authentication
def new_item():
    form = utility.NewItemForm() 

    category_items = model.get_categories_tuples()
    form.category.choices = category_items
    
    # Form
    if form.validate_on_submit():
        response = http_request.add_new_task(request.form)
        if response.status_code == 200:  # Check for a successful HTTP status code
            flash("Item {} has been successfully submitted"
            .format(request.form.get("title")), "success")
        else: 
            flash("Some thing wrong with add item process"
            .format(request.form.get("title")), "danger") 
        return redirect(url_for("home"))  
    
    return render_template("new_item.html", is_authen = get_is_auth(), form=form)

# -------- UPDATE ITEM  ------------
@app.route("/todo/<int:task_id>/edit", methods=["GET", "POST"], endpoint="edit_tasks")
@allow_access_only_browser
# @requires_authentication
def edit_item(task_id):
    task_info = http_request.request_task_by_id(task_id) 

    if task_info:
        form = utility.EditItemForm()
        form.category.choices = model.categories[1:]
        
        if form.validate_on_submit(): 
            response = http_request.request_update_task(request.form, task_id)
            if response.status_code == 200:  # Check for a successful HTTP status code
                flash("Item {} has been successfully updated"
                    .format(form.title.data), "success")
                return redirect(url_for("detail_tasks", task_id=task_id))
            else: 
                flash("Some thing wrong with update item process"
                .format(request.form.get("title")), "danger")    
 
        form.category.default = model.get_category_id_by_name(task_info["category"])
        form.status.default = task_info["status"]
        form.process()
        form.title.data       = task_info["title"]
        form.description.data = task_info["description"]

        return render_template("edit_item.html", 
                                is_authen = get_is_auth(),
                                item=task_info, form=form)
    else: 
        flash("This item does not exist.", "danger")

    return redirect(url_for("home")) 
        
# -------- COMPLATE TASK -------
@app.route("/todo/<int:task_id>/complate", methods=["POST"], endpoint="complete_tasks")
@allow_access_only_browser
#@requires_authentication
def set_task_completed(task_id):
    response = http_request.request_update_completed(task_id)
    if response.status_code == 200:
        flash(f"You have set completed to task", "success")
    else:
        flash(f"Warning: You already completed task", "danger")

    return redirect(url_for("home")) 
    
# -------- DELETE ITEM  ------------
@app.route("/todo/<int:task_id>/delete", methods=["POST"], endpoint="delete_tasks")
#@requires_authentication
def delete_tasks(task_id): 
    task_info = model.get_task_info(task_id)
    if task_info:
        http_request.request_delete_task(task_id)
        flash("Item {} has been successfully deleted.".format(task_info["title"]), "success")
    else: 
        flash("This item does not exist.", "danger")

    return redirect(url_for("home")) 

# -------- ERROR HANDLER  ------------
app.register_error_handler(404, utility.page_404)
app.register_error_handler(405, utility.page_405)
app.register_error_handler(401, utility.page_401)
