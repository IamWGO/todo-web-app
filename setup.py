from html import unescape
from flask import Flask, jsonify, send_from_directory, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import InputRequired, DataRequired, Length
from werkzeug.utils import escape

import model

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"
 

class ItemForm(FlaskForm):
    title       = StringField("Title", validators=[InputRequired("Input is required!"), DataRequired("Data is required!"), Length(min=5, max=20, message="Input must be between 5 and 20 characters long")])
    description = TextAreaField("Description", validators=[InputRequired("Input is required!"), DataRequired("Data is required!"), Length(min=5, max=2000, message="Input must be between 5 and 40 characters long")])
    category    = SelectField("Category",
                              choices= model.categories,
                              coerce=int)
 
class NewItemForm(ItemForm):
    submit      = SubmitField("Submit")

class EditItemForm(ItemForm):
    status    = SelectField("status",
                            choices=[('Pending', 'Pending'),
                                    ('Completed', 'Completed')],
                            coerce=str)
    submit      = SubmitField("Update item")

class DeleteItemForm(FlaskForm):
    submit      = SubmitField("Delete item")

class FilterForm(FlaskForm):
    title       = StringField("Title", validators=[Length(max=20)])
    category    = SelectField("Category", coerce=str)
    submit      = SubmitField("Filter")

@app.route("/item/<int:task_id>/edit", methods=["GET", "POST"])
def edit_item(task_id):

    if model.is_number(task_id): 
        task_info = model.get_task_info(task_id) 

        if task_info:
            form = EditItemForm()
            
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
            form.category.default = model.get_category_id_by_name(task_info["category"])
            form.process()
            form.title.data       = task_info["title"]
            form.description.data = unescape(task_info["description"])
             

            return render_template("edit_item.html", item=task_info, form=form)
    else: 
        flash("This item does not exist.", "danger")

    return redirect(url_for("home")) 
   

@app.route("/item/<int:task_id>/delete", methods=["POST"])
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

@app.route("/item/<int:task_id>", methods=["GET"])
def item(task_id):
    task_info = {}
    if model.is_number(task_id):
        deleteItemForm = DeleteItemForm() 
        task_info = model.get_task_info(int(task_id))
        if task_info:
            return render_template("item.html", item=task_info, deleteItemForm=deleteItemForm) 
        else: 
            flash("This item does not exist.", "danger")
    else:
        flash("This item does not exist.", "danger") 

    return redirect(url_for("home")) 


@app.route("/")
def home(): 
    form = FilterForm(request.args, meta={"csrf": False})
    filter_items = []

    categories = model.get_categories()
    categories.insert(0, (0, "---"))
    form.category.choices = categories

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

        
    print(filter_items)
    return render_template("home.html", items=filter_items, form=form)

@app.route("/item/new", methods=["GET", "POST"])
def new_item():
    form = NewItemForm()

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
    
    return render_template("new_item.html", form=form)