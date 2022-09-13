"""Schemas for models and view queries."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
from marshmallow.validate import Length
from marshmallow_sqlalchemy import auto_field, field_for
from flask_ligand.extensions.api import AutoSchema, Schema
from flask_ligand_example.models import PetModel, NAME_MAX_LENGTH


# ======================================================================================================================
# Globals
# ======================================================================================================================
NAME_VALIDATOR: Length = Length(min=1, max=NAME_MAX_LENGTH)
DESCRIPTION_VALIDATOR: Length = Length(max=4096)


# ======================================================================================================================
# Classes: Public
# ======================================================================================================================
class PetSchema(AutoSchema):
    """Automatically generate schema from the 'Pet' model."""

    class Meta(AutoSchema.Meta):
        model = PetModel

    id = auto_field(dump_only=True)
    name = auto_field(required=True, validate=NAME_VALIDATOR)
    description = auto_field(required=False, validate=DESCRIPTION_VALIDATOR, load_default="")
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)


class PetQueryArgsSchema(Schema):
    """A schema for filtering Pets."""

    name = field_for(PetModel, "name", required=False, validate=NAME_VALIDATOR)
    description = field_for(PetModel, "description", required=False, validate=DESCRIPTION_VALIDATOR)
