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
####Requirements
Flask(0.11.1)
Flask-SQLAlchemy(2.1)
mysqlclient(1.3.7)
oauth2client(3.0.0)

    virtualenv -p python3 env
    env/bin/pip3 install -r requirements.txt

###Tensorflow
######https://www.tensorflow.org/versions/r0.10/get_started/os_setup.html#pip-installation
This version is OS X, CPU only, python3.5.2

    # Mac OS X, CPU only, Python 3.4 or 3.5:
    $ export TF_BINARY_URL=https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-0.10.0rc0-py3-none-any.whl
    # Python 3
    $ env/bin/pip3 install --upgrade $TF_BINARY_URL


### Reference

