"""Tests for the 'openapi' API endpoint"""


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

    def test_add_pet_with_insufficient_role(self, app_test_client, pets_url, access_token_headers_no_roles):
        """
        Verify that the correct HTTP code is returned when attempting to access a protected endpoint using a JWT
        access token that doesn't have the appropriate role for specified.
        """

        pet_data = {"name": "All your base are belong to us!"}

        with app_test_client.post(pets_url, headers=access_token_headers_no_roles, json=pet_data) as ret:
            assert ret.status_code == 403
            assert ret.json["message"] == "This endpoint requires the user to have the 'user' role!"


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


class TestNegativeUpdatePets(object):
    """Negative PUT test cases for the 'pets' endpoint."""

    def test_update_pet_with_insufficient_role(
        self, app_test_client, pets_url, access_token_headers_no_roles, dummy_id, dummy_etag
    ):
        """
        Verify that the correct HTTP code is returned when attempting to access a protected endpoint using a JWT
        access token that doesn't have the appropriate role.
        """

        pet_data = {"name": "updated pet", "description": "A new and improved description!"}

        with app_test_client.put(
            f"{pets_url}{dummy_id}", headers={"If-Match": dummy_etag, **access_token_headers_no_roles}, json=pet_data
        ) as ret:
            assert ret.status_code == 403
            assert ret.json["message"] == "This endpoint requires the user to have the 'user' role!"


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

    def test_delete_pet_with_insufficient_role(
        self, app_test_client, pets_url, access_token_headers_no_roles, dummy_id, dummy_etag
    ):
        """
        Verify that the correct HTTP code is returned when attempting to access a protected endpoint using a JWT
        access token that doesn't have the appropriate role for specified.
        """

        with app_test_client.delete(
            f"{pets_url}{dummy_id}", headers={"If-Match": dummy_etag, **access_token_headers_no_roles}
        ) as ret:
            assert ret.status_code == 403
            assert ret.json["message"] == "This endpoint requires the user to have the 'admin' role!"
