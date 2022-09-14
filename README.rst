====================
flask-ligand-example
====================

|build-status| |pypi-status| |codecov-status| |pre-commit-status|

A simple example project on how to use the `flask-ligand`_ library. This example project is based on the `example`_
from the `flask-smorest`_ project. (Which is a core library that `flask-ligand`_ is built upon)

Quick Start Guide
=================

Follow the instructions below to start exploring this example project!

Prerequisites
-------------

- Python 3.10+
- virtualenvwrapper_
- Docker_ (with `Compose V2`_)

Clone Repo
----------

.. code-block:: bash

    $ git clone git@github.com:cowofevil/flask-ligand-example.git

Make Targets
------------

Execute the following command to get a full list of ``make`` targets::

    $ make help

Setup Python Environment
------------------------

1. Create a Python virtual environment::

    $ mkvirtualenv -p py310 flask-ligand-example

2. Setup develop environment::

    $ make develop-venv

3. Setup git pre-commit hooks::

    $ make setup-pre-commit

4. Verify that environment is ready for development::

    $ make test-tox

Setup Docker Environment
------------------------

The included docker environment used for integration testing can also be used for exploring the example project as well!

1. Setup the Docker environment::

    $ make setup-integration

2. Verify that the Docker environment is ready::

    $ make check-integration

3. (Optionally) Execute the integration tests::

    $ make test-integration

Explore with SwaggerUI Docs
===========================

This example project has all the bells and whistles enabled for the `flask-ligand`_ library which can be explored by
using the included `SwaggerUI`_ documentation. Follow the instuctions below to start start running a local Flask server
to serve the `SwaggerUI`_ documentation.


1. Generate a '.env' file to configure Flask server to use the included Docker environment::

    $ make gen-local-env-file

2. Generate a JWT access token with admin rights for accessing the included example project endpoints::

    $ make gen-admin-access-token

3. Initialize the database::

    $ make setup-db

4. Start the local Flask server::

    $ make run

5. Open a browser and navigate to 'http://localhost:5000/apidocs'.
6. Click the 'Authorize' button and paste in the JWT access token you created previously.

Now go ahead and start playing around with the API!

Access Keycloak Admin Console
-----------------------------

If you would like to make changes to the `Keycloak`_ IAM clients to explore authentication then you can access the
admin console by navigating to 'http://localhost:8080/admin/master/console/'. The admin credentials can be found in the
'docker/env_files/integration.env/' file.

Resources
=========

- `Changelog`_
- `Contributing`_
- `License`_

.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/en/latest/
.. _Docker: https://www.docker.com/products/docker-desktop/
.. _Compose V2: https://docs.master.dockerproject.org/compose/#compose-v2-and-the-new-docker-compose-command
.. _flask-ligand: https://flask-ligand.readthedocs.io/en/stable/
.. _flask-smorest: https://flask-smorest.readthedocs.io/en/latest/
.. _example: https://flask-smorest.readthedocs.io/en/latest/quickstart.html
.. _`SwaggerUI`: https://swagger.io/tools/swagger-ui/
.. _`Keycloak`: https://www.keycloak.org/
.. _`Changelog`: ./CHANGELOG.md
.. _`Contributing`: ./CONTRIBUTING.rst
.. _`License`: ./LICENSE

.. |build-status| image:: https://img.shields.io/github/workflow/status/cowofevil/flask-ligand-example/Build?logo=github
   :target: https://github.com/cowofevil/flask-ligand-example/actions/workflows/bump_and_publish_release.yml
   :alt: Build
.. |pypi-status| image:: https://img.shields.io/pypi/v/flask-ligand-example?color=blue&logo=pypi
   :target: https://pypi.org/project/flask-ligand-example/
   :alt: PyPI
.. |codecov-status| image:: https://img.shields.io/codecov/c/gh/cowofevil/flask-ligand-example?color=teal&logo=codecov
   :target: https://app.codecov.io/gh/cowofevil/flask-ligand-example
   :alt: Codecov
.. |pre-commit-status| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
