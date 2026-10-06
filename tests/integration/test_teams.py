import pytest

from app.enums import UserRole, TeamRole

pytestmark = [pytest.mark.integration]


class TestCreateTeam:
    async def test_success_returns_201(self, client, auth_headers_factory):
        headers, user = await auth_headers_factory(role=UserRole.MANAGER)

        payload = {"name": 'Test team'}

        response = await client.post('teams', json=payload, headers=headers)

        assert response.status_code == 201
        body = response.json()
        assert body['name'] == "Test team"
        assert body['owner_id'] == user.id

    async def test_unauthorized_returns_401(self, client):
        payload = {"name": 'Test team'}

        response = await client.post('teams', json=payload)

        assert response.status_code == 401

    async def test_no_permission_returns_403(self, client, auth_headers_factory):
        headers, user = await auth_headers_factory(role=UserRole.MEMBER)

        payload = {"name": 'Test team'}

        response = await client.post('teams', json=payload, headers=headers)

        assert response.status_code == 403

    async def test_empty_payload_returns_422(self, client, auth_headers_factory):
        headers, user = await auth_headers_factory(role=UserRole.MANAGER)

        response = await client.post('teams', json={}, headers=headers)

        assert response.status_code == 422


class TestGetTeam:
    async def test_all_success_returns_200(self, client,auth_headers_factory, test_team):
        headers, user = await auth_headers_factory(role=UserRole.ADMIN)
        response = await client.get('teams', headers=headers)

        assert response.status_code == 200
        teams = response.json()
        assert len(teams) == 1
        team = teams[0]
        assert team['name'] == 'Test team'
        assert team['id'] == test_team.id

    async def test_success_returns_200(self, client,auth_headers_factory, test_team):
        headers, user = await auth_headers_factory(role=UserRole.ADMIN)
        response = await client.get(f'teams/{test_team.id}', headers=headers)

        assert response.status_code == 200
        body = response.json()
        assert body['name'] == 'Test team'
        assert body['id'] == test_team.id

    async def test_not_found_returns_404(self, client, auth_headers_factory):
        headers, user = await auth_headers_factory(role=UserRole.ADMIN)
        response = await client.get(f'teams/2', headers=headers)
        assert response.status_code == 404


class TestDeleteTeam:
    async def test_admin_success(self, client, auth_headers_factory, test_team):
        headers, user = await auth_headers_factory(role=UserRole.ADMIN)

        response = await client.delete(f'teams/{test_team.id}', headers=headers)

        assert response.status_code == 204

    async def test_no_permission(self, client, auth_headers_factory, test_team):
        headers, user = await auth_headers_factory(role=UserRole.MANAGER)

        response = await client.delete(f'teams/{test_team.id}', headers=headers)

        assert response.status_code == 403

    async def test_unauthorized(self, client, auth_headers_factory, test_team):
        response = await client.delete(f'teams/{test_team.id}')
        assert response.status_code == 401


class TestJoinTeam:
    async def test_success_returns_200(self, db_session, client, auth_headers_factory, test_team):
        headers, user = await auth_headers_factory(role=UserRole.MEMBER)

        payload = {"invite_code": test_team.invite_code}

        response = await client.post(f'teams/{test_team.id}/join', json=payload, headers=headers)

        assert response.status_code == 201

        response = await client.get(f'teams/{test_team.id}/members', headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 2
        assert body[1]['id'] == user.id

    async def test_unauthorized_returns_401(self, client, test_team):
        payload = {"invite_code": test_team.invite_code}

        response = await client.post(f'teams/{test_team.id}/join', json=payload)

        assert response.status_code == 401

    async def test_empty_payload_returns_422(self, client, auth_headers_factory, test_team):
        headers, user = await auth_headers_factory(role=UserRole.MEMBER)

        response = await client.post(f'teams/{test_team.id}/join', json={}, headers=headers)

        assert response.status_code == 422


class TestRoleUpdateTeam:
    async def test_success_returns_200(self, client, auth_headers_factory, team_factory):
        headers1, user1 = await auth_headers_factory(role=UserRole.MANAGER)
        team = await team_factory(user1)

        headers2, user2 = await auth_headers_factory(role=UserRole.MEMBER)

        payload = {"invite_code": team.invite_code}
        await client.post(f'teams/{team.id}/join', json=payload, headers=headers2)

        payload = {"role": TeamRole.TESTER}
        response = await client.patch(f'teams/{team.id}/members/{user2.id}', json=payload, headers=headers1)

        assert response.status_code == 200
        body = response.json()
        assert body['role'] == TeamRole.TESTER

    async def test_unauthorized_returns_401(self, client, auth_headers_factory, team_factory):
        headers1, user1 = await auth_headers_factory(role=UserRole.MANAGER)
        team = await team_factory(user1)

        headers2, user2 = await auth_headers_factory(role=UserRole.MEMBER)

        payload = {"invite_code": team.invite_code}
        await client.post(f'teams/{team.id}/join', json=payload, headers=headers2)

        payload = {"role": TeamRole.TESTER}
        response = await client.patch(f'teams/{team.id}/members/{user2.id}', json=payload)

        assert response.status_code == 401

    async def test_empty_payload_returns_422(self, client, auth_headers_factory, team_factory):
        headers1, user1 = await auth_headers_factory(role=UserRole.MANAGER)
        team = await team_factory(user1)

        headers2, user2 = await auth_headers_factory(role=UserRole.MEMBER)

        payload = {"invite_code": team.invite_code}
        await client.post(f'teams/{team.id}/join', json=payload, headers=headers2)

        response = await client.patch(f'teams/{team.id}/members/{user2.id}', headers=headers1)
        assert response.status_code == 422

    async def test_wrong_role_returns_422(self, client, auth_headers_factory, team_factory):
        headers1, user1 = await auth_headers_factory(role=UserRole.MANAGER)
        team = await team_factory(user1)

        headers2, user2 = await auth_headers_factory(role=UserRole.MEMBER)

        payload = {"invite_code": team.invite_code}
        await client.post(f'teams/{team.id}/join', json=payload, headers=headers2)

        payload = {"role": 'asdasd'}
        response = await client.patch(f'teams/{team.id}/members/{user2.id}', json=payload, headers=headers1)
        assert response.status_code == 422


class TestMemberDelete:
    async def test_success_returns_204(self, db_session, client, auth_headers_factory, team_factory):
        headers1, user1 = await auth_headers_factory(role=UserRole.MANAGER)
        team = await team_factory(user1)

        headers2, user2 = await auth_headers_factory(role=UserRole.MEMBER)
        payload = {"invite_code": team.invite_code}
        await client.post(f'teams/{team.id}/join', json=payload, headers=headers2)

        response = await client.delete(f'teams/{team.id}/members/{user2.id}', headers=headers1)
        assert response.status_code == 204

    async def test_unauthorized_returns_401(self, client, auth_headers_factory, team_factory):
        headers1, user1 = await auth_headers_factory(role=UserRole.MANAGER)
        team = await team_factory(user1)

        headers2, user2 = await auth_headers_factory(role=UserRole.MEMBER)
        payload = {"invite_code": team.invite_code}
        await client.post(f'teams/{team.id}/join', json=payload, headers=headers2)

        response = await client.delete(f'teams/{team.id}/members/{user2.id}')
        assert response.status_code == 401

    async def test_no_permission_returns_403(self, client, auth_headers_factory, team_factory):
        headers1, user1 = await auth_headers_factory(role=UserRole.MANAGER)
        team = await team_factory(user1)

        headers2, user2 = await auth_headers_factory(role=UserRole.MEMBER)
        payload = {"invite_code": team.invite_code}
        await client.post(f'teams/{team.id}/join', json=payload, headers=headers2)

        response = await client.delete(f'teams/{team.id}/members/{user2.id}', headers=headers2)
        assert response.status_code == 403
