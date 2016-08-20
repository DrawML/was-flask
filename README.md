# DrawML WAS
 * python3
 * flask

## Directory stucture
* app.py
* config.py
* env
* app
    * module_name
        * __init__.py
        * controllers.py
        * models.py
    * static
    * templates
        * module_name

## Install and dependency
    virtualenv -p python3 env
    env/bin/pip3 install flask
    env/bin/pip3 install flask-sqlalchemy
    env/bin/pip3 install mysqlclient
    env/bin/pip3 install rauth
    