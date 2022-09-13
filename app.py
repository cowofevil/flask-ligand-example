"""Flask app flask_ligand_example service entrypoint."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
from sys import exit
from os import getenv
import flask_ligand_example


# ======================================================================================================================
# Globals
# ======================================================================================================================
try:
    app = flask_ligand_example.create_app(
        getenv("FLASK_ENV", "prod"),
        "Flask Ligand Example",
        flask_ligand_example.__version__,
        "flask-ligand-example-client",
    )
except RuntimeError as e:
    print(f"Service initialization failure!\nReason: {e}")
    exit(1)
