from datetime import timedelta
from html import unescape
from flask import (Flask, jsonify, request, 
                   render_template,redirect, url_for, flash)

from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from functools import wraps

import requests
import config
import utility
import model

app = Flask(__name__)
# #################### SECURITY ##########################
# security mechanisms used in web applications to protect against Cross-Site Request 
app.secret_key = config.JWT_SECRET_KEY
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
jwt = JWTManager(app)

def get_is_auth():
    return config.jwt_token != "" 
 
# #################### AUTH PROCESS ##########################
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
 
def allow_access_only_postman(func):
    def decorated_function(*args, **kwargs): 
        user_agent = request.headers.get('User-Agent')
        substring = "Postman"
        if substring in user_agent:
            return redirect(url_for("home"))
        return func(*args, **kwargs)
    return decorated_function

def allow_access_only_browser(func):
    def decorated_function(*args, **kwargs): 
        user_agent = request.headers.get('User-Agent')
        substring = "Postman"
        if substring in user_agent:
            return "Postman can't access to this URL"
        return func(*args, **kwargs)
    return decorated_function


# #################### ENDPOINT - AUTH PROCESS ##########################
@app.route("/protected", methods=["GET"])
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

# #################### ENDPOINT - CRUD PROCESS ############### ###########
# -------- LIST ITEMS  ------------
@app.route("/", endpoint="home")
@allow_access_only_browser
def home(): 
    deleteItemForm = utility.DeleteItemForm() 
    filter_form = utility.FilterForm(request.args, meta={"csrf": False})
    filter_items = []

    filter_category = config.categories
    if not model.get_category_name_by_id(0):
        filter_category.insert(0, (0, "---"))
    filter_form.category.choices = filter_category

    if filter_form.validate():  
        title = filter_form.title.data
        category_id = int(filter_form.category.data)
        
        if (title.strip() and category_id > 0):
            filter_items = model.search_by_title_and_category_name(title, category_id)
        elif title.strip():
             filter_items = model.search_task_by_title(title)
        elif category_id > 0:
            filter_items = model.search_tasks_by_category_name(category_id)
        else: 
            filter_items = model.get_all_tasks()
    else: 
        filter_items = model.get_all_tasks() 

    categories = config.categories
    if model.get_category_name_by_id(0):
        categories = categories[1:] 
 
    return render_template("home.html",is_authen = get_is_auth(),
                            items=filter_items,
                            categories=categories,
                            form=filter_form,
                            deleteItemForm=deleteItemForm)

# -------- ITEM DETAIL  ------------
@app.route("/tasks/<int:task_id>/detail", methods=["GET"] ,endpoint="detail_item")
@allow_access_only_browser
def item(task_id):
    task_info = {}
    deleteItemForm = utility.DeleteItemForm() 
    task_info = model.get_task_info(int(task_id))
    if task_info:
        return render_template("item.html", 
                                is_authen = get_is_auth(),
                                item=task_info, 
                                deleteItemForm=deleteItemForm) 
    else: 
        flash("This item does not exist.", "danger")

    return redirect(url_for("home")) 



# -------- NEW ITEM  ------------
@app.route("/tasks/new", methods=["GET", "POST"], endpoint="new_item")
@allow_access_only_browser
@requires_authentication
def new_item():
    form = utility.NewItemForm() 
    
    # Form
    if form.validate_on_submit():
        if model.get_category_name_by_id(int(request.form['category'])):
            category_name = model.get_category_name_by_id(int(request.form['category']))
            new_task = {"id": model.get_max_id(),
                    "title": request.form['title'],
                    "description": request.form['description'],
                    "category": category_name,
                    "status": "Pending"
                    }
            
            model.add_new_task(new_task)
            # Redirect to some page
            flash("Item {} has been successfully submitted"
                .format(request.form.get("title")), "success")
            return redirect(url_for("home")) 
        else:
            flash("Category is not matched with database", "danger")
    
    return render_template("new_item.html", is_authen = get_is_auth(), form=form)


# -------- UPDATE ITEM  ------------
@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"], endpoint="edit_item")
@allow_access_only_browser
@requires_authentication
def edit_item(task_id):
 
    if model.is_number(task_id): 
        task_info = model.get_task_info(task_id) 

        if task_info:
            form = utility.EditItemForm()
            
            if form.validate_on_submit(): 
                category_name = model.get_category_name_by_id(int(request.form['category']))
                update_task = {"id": task_id,
                    "title": request.form['title'],
                    "description": request.form['description'],
                    "category": category_name,
                    "status": request.form['status']
                    }

                model.update_task(task_id, update_task) 

                flash("Item {} has been successfully updated".format(form.title.data), "success")
                return redirect(url_for("item", task_id=task_id))

            form.category.choices = config.categories[1:]
            form.category.default = model.get_category_id_by_name(task_info["category"])

            form.status.default = task_info["status"]
            
            form.process()
            form.title.data       = task_info["title"]
            form.description.data = unescape(task_info["description"])
            

            return render_template("edit_item.html", 
                                    is_authen = get_is_auth(),
                                    item=task_info, form=form)
    else: 
        flash("This item does not exist.", "danger")

    return redirect(url_for("home")) 
        
# -------- COMPLATE TASK -------
@app.route("/tasks/<int:task_id>/complate", methods=["POST"], endpoint="complete_item")
@allow_access_only_browser
@requires_authentication
def set_task_completed(task_id):
    task_info = model.get_task_info(task_id) 
    if task_info:
        task_to_update = task_info
        if not task_info["status"] == "Completed":
            task_to_update["status"] = "Completed"
            model.update_task(task_id, task_to_update) 
            flash(f"You have set completed to task: \n {task_info["description"]}", "success")
        else:
            flash(f"Warning: You already completed task: \n {task_info["description"]}", "danger")

    return redirect(url_for("home")) 
    
# -------- DELETE ITEM  ------------
@app.route("/tasks/<int:task_id>/delete", methods=["POST"], endpoint="delete_item")
#@requires_authentication
def delete_item(task_id): 
    if model.is_number(task_id): 
        task_info = model.get_task_info(task_id)
        if task_info:
            model.delete_task(task_id)
            flash("Item {} has been successfully deleted.".format(task_info["title"]), "success")
        else: 
            flash("This item does not exist.", "danger")
    else:
        flash("This item does not exist.", "danger")

    return redirect(url_for("home")) 

# -------- ERROR HANDLER  ------------
def page_404(e):
    return render_template("errors/404.html", is_authen = get_is_auth())

def page_405(e):
    return render_template("errors/405.html", is_authen = get_is_auth())

def page_401(e):
    return render_template("errors/401.html", is_authen = get_is_auth())

app.register_error_handler(404, page_404)
app.register_error_handler(405, page_405)
app.register_error_handler(401, page_401)
