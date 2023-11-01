
> mkdir sample-webshop
> cd sample-webshop
> python -m venv venv
> pip freeze > requirements.txt
> pip install -r requirements.txt


create file : .flaskenv

FLASK_APP=setup.py
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_RUN_EXTRA_FILES=templates/**/*.html,static/css/*.css


Create database : you must have folder db 
> python db/db_init.py


> pip install flask_wtf
> pip freeze > requirements.txt
> pip install -r requirements.txt





PostgrSql -----------------------------

CREATE USER wgo WITH PASSWORD '123456';
GRANT CONNECT ON DATABASE webshop TO wgo;

import psycopg2

#establishing the connection
conn = psycopg2.connect(
   database="webshop", user='wgo', password='123456', host='127.0.0.1', port= '5432'
)
#Creating a cursor object using the cursor() method
cursor = conn.cursor()

#Executing an MYSQL function using the execute() method
cursor.execute("select version()")

# Fetch a single row using fetchone() method.
data = cursor.fetchone()
print("Connection established to: ",data)

#Closing the connection
conn.close()


  <div class="col-lg-3 my-4">
    <a href="{{ url_for('item_edit', task_id=item) }}" class="btn btn-primary">Edit item</a>
    <form class="delete-form" method="DELETE" action="{{ url_for('item', task_id=item) }}">
      {{ deleteItemForm.hidden_tag() }}
      {{ deleteItemForm.submit(class="btn btn-danger", onclick="return confirm('Are you sure you want to delete this item?');") }}
    </form>
  </div>