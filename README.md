pyramid_forksafe
================

This package creates standardized Pyramid events for forking hooks in popular containers.

This allows you to write generic fork routines, and easily swap containers during deployment or development.

The event will be invoked with the application's `config`, through which you can access `config.registry` and `config.registry.settings`

## Usage - Generic

Include a SPECIFIC container package in your `environment.ini` file (or main config)

	# development.ini
    pyramid.includes = pyramid_forksafe.containers.uwsgi

Define a GENERIC hook.  

    def post_fork_hook(config):
        cyrpto_atfork()
        models.engine.dispose(config)

    config.add_subscriber(post_fork_hook, ApplicationPostFork)


You can even import the generic package in your `environment.ini` file (or main config), and this will try to enable services

	# development.ini
    pyramid.includes = pyramid_forksafe


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


## Why?

Pyramid is Thread Safe, which is different than Fork Safe.

Several popular libraries are not fork-safe:

* SqlAlchemy's connection pool is not fork-safe.  Your deployment *must* call `engine.dispose()` after a fork.
* PyMongo's connections and locks are not fork-safe.  The entire client must be replaced after a fork.
* PyCrypto's Random generator will only work correctly if Random.atfork() is called.

In some situations, you may need the registry and/or settings during postfork actions; getting this information into a custom hook can be a hassle - and you may need to write against the container's API instead of Pyramid. 


## Container Support

Currently `uwsgi` and `gunicorn` are supported.   Celery is planned.  Pull requests are welcome.


## Status

2016.11.09 - this is experimental
