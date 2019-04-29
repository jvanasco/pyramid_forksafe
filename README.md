pyramid_forksafe
================

This package creates standardized Pyramid events for various forking hooks in popular deployment containers.

Using `pyramid_forksafe` allows a developer to write generic routines for forking events, allowing them to easily swap containers during deployment or development.

Each event is invoked with the application's `registry`, through which one can access `registry.settings`

## Why?

Pyramid is Thread Safe, which is different than Fork Safe.

Several popular libraries are not fork-safe:

* SqlAlchemy's connection pool is not fork-safe.  Your deployment *must* call `engine.dispose()` after a fork.
* PyMongo's connections and locks are not fork-safe.  The entire client must be replaced after a fork.
* PyCrypto's Random generator will only work correctly if Random.atfork() is called.

In some situations, a developer may need to access the registry and/or settings during postfork actions. Getting this information into a custom hook can be a hassle, as one will need to write against each container's API instead of Pyramid's. 

This blog posting describes the difference between fork-safe and thread-safe pretty well  http://www.dctrwatson.com/2010/09/python-thread-safe-does-not-mean-fork-safe/


## Usage - Generic

Define a GENERIC hook.  

    def post_fork_hook(_registry):
        cyrpto_atfork()
        models.engine.dispose(_registry)
    config.add_subscriber(post_fork_hook, ApplicationPostFork)

You can import the generic package in your `environment.ini` file (or main config), and this will try to enable services if possible:

	# development.ini
    pyramid.includes = pyramid_forksafe

or you may wish to import a SPECIFIC container package in your `environment.ini` file (or main config)

	# development.ini
    pyramid.includes = pyramid_forksafe.containers.uwsgi

Currently, this approach only works for `uWSGI`.  `gunicorn` requires another approach.


## Usage - uWSGI

simply include the package and uwsgi will be automatically enabled:

in your `__init__.py`:

    config.include('pyramid_forksafe')

or your `{environment}.ini`

    pyramid.includes = pyramid_forksafe

## Usage - gunicorn

`gunicorn` will need some hooks imported into it's python configuration file

assuming you invoke gunicorn like this:

	gunicorn --paste production.ini -c config.py

then your `config.py` just needs to import the container hooks:

    from pyramid_forksafe.containers.gunicorn import (
        pre_fork,
        post_fork,
        post_worker_init,
    )

those hooks are written to the `gunicorn` api, and will invoke the notification

## Container Support

Currently `uwsgi` and `gunicorn` are supported with the hooks outlined below.   Celery is planned.  Pull requests are welcome.


| container | pyramid\_forksafe event      | container hook |
|-----------|-----------------------------|------|
| uWSGI     | `ApplicationPostFork`       | [`postfork`](http://uwsgi-docs.readthedocs.io/en/latest/PythonDecorators.html#uwsgidecorators.postfork) |
| gunicorn  | `ApplicationPostFork`       | [`post_fork`](http://docs.gunicorn.org/en/latest/settings.html#post-fork) |
| gunicorn  | `ApplicationPreFork`        | [`pre_fork`](http://docs.gunicorn.org/en/latest/settings.html#pre-fork) |
| gunicorn  | `ApplicationPostWorkerInit` | [`post_worker_init`](http://docs.gunicorn.org/en/latest/settings.html#post-worker-init) |


## Status

2019.04.29 - Python3 Support. This has been production safe for uWSGI for a while now.
2016.11.09 - this is experimental


