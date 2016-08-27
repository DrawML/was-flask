# DrawML WAS
 * python3
 * flask
 * [REST API wiki](https://github.com/DrawML/was-flask/wiki/REST-API)

## Directory stucture
* app.py
* config
    * app_config.py
    * config_file.json
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
    env/bin/pip3 install oauth2client


### Reference
* oauth2client : https://developers.google.com/api-client-library/python/auth/web-app
