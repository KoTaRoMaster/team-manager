import pytest

pytestmark = [pytest.mark.integration]


class TestCreateUser:
    async def test_success_returns_201(self, client):
        payload = {
            'name': 'test_user',
            'email': 'test@example.com',
            'password': 'Test1234!',
            'confirm_password': 'Test1234!',
        }

        response = await client.post('auth/register', json=payload)

        assert response.status_code == 201
        body = response.json()
        assert body['name'] == payload['name']
        assert body['email'] == payload['email']

    async def test_empty_payload_returns_422(self, client):
        response = await client.post('auth/register', json={})

        assert response.status_code == 422

    async def test_different_password_returns_422(self, client):
        payload = {
            'name': 'test_user',
            'email': 'test@example.com',
            'password': 'Test1234!',
            'confirm_password': 'test1234!',
        }

        response = await client.post('auth/register', json=payload)

        assert response.status_code == 422

    async def test_wrong_email_returns_422(self, client):
        payload = {
            'name': 'test_user',
            'email': 'le.com',
            'password': 'Test1234!',
            'confirm_password': 'Test1234!',
        }

        response = await client.post('auth/register', json=payload)

        assert response.status_code == 422

    @pytest.mark.parametrize(
        'password',
        ['test1234!', 'TestTest', 'Test1'],
        ids=['no_upper_letter', 'no_number', 'len_less_than_8']
    )
    async def test_wrong_password_returns_422(self, client, password):
        payload = {
            'name': 'test_user',
            'email': 'test@example.com',
            'password': password,
            'confirm_password': password,
        }

        response = await client.post('auth/register', json=payload)

        assert response.status_code == 422

    async def test_empty_name_returns_422(self, client):
        payload = {
            'name': '',
            'email': 'test@example.com',
            'password': 'Test1234!',
            'confirm_password': 'Test1234!',
        }

        response = await client.post('auth/register', json=payload)

        assert response.status_code == 422


class TestGetUser:
    # async def test_get_all_users_success_returns_200(self, client, user_factory):
    #     user1 = await user_factory()
    #     user2 = await user_factory()
    #
    #     response = await client.get('users')
    #
    #     assert response.status_code == 200
    #     users = response.json()
    #     assert len(users) == 2
    #
    #     assert users[0]['name'] == user1.name
    #     assert users[0]['email'] == user1.email
    #
    #     assert users[1]['name'] == user2.name
    #     assert users[1]['email'] == user2.email

    # async def test_get_user_success_returns_200(self, client, user_factory):
    #     user = await user_factory()
    #
    #     response = await client.get(f'users/{user.id}')
    #
    #     assert response.status_code == 200
    #     body = response.json()
    #     assert body['name'] == user.name
    #     assert body['id'] == user.id

    async def test_get_user_not_found_returns_404(self, client):
        response = await client.get(f'users/2')
        assert response.status_code == 404
