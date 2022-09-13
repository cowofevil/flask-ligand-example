"""Pet endpoints."""

# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import annotations
from http import HTTPStatus
from typing import TYPE_CHECKING
from flask.views import MethodView
from flask_ligand_example.models import PetModel
from flask_ligand.extensions.database import DB
from flask_ligand.views.common.openapi_doc import BEARER_AUTH
from flask_ligand.extensions.jwt import jwt_role_required, abort
from flask_ligand.extensions.api import Blueprint, SQLCursorPage
from flask_ligand_example.schemas import PetSchema, PetQueryArgsSchema


# ======================================================================================================================
# Type Checking
# ======================================================================================================================
if TYPE_CHECKING:  # pragma: no cover
    from uuid import UUID
    from typing import Any


# ======================================================================================================================
# Globals
# ======================================================================================================================
INVALID_PET_ID = "The specified pet ID does not exist or has an invalid format!"
BLP = Blueprint(
    "Pets",
    __name__,
    url_prefix="/pets",
    description="Information about all the pets you love!",
)


# ======================================================================================================================
# Functions: Private
# ======================================================================================================================
def _we_love_pets(description: str) -> None:
    """
    Verify that the description doesn't include pet hate.

    Args:
        description: The pet description to validate.

    Raises:
        werkzeug.exceptions.HTTPException
    """

    if "hate" in description:
        abort(HTTPStatus(400), "No pet hatred allowed!")


# ======================================================================================================================
# Classes: Public
# ======================================================================================================================
@BLP.route("/")
class Pets(MethodView):
    @BLP.etag
    @BLP.arguments(PetQueryArgsSchema, location="query")
    @BLP.response(200, PetSchema(many=True))
    @BLP.paginate(SQLCursorPage)  # noqa
    def get(self, args: dict[str, Any]) -> list[PetModel]:
        """Get all pets or filter for a subset of pets."""

        items: list[PetModel] = PetModel.query.filter_by(**args)

        return items

    @BLP.etag
    @BLP.arguments(PetSchema)
    @BLP.response(201, PetSchema)
    @BLP.doc(security=BEARER_AUTH)
    @jwt_role_required(role="user")
    def post(self, new_item: dict[str, Any]) -> PetModel:
        """Add a new pet."""

        _we_love_pets(new_item["description"])

        item = PetModel(**new_item)
        DB.session.add(item)
        DB.session.commit()

        return item


@BLP.route("/<uuid:item_id>")
class PetsById(MethodView):
    @BLP.etag
    @BLP.response(200, PetSchema)
    def get(self, item_id: UUID) -> PetModel:
        """Get a pet by ID."""

        item: PetModel = PetModel.query.get_or_404(item_id, description=INVALID_PET_ID)

        return item

    @BLP.etag
    @BLP.arguments(PetSchema)
    @BLP.response(200, PetSchema)
    @BLP.doc(security=BEARER_AUTH)
    @jwt_role_required(role="user")
    def put(self, new_item: dict[str, Any], item_id: UUID) -> PetModel:
        """Update an existing pet."""

        item: PetModel = PetModel.query.get_or_404(item_id, description=INVALID_PET_ID)

        _we_love_pets(new_item["description"])

        BLP.check_etag(item, PetSchema)
        PetSchema().update(item, new_item)
        DB.session.add(item)
        DB.session.commit()

        return item

    @BLP.etag
    @BLP.response(204)
    @BLP.doc(security=BEARER_AUTH)
    @jwt_role_required(role="admin")
    def delete(self, item_id: UUID) -> None:
        """Delete a pet."""

        item: PetModel = PetModel.query.get_or_404(item_id, description=INVALID_PET_ID)

        BLP.check_etag(item, PetSchema)
        DB.session.delete(item)
        DB.session.commit()
