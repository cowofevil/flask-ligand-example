"""Tests for the 'openapi' API endpoint"""

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest


# ======================================================================================================================
# Test Suites
# ======================================================================================================================
class TestGetPets(object):
    """GET test cases for the 'pets' endpoint."""

    def test_get_all_pets(
        self,
        primed_test_client,
        pets_url,
        access_token_headers,
        pets_test_data_set,
        iso_8601_datetime_rgx,
        helpers,
    ):
        """Verify that the endpoint returns all pets."""

        with primed_test_client.get(pets_url, headers=access_token_headers) as ret:
            assert ret.status_code == 200
            assert len(ret.json) == 3

            for i in range(3):
                assert helpers.is_sub_dict(pets_test_data_set[i], ret.json[i])

                # Verify datetime format only.
                assert iso_8601_datetime_rgx.match(ret.json[i]["created_at"])
                assert iso_8601_datetime_rgx.match(ret.json[i]["updated_at"])

    def test_get_pets_with_pagination(
        self,
        primed_test_client,
        pets_url,
        access_token_headers,
        helpers,
    ):
        """Verify that the endpoint supports pagination."""

        with primed_test_client.get(f"{pets_url}?page=1&page_size=2", headers=access_token_headers) as ret:
            assert ret.status_code == 200
            assert len(ret.json) == 2

            assert helpers.loads(ret.headers["X-Pagination"])["total"] == 3
            assert helpers.loads(ret.headers["X-Pagination"])["total_pages"] == 2

    def test_filter_pets_by_name(self, primed_test_client, pets_url, access_token_headers, pets_test_data_set, helpers):
        """Verify that a pet can be retrieved by pet name."""

        pet_exp = pets_test_data_set[0]

        with primed_test_client.get(f"{pets_url}?name={pet_exp['name']}", headers=access_token_headers) as ret:
            assert ret.status_code == 200
            assert len(ret.json) == 1
            assert helpers.is_sub_dict(pet_exp, ret.json[0])

    def test_filter_pets_by_desc(self, primed_test_client, pets_url, access_token_headers, pets_test_data_set, helpers):
        """Verify that a pet can be retrieved by pet description."""

        pet_exp = pets_test_data_set[0]

        with primed_test_client.get(
            f"{pets_url}?description={pet_exp['description']}", headers=access_token_headers
        ) as ret:
            assert ret.status_code == 200
            assert len(ret.json) == 1
            assert helpers.is_sub_dict(pet_exp, ret.json[0])

    def test_get_pet_by_id(self, primed_test_client, pets_url, access_token_headers, pets_test_data_set, helpers):
        """Verify that a pet can be retrieved by ID."""

        pet_exp = pets_test_data_set[0]
        # Mini-test to make sure the names and IDs are aligned in the test data set.
        pet_id_exp = primed_test_client.get(
            f"{pets_url}?name={pets_test_data_set[0]['name']}", headers=access_token_headers
        ).json[0]["id"]

        with primed_test_client.get(f"{pets_url}{pet_id_exp}", headers=access_token_headers) as ret:
            assert ret.status_code == 200
            assert helpers.is_sub_dict(pet_exp, ret.json)


class TestNegativeGetPets(object):
    """Negative GET test cases for the 'pets' endpoint."""

    def test_filter_pets_no_results(self, primed_test_client, pets_url, access_token_headers):
        """Verify that a filter specifying a value that does not exist returns no results."""

        with primed_test_client.get(f"{pets_url}?name=does_not_exist", headers=access_token_headers) as ret:
            assert ret.status_code == 200
            assert len(ret.json) == 0

    def test_get_pet_by_id_with_invalid_id(
        self, primed_test_client, pets_url, access_token_headers, dummy_id, invalid_pet_id_error_msg
    ):
        """Verify that the correct HTTP code is returned when an invalid ID is specified."""

        with primed_test_client.get(f"{pets_url}{dummy_id}", headers=access_token_headers) as ret:
            assert ret.status_code == 404
            assert ret.json["message"] == invalid_pet_id_error_msg


class TestAddPets(object):
    """POST test cases for the 'pets' endpoint."""

    def test_add_pets(self, primed_test_client):
        """Verify that pets can be added."""

        assert primed_test_client

    @pytest.mark.parametrize("name", ["a", "a" * 255])
    def test_add_pet_with_name_boundary_check(self, name, app_test_client, pets_url, access_token_headers, helpers):
        """Verify that a pet can be added with a minimal and maximal allowable name length."""

        pet_exp = {"name": name, "description": "a description"}

        with app_test_client.post(pets_url, headers=access_token_headers, json=pet_exp) as ret:
            assert ret.status_code == 201
            assert helpers.is_sub_dict(pet_exp, ret.json)

    @pytest.mark.parametrize("desc", ["", "a" * 4096])
    def test_add_pet_with_desc_boundary_check(self, desc, app_test_client, pets_url, access_token_headers, helpers):
        """Verify that a pet can be added with a minimal and maximal allowable description length."""

        pet_exp = {"name": "a", "description": desc}

        with app_test_client.post(pets_url, headers=access_token_headers, json=pet_exp) as ret:
            assert ret.status_code == 201
            assert helpers.is_sub_dict(pet_exp, ret.json)

    def test_add_pet_with_only_required(self, app_test_client, pets_url, access_token_headers):
        """Verify that a pet can be updated while only specifying required fields."""

        pet_exp = {"name": "a fun pet name!"}

        with app_test_client.post(pets_url, headers=access_token_headers, json=pet_exp) as ret:
            assert ret.status_code == 201
            assert ret.json["description"] == ""


class TestNegativeAddPets(object):
    """Negative POST test cases for the 'pets' endpoint."""

    def test_add_pet_without_access_token(self, app_test_client, pets_url):
        """
        Verify that the correct HTTP code is returned when attempting to access a protected endpoint without a JWT
        access token.
        """

        pet_data = {"name": "All your base are belong to us!"}

        with app_test_client.post(pets_url, json=pet_data) as ret:
            assert ret.status_code == 401
            assert ret.json["message"] == "Missing Authorization Header"

    # noinspection PyTestParametrized
    @pytest.mark.parametrize("default_roles", ["insufficient_role"])
    def test_add_pet_with_insufficient_role(self, app_test_client, pets_url, access_token_headers):
        """
        Verify that the correct HTTP code is returned when attempting to access a protected endpoint using a JWT
        access token that doesn't have the appropriate role for specified.

        Note: This test does a trick with parameterization to override the implicitly imported "default_roles"
        fixture. See this documentation for more details:

        https://docs.pytest.org/en/6.2.x/fixture.html#override-a-fixture-with-direct-test-parametrization
        """

        pet_data = {"name": "All your base are belong to us!"}

        with app_test_client.post(pets_url, headers=access_token_headers, json=pet_data) as ret:
            assert ret.status_code == 403
            assert ret.json["message"] == "This endpoint requires the user to have the 'user' role!"

    def test_add_pet_with_invalid_data(self, app_test_client, pets_url, access_token_headers):
        """Verify that the correct HTTP code is returned when an invalid data is sent."""

        pet_data = {"not": "valid"}

        with app_test_client.post(pets_url, headers=access_token_headers, json=pet_data) as ret:
            assert ret.status_code == 422

    def test_add_pet_with_disallowed_desc(self, app_test_client, pets_url, access_token_headers):
        """Verify that the correct HTTP code is returned when the description contains a disallowed content."""

        pet_data = {"name": "A bag of spiders", "description": "I hate this pet!"}

        with app_test_client.post(pets_url, headers=access_token_headers, json=pet_data) as ret:
            assert ret.status_code == 400
            assert ret.json["message"] == "No pet hatred allowed!"

    @pytest.mark.parametrize("name", ["", "a" * 256])
    def test_add_pet_with_name_neg_boundary_check(self, name, app_test_client, pets_url, access_token_headers):
        """Verify that the correct HTTP code is returned when the name is outside the allowable length."""

        pet_data = {"name": name, "description": "a reasonable description"}

        with app_test_client.post(pets_url, headers=access_token_headers, json=pet_data) as ret:
            assert ret.status_code == 422

    def test_add_pet_with_excessive_desc_length(self, app_test_client, pets_url, access_token_headers):
        """Verify that the correct HTTP code is returned when the length of the description is too long."""

        pet_data = {"name": "a nifty name", "description": "a" * 4097}

        with app_test_client.post(pets_url, headers=access_token_headers, json=pet_data) as ret:
            assert ret.status_code == 422

    def test_add_pet_with_extra_data(self, app_test_client, pets_url, access_token_headers):
        """Verify that the correct HTTP code is returned when the JSON body contains extraneous data."""

        pet_data = {"name": "a nifty name", "description": "a respectable description", "extra": "data"}

        with app_test_client.post(pets_url, headers=access_token_headers, json=pet_data) as ret:
            assert ret.status_code == 422


class TestUpdatePets(object):
    """PUT test cases for the 'pets' endpoint."""

    def test_update_pet(self, primed_test_client, pets_url, access_token_headers, pets_test_data_set, helpers):
        """Verify that a pet can be updated."""

        pet_id = pets_test_data_set[0]["id"]
        pet_etag = primed_test_client.get(f"{pets_url}{pet_id}", headers=access_token_headers).headers["ETag"]
        pet_exp = {"name": "updated pet", "description": "A new and improved description!"}
        old_update_time = helpers.parse_iso_str(
            primed_test_client.get(pets_url, headers=access_token_headers).json[0]["updated_at"]
        )

        # Wait one second to get a differential in update time.
        helpers.wait(1)

        with primed_test_client.put(
            f"{pets_url}{pet_id}", headers={"If-Match": pet_etag, **access_token_headers}, json=pet_exp
        ) as ret:
            assert ret.status_code == 200

        with primed_test_client.get(f"{pets_url}{pet_id}", headers=access_token_headers) as ret:
            assert ret.status_code == 200
            assert helpers.is_sub_dict(pet_exp, ret.json)

            # Verify that update time has changed.
            assert helpers.parse_iso_str(ret.json["updated_at"]) > old_update_time

    def test_update_pet_with_only_required(
        self, primed_test_client, pets_url, access_token_headers, pets_test_data_set, helpers
    ):
        """Verify that a pet can be updated while only specifying required fields."""

        pet_id = pets_test_data_set[0]["id"]
        pet_etag = primed_test_client.get(f"{pets_url}{pet_id}", headers=access_token_headers).headers["ETag"]
        pet_exp = {"name": "updated pet"}

        with primed_test_client.put(
            f"{pets_url}{pet_id}", headers={"If-Match": pet_etag, **access_token_headers}, json=pet_exp
        ) as ret:
            assert ret.status_code == 200

        with primed_test_client.get(f"{pets_url}{pet_id}", headers=access_token_headers) as ret:
            assert ret.status_code == 200
            assert helpers.is_sub_dict(pet_exp, ret.json)

            # Verify that non-required fields return correct default values.
            assert ret.json["description"] == ""


class TestNegativeUpdatePets(object):
    """Negative PUT test cases for the 'pets' endpoint.

    NOTE: Intentionally omitting tests for testing data validation beyond invalid since updating pets uses the same
    schema as adding pets. Proving that data validation works in one scenario is enough to prove the correct schema
    has been applied to the endpoint.
    """

    def test_update_pet_without_access_token(self, app_test_client, pets_url, dummy_id, dummy_etag):
        """
        Verify that the correct HTTP code is returned when attempting to access a protected endpoint without a JWT
        access token.
        """

        pet_data = {"name": "updated pet", "description": "A new and improved description!"}

        with app_test_client.put(f"{pets_url}{dummy_id}", headers={"If-Match": dummy_etag}, json=pet_data) as ret:
            assert ret.status_code == 401
            assert ret.json["message"] == "Missing Authorization Header"

    # noinspection PyTestParametrized
    @pytest.mark.parametrize("default_roles", ["insufficient_role"])
    def test_update_pet_with_insufficient_role(
        self, app_test_client, pets_url, access_token_headers, dummy_id, dummy_etag
    ):
        """
        Verify that the correct HTTP code is returned when attempting to access a protected endpoint using a JWT
        access token that doesn't have the appropriate role.

        Note: This test does a trick with parameterization to override the implicitly imported "default_roles"
        fixture. See this documentation for more details:

        https://docs.pytest.org/en/6.2.x/fixture.html#override-a-fixture-with-direct-test-parametrization
        """

        pet_data = {"name": "updated pet", "description": "A new and improved description!"}

        with app_test_client.put(
            f"{pets_url}{dummy_id}", headers={"If-Match": dummy_etag, **access_token_headers}, json=pet_data
        ) as ret:
            assert ret.status_code == 403
            assert ret.json["message"] == "This endpoint requires the user to have the 'user' role!"

    def test_update_non_existent_pet(
        self,
        primed_test_client,
        pets_url,
        access_token_headers,
        pets_test_data_set,
        dummy_id,
        invalid_pet_id_error_msg,
    ):
        """Verify that the correct HTTP code is returned when attempting to update a pet that doesn't exist."""

        pet_id = pets_test_data_set[0]["id"]
        pet_etag = primed_test_client.get(f"{pets_url}{pet_id}", headers=access_token_headers).headers["ETag"]
        pet_data = {"name": "updated pet", "description": "A new and improved description!"}

        with primed_test_client.put(
            f"{pets_url}{dummy_id}", headers={"If-Match": pet_etag, **access_token_headers}, json=pet_data
        ) as ret:
            assert ret.status_code == 404
            assert ret.json["message"] == invalid_pet_id_error_msg

    def test_update_pet_with_invalid_data(self, primed_test_client, pets_url, access_token_headers, pets_test_data_set):
        """Verify that the correct HTTP code is returned when attempting to update the pet with invalid data."""

        pet_id = pets_test_data_set[0]["id"]
        pet_etag = primed_test_client.get(f"{pets_url}{pet_id}", headers=access_token_headers).headers["ETag"]
        pet_data = {"not": "valid"}

        with primed_test_client.put(
            f"{pets_url}{pet_id}", headers={"If-Match": pet_etag, **access_token_headers}, json=pet_data
        ) as ret:
            assert ret.status_code == 422

    def test_update_pet_with_disallowed_desc(
        self, primed_test_client, pets_url, access_token_headers, pets_test_data_set
    ):
        """Verify that the correct HTTP code is returned when the description contains a disallowed content."""

        pet_id = pets_test_data_set[0]["id"]
        pet_etag = primed_test_client.get(f"{pets_url}{pet_id}", headers=access_token_headers).headers["ETag"]
        pet_data = {"name": "A bag of spiders", "description": "I hate this pet!"}

        with primed_test_client.put(
            f"{pets_url}{pet_id}", headers={"If-Match": pet_etag, **access_token_headers}, json=pet_data
        ) as ret:
            assert ret.status_code == 400
            assert ret.json["message"] == "No pet hatred allowed!"

    def test_update_pet_without_etag(self, primed_test_client, pets_url, access_token_headers, pets_test_data_set):
        """Verify that the correct HTTP code is returned when attempting to update a pet without an ETag header."""

        pet_id = pets_test_data_set[0]["id"]
        pet_data = {"name": "updated pet", "description": "A new and improved description!"}

        with primed_test_client.put(f"{pets_url}{pet_id}", headers=access_token_headers, json=pet_data) as ret:
            assert ret.status_code == 428

    def test_update_pet_with_invalid_etag(
        self, primed_test_client, pets_url, access_token_headers, pets_test_data_set, dummy_etag
    ):
        """
        Verify that the correct HTTP code is returned when attempting to update a pet with an invalid ETag
        header.
        """

        pet_id = pets_test_data_set[0]["id"]
        pet_data = {"name": "updated pet", "description": "A new and improved description!"}

        with primed_test_client.put(
            f"{pets_url}{pet_id}", json=pet_data, headers={"If-Match": dummy_etag, **access_token_headers}
        ) as ret:
            assert ret.status_code == 412


class TestDeletePets(object):
    """DELETE test cases for the 'pets' endpoint."""

    def test_delete_pet(self, primed_test_client, pets_url, access_token_headers, pets_test_data_set):
        """Verify that a pet can be deleted."""

        pet_id = pets_test_data_set[0]["id"]
        pet_etag = primed_test_client.get(f"{pets_url}{pet_id}", headers=access_token_headers).headers["ETag"]

        with primed_test_client.delete(
            f"{pets_url}{pet_id}", headers={"If-Match": pet_etag, **access_token_headers}
        ) as ret:
            assert ret.status_code == 204

        with primed_test_client.get(f"{pets_url}{pet_id}", headers=access_token_headers) as ret:
            assert ret.status_code == 404


class TestNegativeDeletePets(object):
    """Negative DELETE test cases for the 'pets' endpoint."""

    def test_delete_pet_without_access_token(
        self, app_test_client, pets_url, access_token_headers, dummy_id, dummy_etag
    ):
        """
        Verify that the correct HTTP code is returned when attempting to access a protected endpoint without a JWT
        access token.
        """

        with app_test_client.delete(f"{pets_url}{dummy_id}", headers={"If-Match": dummy_etag}) as ret:
            assert ret.status_code == 401
            assert ret.json["message"] == "Missing Authorization Header"

    # noinspection PyTestParametrized
    @pytest.mark.parametrize("default_roles", ["user"])
    def test_delete_pet_with_insufficient_role(
        self, app_test_client, pets_url, access_token_headers, dummy_id, dummy_etag
    ):
        """
        Verify that the correct HTTP code is returned when attempting to access a protected endpoint using a JWT
        access token that doesn't have the appropriate role for specified.

        Note: This test does a trick with parameterization to override the implicitly imported "default_roles"
        fixture. See this documentation for more details:

        https://docs.pytest.org/en/6.2.x/fixture.html#override-a-fixture-with-direct-test-parametrization
        """

        with app_test_client.delete(
            f"{pets_url}{dummy_id}", headers={"If-Match": dummy_etag, **access_token_headers}
        ) as ret:
            assert ret.status_code == 403
            assert ret.json["message"] == "This endpoint requires the user to have the 'admin' role!"

    def test_delete_non_existent_pet(
        self,
        primed_test_client,
        pets_url,
        access_token_headers,
        pets_test_data_set,
        dummy_id,
        invalid_pet_id_error_msg,
    ):
        """Verify that the correct HTTP code is returned when attempting to delete a pet that doesn't exist."""

        pet_id = pets_test_data_set[0]["id"]
        pet_etag = primed_test_client.get(f"{pets_url}{pet_id}", headers=access_token_headers).headers["ETag"]

        with primed_test_client.delete(
            f"{pets_url}{dummy_id}", headers={"If-Match": pet_etag, **access_token_headers}
        ) as ret:
            assert ret.status_code == 404
            assert ret.json["message"] == invalid_pet_id_error_msg

        with primed_test_client.get(pets_url, headers=access_token_headers) as ret:
            assert ret.status_code == 200
            assert len(ret.json) == 3

    def test_delete_without_etag(self, primed_test_client, pets_url, access_token_headers, pets_test_data_set):
        """Verify that the correct HTTP code is returned when attempting to delete a pet without an ETag header."""

        pet_id = pets_test_data_set[0]["id"]

        with primed_test_client.delete(f"{pets_url}{pet_id}", headers=access_token_headers) as ret:
            assert ret.status_code == 428

        with primed_test_client.get(pets_url, headers=access_token_headers) as ret:
            assert ret.status_code == 200
            assert len(ret.json) == 3

    def test_update_with_invalid_etag(
        self, primed_test_client, pets_url, access_token_headers, pets_test_data_set, dummy_etag
    ):
        """
        Verify that the correct HTTP code is returned when attempting to update a pet with an invalid ETag
        header.
        """

        pet_id = pets_test_data_set[0]["id"]

        with primed_test_client.delete(
            f"{pets_url}{pet_id}", headers={"If-Match": dummy_etag, **access_token_headers}
        ) as ret:
            assert ret.status_code == 412

        with primed_test_client.get(pets_url, headers=access_token_headers) as ret:
            assert ret.status_code == 200
            assert len(ret.json) == 3
