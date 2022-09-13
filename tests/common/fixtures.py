# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import annotations
import pytest
from typing import TYPE_CHECKING
from flask_ligand_example.views.pet import INVALID_PET_ID


# ======================================================================================================================
# Type Checking
# ======================================================================================================================
if TYPE_CHECKING:
    from typing import Any


# ======================================================================================================================
# Globals
# ======================================================================================================================
PETS_URL = "/pets/"


# ======================================================================================================================
# Fixtures: Public
# ======================================================================================================================
@pytest.fixture(scope="session")
def pets_url() -> str:
    """The URL for the 'pets' API endpoint."""

    return PETS_URL


@pytest.fixture(scope="function")
def pets_test_data_set() -> list[dict[str, Any]]:
    """Test data set for the 'pets' endpoint."""

    data_set = [{"name": f"pet_name_{i}", "description": f"pet_description_{i}"} for i in range(3)]

    return data_set


@pytest.fixture(scope="session")
def invalid_pet_id_error_msg() -> str:
    """
    The expected error message returned when a non-existent pet ID is specified.

    NOTE: This is referenced to the originating module since we only care about a custom message being returned and
    not the contents of the message.
    """

    return INVALID_PET_ID
