pyramid_forksafe
================

Build Status: ![Python package](https://github.com/jvanasco/pyramid_forksafe/workflows/Python%20package/badge.svg)

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

	from pyramid_forksafe.events import ApplicationPostFork

    def post_fork_hook(event):
    	"""
    	The event has an attribute for the Pyramid Application's `registry`
    		`event.registry`
    	""""
        cyrpto_atfork()
        models.engine.dispose()

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

important note:

you MUST run uWSGI with the `--master` argument.


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

you can also update the debug tool by running after configuration:

	from pyramid_forksafe.containers.gunicorn import mark_configured
	mark_configured(config.registry)


## Container Support

Currently `uwsgi` and `gunicorn` are supported with the hooks outlined below.   Celery integration is planned.  Pull requests are very welcome.


| container | pyramid\_forksafe event      | container hook |
|-----------|-----------------------------|------|
| uWSGI     | `ApplicationPostFork`       | [`postfork`](http://uwsgi-docs.readthedocs.io/en/latest/PythonDecorators.html#uwsgidecorators.postfork) |
| gunicorn  | `ApplicationPostFork`       | [`post_fork`](http://docs.gunicorn.org/en/latest/settings.html#post-fork) |
| gunicorn  | `ApplicationPreFork`        | [`pre_fork`](http://docs.gunicorn.org/en/latest/settings.html#pre-fork) |
| gunicorn  | `ApplicationPostWorkerInit` | [`post_worker_init`](http://docs.gunicorn.org/en/latest/settings.html#post-worker-init) |


## The Debug Object

including this package will put an informative dict into `registry.pyramid_forksafe`

under waitress, it will look like this:

	[('status', 'attempting auto-configure'),
	 ('environment', None),
	 ('autoconfigure.log', ['uWSGI not available']),
	 ('executed_hooks', set([]))]

under uWSGI without master, it will look like this:

	[('status', 'uWSGI error'),
	 ('environment', None),
	 ('autoconfigure.log',
	  ['uWSGI error: you have to enable the uWSGI master process to use this module']),
	 ('executed_hooks', set([]))]

under uWSGI properly configured, it will look like this:

	[('status', 'uWSGI hook configured'),
	 ('environment', 'uWSGI'),
	 ('autoconfigure.log', ['uWSGI available', 'uWSGI hook configured']),
	 ('executed_hooks',
	  set([('containers.uwsgi.post_fork_hook', 'ApplicationPostFork')]))]


## Debugtoolbar support

to enable the debugtoobar support, you can configure your `development.ini` with:

	debugtoolbar.includes = pyramid_forksafe.debugtoolbar

The toolbar just shows the debug object `request.registry.pyramid_forksafe` on the toolbar

This should always show an error, because the debugtoolbar does not run under forking servers.



## Status
2019.05.01 - debugtoolbar
2019.04.30 - debug object
2019.04.29 - Python3 Support. This has been production safe for uWSGI for a while now.
2016.11.09 - this is experimental
