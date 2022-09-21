"""View modules initialization."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import annotations
from typing import TYPE_CHECKING
from flask_ligand_example.views import pet


# ======================================================================================================================
# Type Checking
# ======================================================================================================================
if TYPE_CHECKING:  # pragma: no cover
    from flask_ligand.extensions.api import Api


# ======================================================================================================================
# Globals
# ======================================================================================================================
MODULES = (pet,)


# ======================================================================================================================
# Functions: Public
# ======================================================================================================================
def register_blueprints(api: Api) -> None:
    """
    Initialize application with all modules

    Args:
        api: An initialized Api or Flask app ready to register blueprints.
    """

    for module in MODULES:
        api.register_blueprint(module.BLP)  # type: ignore
