# IHR Electric Cars Charging Plot API Server #

## Project Structure ##

* Main source code: 
  All source code are located in `application` folder.
    * `default_settings.py` contains basic configurations, it will be rewrite
      by `production.py` if production server is started from `runproduct.sh`;
    * `__init__.py` is the entrance of entire project where Flask modules and
      WSGI application are defined; extensions shall also be initialized here
      to make them available globally `route`, `script` and other similar modules
      will be imported at the end of this file, after all their dependencies
      modules and extensions are initialized;
    * `models.py` defines ORM layer classes;
    * `route.py` defines server URL routes;
    * `script.py` defines command line management utilities.

* Unit test cases:
  Unit cases are in `tests`. Feature and other black box test cases are included in separated project.

* SQL Database migration scripts:
  SQL DB upgrading and migrating scripts are managed by [alembic](https://alembic.readthedocs.org/en/latest/),
  with in project.

* Assistant scripts:
  Under project folder there are several scripts for backend web server management.
    * `manage.py` is a proxy to [Flask-Script](https://flask-script.readthedocs.org/en/latest/), which
      redirects commands to `application/script.py`;
    * `rundev.py` starts a debug server listening at `http://127.0.0.1:5000`;
    * `runproduct.py` starts [gunicorn](http://gunicorn.org/) production server.
      It requires root privilege to listen at port 80. 
    * `runtests.py` is just a wrapper to Python
      [unittest](https://docs.python.org/2/library/unittest.html) framework main entrance.

## Deploy Product Server ##

[Fabric](http://docs.fabfile.org/en/1.10/index.html) is used as automatic
deployment tool. Clone project and install `Fabric` then execute following
commands to deploy a new server:

```bash
fab -H <server> -u <username> first_install
```

Login password will be asked to continue. The `sudo` privilege shall be granted
to the user on target server(s) used for deploying.

For servers on which project has been deployed before, action `update` can be
used for pulling latest code then restarting API service:

```bash
fab -H <server> -u <username> update

# since update is default action, it can be omitted, like
fab -H <server> -u <username>
```

Some other useful actions:
```bash
# start service
fab -H <server> -u <username> start

# stop service
fab -H <server> -u <username> stop

# show service process status
fab -H <server> -u <username> status
```

To control more servers in a bunch, read specify multiple targets separated by
comma(`,`) after `-H` option. Parallel is optional by adding `-P` option to
`fab` command. For more, please read [the
document](http://docs.fabfile.org/en/1.10/usage/parallel.html).

## Setup Develop Environment ##

* Checkout project:
  For key pair settings, please refer to
  [bitbucket help](https://confluence.atlassian.com/bitbucket/add-an-ssh-key-to-an-account-302811853.html).
```bash
git clone git@bitbucket.org:huangloong/charger-web-backend.git
cd charger-web-backend
```

* Install [pip](https://pip.pypa.io/en/stable/installing/).

* Setup an virtual environment (optional but highly recommended)
    * Install [VirtualEnv](https://virtualenv.readthedocs.org/en/latest/) if not done yet:
      `sudo pip install virtualenv`
    * Create virtual environment
      `virtualenv venv`
    * Activate the environment, **shall be done every time after starting a new terminal**
      `source venv/bin/activate`

* Install dependencies: `pip install -r requirements.txt`

* Run test cases:
```bash
./runtests.py
./rundev.py
```

* Run production server:
```bash
sudo su
# with virtual environment
source venv/bin/activate
./runproduct.sh
```

## Dependencies ##

* `alembic` for SQL DB migration scripts between different versions. [Website](https://alembic.readthedocs.org/en/latest/)
* `Flask` Web service framework. [Website](https://flask.readthedocs.org/en/latest)
* `Flask-Script` Web service management script skeleton. [Website](https://flask-script.readthedocs.org/en/latest/)
* `Flask-SQLAlchemy` ORM integration. [Website](http://flask-sqlalchemy.pocoo.org/)
* `Flask-User` user management framework. [Website](http://pythonhosted.org/Flask-User/)
* `gevent` nonblocking socket for production server. [Website](http://www.gevent.org/)
* `gunicorn` pre-forking WSGI server (for production). [Website](http://gunicorn.org/)

