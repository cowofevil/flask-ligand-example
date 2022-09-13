# ======================================================================================================================
# Imports
# ======================================================================================================================
from __future__ import annotations
import pytest
from os import walk
from os.path import join
from requests import post
from dotenv import dotenv_values
from typing import TYPE_CHECKING
from flask_migrate import downgrade
from flask.testing import FlaskClient
from flask_ligand_example import create_app

pytest_plugins = ["flask_ligand", "tests.common.fixtures"]


# ======================================================================================================================
# Type Checking
# ======================================================================================================================
if TYPE_CHECKING:
    from flask import Flask
    from typing import Any, Optional, Generator
    from pytest_flask_ligand import FlaskLigandTestHelpers


# ======================================================================================================================
# Globals
# ======================================================================================================================
MIGRATION_DIRECTORY = "migrations"


# ======================================================================================================================
# Fixtures
# ======================================================================================================================
@pytest.fixture(scope="session")
def migration_directory() -> str:
    """The path to the migrations folder used by Flask-Migrate."""

    return MIGRATION_DIRECTORY


@pytest.fixture(scope="session")
def int_testing_env_vars() -> dict[str, Optional[str]]:
    """The full bevy of integration testing environment variables stored in the 'docker/env_files/*.env' files."""

    env_vars = {}

    for root, _, files in walk("docker/env_files"):
        for file in files:
            env_vars.update(dotenv_values(join(root, file)))

    return env_vars


@pytest.fixture(scope="session")
def access_token_headers(int_testing_env_vars: dict[str, Optional[str]]) -> dict[str, Any]:
    """
    JWT access token headers ready to use for making requests against protected endpoints using the 'admin'
    composite role.
    """

    # noinspection HttpUrlsUsage
    token_url = (
        f"http://{int_testing_env_vars['KC_HOSTNAME']}:{int_testing_env_vars['KC_PORT']}/"
        f"realms/{int_testing_env_vars['KC_REALM']}/"
        "protocol/openid-connect/token"
    )
    headers = {"content-type": "application/x-www-form-urlencoded"}
    payload = (
        f"grant_type=client_credentials&"
        f"client_id={int_testing_env_vars['KC_ADMIN_CLIENT_ID']}&"
        f"client_secret={int_testing_env_vars['KC_ADMIN_CLIENT_SECRET']}"
    )

    access_token = post(token_url, data=payload, headers=headers, verify=False).json()["access_token"]

    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="session")
def access_token_headers_no_roles(int_testing_env_vars: dict[str, Optional[str]]) -> dict[str, Any]:
    """JWT access token headers that lack the necessary roles for accessing protected endpoints."""

    # noinspection HttpUrlsUsage
    token_url = (
        f"http://{int_testing_env_vars['KC_HOSTNAME']}:{int_testing_env_vars['KC_PORT']}/"
        f"realms/{int_testing_env_vars['KC_REALM']}/"
        "protocol/openid-connect/token"
    )
    headers = {"content-type": "application/x-www-form-urlencoded"}
    payload = (
        f"grant_type=client_credentials&"
        f"client_id={int_testing_env_vars['KC_NO_ROLES_CLIENT_ID']}&"
        f"client_secret={int_testing_env_vars['KC_NO_ROLES_CLIENT_SECRET']}"
    )

    access_token = post(token_url, data=payload, headers=headers, verify=False).json()["access_token"]

    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
def basic_flask_app(
    open_api_client_name: str,
    migration_directory: str,
    int_testing_env_vars: dict[str, Optional[str]],
) -> Flask:
    """A basic Flask app ready to be used for testing."""

    db_uri = (
        f"postgresql+pg8000://"
        f"{int_testing_env_vars['POSTGRES_USER']}:{int_testing_env_vars['POSTGRES_PASSWORD']}@"
        f"{int_testing_env_vars['LOCAL_HOSTNAME']}:"
        f"{int_testing_env_vars['POSTGRES_PORT']}/"
        f"{int_testing_env_vars['LOCAL_APP_DB_NAME']}"
    )

    # noinspection HttpUrlsUsage
    override_settings = {
        "OIDC_ISSUER_URL": f"http://{int_testing_env_vars['KC_HOSTNAME']}:{int_testing_env_vars['KC_PORT']}",
        "OIDC_REALM": f"{int_testing_env_vars['KC_REALM']}",
        "SQLALCHEMY_DATABASE_URI": db_uri,
        "DB_AUTO_UPGRADE": True,
        "DB_MIGRATION_DIR": migration_directory,
    }

    return create_app(
        flask_env="local",
        api_title="Flask Ligand Integration Testing Service",
        api_version="1.0.1",
        openapi_client_name=open_api_client_name,
        **override_settings,
    )


@pytest.fixture(scope="function")
def app_test_client(basic_flask_app: Flask, migration_directory: str) -> Generator[FlaskClient, None, None]:
    """Flask app test client with 'IntegrationTestView' pre-configured."""

    yield basic_flask_app.test_client()

    # Teardown
    with basic_flask_app.app_context():
        downgrade(directory=migration_directory)


@pytest.fixture(scope="function")
def primed_test_client(
    app_test_client: FlaskClient,
    pets_url: str,
    access_token_headers: dict[str, Any],
    pets_test_data_set: list[dict[str, Any]],
    helpers: FlaskLigandTestHelpers,
) -> FlaskClient:
    """Flask app configured for testing with the database pre-populated with test data."""

    for i in range(len(pets_test_data_set)):

        with app_test_client.post(pets_url, headers=access_token_headers, json=pets_test_data_set[i]) as ret:
            assert ret.status_code == 201

            # Update pets data set with id
            pets_test_data_set[i]["id"] = ret.json["id"]  # type: ignore

            # Verify pets data integrity
            assert helpers.is_sub_dict(pets_test_data_set[i], ret.json)

    return app_test_client
