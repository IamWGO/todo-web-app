from html import unescape
from flask import (Flask, jsonify, request, 
                   render_template,redirect, url_for, flash)

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

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

@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

def authorized_request():
    # Create the 'Authorization' header with the JWT token 
    headers = {
        'Authorization': f"Bearer {config.jwt_token}"
    }

    # Make an HTTP GET request to the API with the 'Authorization' header
    request_url = request.url_root + "/protected"
    response = requests.get(request_url, headers=headers)
    return response.status_code

 
# #################### ENDPOINT ##########################
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["GET","POST"])
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

@app.route("/logout")
def logout():
    config.jwt_token = ""
    flash("You have logout !! ", "success")
    return redirect(url_for("home"))


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


# -------- ITEM DETAIL  ------------
@app.route("/item/<int:task_id>", methods=["GET"])
def item(task_id):
    task_info = {}
    if model.is_number(task_id):
        deleteItemForm = utility.DeleteItemForm() 
        task_info = model.get_task_info(int(task_id))
        if task_info:
            return render_template("item.html", 
                                   is_authen = get_is_auth(),
                                   item=task_info, 
                                   deleteItemForm=deleteItemForm) 
        else: 
            flash("This item does not exist.", "danger")
    else:
        flash("This item does not exist.", "danger") 

    return redirect(url_for("home")) 


# -------- LIST ITEMS  ------------
@app.route("/")
def home(): 
    form = utility.FilterForm(request.args, meta={"csrf": False})
    filter_items = []

    filter_category = config.categories
    if not model.get_category_name_by_id(0):
        filter_category.insert(0, (0, "---"))
    form.category.choices = filter_category

    if form.validate():  
        title = form.title.data
        category_id = int(form.category.data)
        
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
 
    return render_template("home.html",is_authen = get_is_auth(), items=filter_items, form=form)

# -------- NEW ITEM  ------------
@app.route("/item/new", methods=["GET", "POST"])
def new_item():
    # if not authorized then redirect to login
    auth_result = authorized_request()
    if (auth_result != 200):
        return redirect(url_for("login")) 

    form = utility.NewItemForm() 
    if model.get_category_name_by_id(0):
        form.category.choices = config.categories[1:]

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
@app.route("/item/<int:task_id>/edit", methods=["GET", "POST"])
def edit_item(task_id):
    # if not authorized then redirect to login
    auth_result = authorized_request()
    if (auth_result != 200):
        return redirect(url_for("login")) 
 
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
            form.status.default = task_info["status"]

            if model.get_category_name_by_id(0):
                form.category.choices = config.categories[1:]
            
            form.category.default = model.get_category_id_by_name(task_info["category"])
            form.process()
            form.title.data       = task_info["title"]
            form.description.data = unescape(task_info["description"])
            

            return render_template("edit_item.html", 
                                    is_authen = get_is_auth(),
                                    item=task_info, form=form)
    else: 
        flash("This item does not exist.", "danger")

    return redirect(url_for("home")) 
    
# -------- DELETE ITEM  ------------
@app.route("/item/<int:task_id>/delete", methods=["POST"])
def delete_item(task_id): 
    # if not authorized then redirect to login
    auth_result = authorized_request()
    if (auth_result != 200):
        return redirect(url_for("login")) 
 
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
