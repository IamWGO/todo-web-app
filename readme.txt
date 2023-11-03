
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

DECODEED
header
{
  "alg": "HS256",
  "typ": "JWT"
}
playload
{}

ENCODED 
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.ZZlqptuwSooNrxSm_dmtInv2rsFDrBspAlBoWqBX1Ys




 {% if items[category[1] %}

            {% for item in items[category[1]] %}
            <div class="col-lg-6 col-md-6 mb-4">
                <div class="card h-100"> 
                  <div class="card-body">
                    <h4 class="card-title">
                      <a href="{{ url_for('item', task_id=item.id) }}">{{ item.title }}</a>
                    </h4>
                    <h5>{{ item.status }}</h5>
                    <p class="card-text">{{ item.description | safe }}</p>
                  </div>
                  <div class="card-footer">
                    <small class="text-muted" style="float: left;">
                      {{ item.category }}
                    </small>
                    <a href="{{ url_for('item', task_id=item.id) }}" style="float: right;">
                      <small class="text-muted">View</small>
                    </a>
                    <div style="clear: both;"></div>
                  </div>
                  
                </div>
            </div>
            {% endfor %}
          {% else %}
          <h1 class="offset-lg-3">No items in {{category[1]}}.</h1>
          {% endif %}