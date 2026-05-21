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
- `Hatch 1.6+`_
- Docker_ (with `Compose V2`_)

Clone Repo
----------

.. code-block:: bash

    $ git clone git@github.com:cowofevil/flask-ligand-example.git

Setup Python Environment
------------------------

1. Navigate to your local git clone of this repository and create a Hatch 'virtualenv' environment for development::

    $ hatch env create

2. Verify development environment is working by running tests::

    $ hatch test

3. Setup git pre-commit hooks::

    $ hatch run setup-pre-commit

4. Prime 'tox' for fast testing::

    $ hatch run test-tox

5. Run tests super fast against all supported Python versions::

    $ hatch run test-tox-fast

6. Enable the Hatch 'virtualenv' development environment::

    $ hatch shell

7. Have fun hacking!

Setup Docker Environment
------------------------

The included docker environment used for integration testing can also be used for exploring the example project as well!

1. Setup the Docker environment::

    $ hatch run setup-integration

2. Verify that the Docker environment is ready::

    $ hatch run check-integration

3. (Optionally) Execute the integration tests::

    $ hatch run test-integration

Explore with SwaggerUI Docs
===========================

This example project has all the bells and whistles enabled for the `flask-ligand`_ library which can be explored by
using the included `SwaggerUI`_ documentation. Follow the instructions below to start start running a local Flask server
to serve the `SwaggerUI`_ documentation.


1. Generate a '.env' file to configure Flask server to use the included Docker environment::

    $ mhatch run gen-local-env-file

2. Initialize the database::

    $ hatch run setup-db

3. Generate a JWT access token with admin rights for accessing the included example project endpoints::

    $ hatch run gen-admin-access-token

4. Start the local Flask server::

    $ hatch run run-server

5. Open a browser and navigate to 'http://localhost:5000/apidocs'.
6. Click the 'Authorize' button and paste in the JWT access token you created previously.

Now go ahead and start playing around with the API!

Access Keycloak Admin Console
-----------------------------

If you would like to make changes to the `Keycloak`_ IAM clients to explore authentication then you can access the
admin console by navigating to 'http://localhost:8080/admin/master/console/'. The admin credentials can be found in the
'docker/env_files/integration.env/' file.

Flask-Migrate Auto-generation
=============================

For `Flask-Migrate`_ to work well when auto-generating migration scripts it is critical that the ``script.py.mako``
template in the ``migrations`` folder include an import for ``sqlalchemy_utils``. This project already has the template
updated, but if you are using the ``flask-ligand`` library without copying this example project, then it is necessary
you make the appropriate update to the ``script.py.mako`` template before using `Flask-Migrate`_.

Resources
=========

- `Changelog`_
- `Contributing`_
- `License`_

.. _Hatch 1.6+: https://hatch.pypa.io/latest/
.. _Docker: https://www.docker.com/products/docker-desktop/
.. _Compose V2: https://docs.master.dockerproject.org/compose/#compose-v2-and-the-new-docker-compose-command
.. _flask-ligand: https://flask-ligand.readthedocs.io/en/stable/
.. _flask-smorest: https://flask-smorest.readthedocs.io/en/latest/
.. _`Flask-Migrate`: https://flask-migrate.readthedocs.io/en/latest/
.. _example: https://flask-smorest.readthedocs.io/en/latest/quickstart.html
.. _`SwaggerUI`: https://swagger.io/tools/swagger-ui/
.. _`Keycloak`: https://www.keycloak.org/
.. _`Changelog`: ./CHANGELOG.md
.. _`Contributing`: ./CONTRIBUTING.rst
.. _`License`: ./LICENSE

.. |build-status| image:: https://img.shields.io/github/actions/workflow/status/cowofevil/flask-ligand-example/bump_and_publish_release.yml?branch=main&logo=github
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
