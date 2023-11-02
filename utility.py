from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import InputRequired, DataRequired, Length
from werkzeug.utils import escape
 

# #################### WT-FORM ##########################
class ItemForm(FlaskForm):
    title       = StringField("Title", validators=[InputRequired("Input is required!"), DataRequired("Data is required!"), Length(min=5, max=100, message="Input must be between 5 and 20 characters long")])
    description = TextAreaField("Description", validators=[InputRequired("Input is required!"), DataRequired("Data is required!"), Length(min=5, max=2000, message="Input must be between 5 and 40 characters long")])
    category    = SelectField("Category", coerce=int)
 
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

class AuthForm(FlaskForm):
    submit      = SubmitField("Get Token")
    

class FilterForm(FlaskForm):
    title       = StringField("Title", validators=[Length(max=20)])
    category    = SelectField("Category",
                              coerce=int)
    submit      = SubmitField("Filter")