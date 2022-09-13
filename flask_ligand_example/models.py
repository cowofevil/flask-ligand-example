"""Models"""

# ======================================================================================================================
# Imports
# ======================================================================================================================
import uuid
from flask_ligand.extensions.database import DB
from sqlalchemy_utils.types.uuid import UUIDType


# ======================================================================================================================
# Globals
# ======================================================================================================================
NAME_MAX_LENGTH: int = 255


# ======================================================================================================================
# Classes: Public
# ======================================================================================================================
class PetModel(DB.Model):  # type: ignore
    """Pet model class."""

    __tablename__ = "pet"

    id = DB.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = DB.Column(DB.String(length=NAME_MAX_LENGTH), nullable=False)
    description = DB.Column(DB.Text(), nullable=False)
    created_at = DB.Column(DB.DateTime, default=DB.func.current_timestamp(), nullable=False)
    updated_at = DB.Column(
        DB.DateTime, default=DB.func.current_timestamp(), onupdate=DB.func.current_timestamp(), nullable=False
    )
