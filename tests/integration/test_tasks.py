import datetime

import pytest

from app.enums import UserRole, TaskStatus

pytestmark = [pytest.mark.integration]


class TestCreateTask:
    async def test_title_only_success_returns_201(self, client, auth_headers_factory, team_factory):
        headers, user = await auth_headers_factory(role=UserRole.MANAGER)

        team = await team_factory(user)

        payload = {
            'title': 'Test task'
        }

        response = await client.post(f"/teams/{team.id}/tasks", headers=headers, json=payload)

        assert response.status_code == 201
        body = response.json()
        assert body['title'] == 'Test task'
        assert body['status'] == TaskStatus.OPEN

    async def test_all_task_success_returns_201(self, client, auth_headers_factory, user_factory, team_factory):
        headers_manager, user_manager = await auth_headers_factory(role=UserRole.MANAGER)
        headers_member, user_member = await auth_headers_factory(role=UserRole.MEMBER)

        team = await team_factory(user_manager)

        payload = {
            'invite_code': team.invite_code
        }

        join_response = await client.post(f'/teams/{team.id}/join', headers=headers_member, json=payload)

        assert join_response.status_code == 201

        payload = {
            'title': 'Test task',
            'description': 'Test description',
            'assignee_id': user_member.id,
            'due_date': '2026-10-03',
        }

        response = await client.post(f"/teams/{team.id}/tasks", headers=headers_manager, json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body['title'] == 'Test task'
        assert body['description'] == 'Test description'
        assert body['status'] == TaskStatus.IN_PROGRESS
        assert body['due_date'] == '2026-10-03'
        assert body['assignee_id'] == user_member.id

    async def test_no_permission_returns_403(self, client, auth_headers_factory, team_factory):
        headers, user = await auth_headers_factory(role=UserRole.MEMBER)

        team = await team_factory(user)

        payload = {
            'title': 'Test task'
        }

        response = await client.post(f"/teams/{team.id}/tasks", headers=headers, json=payload)

        assert response.status_code == 403

    async def test_unauthorized_returns_401(self, client, auth_headers_factory, team_factory):
        headers, user = await auth_headers_factory(role=UserRole.MANAGER)

        team = await team_factory(user)

        payload = {
            'title': 'Test task'
        }

        response = await client.post(f"/teams/{team.id}/tasks", json=payload)

        assert response.status_code == 401

    async def test_another_manager_returns_403(self, client, auth_headers_factory, test_team):
        headers, user = await auth_headers_factory(role=UserRole.MANAGER)

        payload = {
            'title': 'Test task'
        }

        response = await client.post(f"/teams/{test_team.id}/tasks", headers=headers, json=payload)

        assert test_team.owner_id != user.id
        assert response.status_code == 403
        assert response.json()['detail'] == 'Вы не являетесь создателем команды'

    async def test_already_exists_returns_201(self, client, auth_headers_factory, team_factory):
        headers, user = await auth_headers_factory(role=UserRole.MANAGER)

        team = await team_factory(user)

        payload = {
            'title': 'Test task'
        }

        response1 = await client.post(f"/teams/{team.id}/tasks", headers=headers, json=payload)
        response2 = await client.post(f"/teams/{team.id}/tasks", headers=headers, json=payload)

        assert response1.status_code == 201
        body1 = response1.json()
        assert body1['title'] == 'Test task'

        assert response2.status_code == 201
        body2 = response2.json()
        assert body2['title'] == 'Test task'

    async def test_empty_payload_returns_422(self, client, auth_headers_factory, team_factory):
        headers, user = await auth_headers_factory(role=UserRole.MANAGER)

        team = await team_factory(user)

        response = await client.post(f"/teams/{team.id}/tasks", headers=headers, json={})

        assert response.status_code == 422

    async def test_wrong_team_id_returns_422(self, client, auth_headers_factory):
        headers, user = await auth_headers_factory(role=UserRole.MANAGER)
        payload = {
            'title': 'Test task'
        }
        response = await client.post(f"/teams/s/tasks", headers=headers, json=payload)

        assert response.status_code == 422

    async def test_another_team_id_returns_404(self, client, auth_headers_factory, team_factory):
        headers, user = await auth_headers_factory(role=UserRole.MANAGER)

        team = await team_factory(user)

        payload = {
            'title': 'Test task'
        }

        response = await client.post(f"/teams/{team.id+1}/tasks", headers=headers, json=payload)

        assert response.status_code == 404

class TestUpdateTask:
    async def test_title_only_success_returns_200(self, client, auth_headers_factory, team_factory, task_factory):
        headers, user = await auth_headers_factory(role=UserRole.MANAGER)

        team = await team_factory(user)

        task = await task_factory(user, team)

        updated_payload = {
            'title': 'Updated Test task'
        }

        response = await client.patch(f"tasks/{task.id}", headers=headers, json=updated_payload)

        assert response.status_code == 200
        body = response.json()
        assert body['title'] == 'Updated Test task'

    async def test_all_task_success_returns_200(self, db_session, client, auth_headers_factory, team_factory, task_factory):
        headers_manager, user_manager = await auth_headers_factory(role=UserRole.MANAGER)
        headers_member1, user_member1 = await auth_headers_factory(role=UserRole.MEMBER)

        team = await team_factory(user_manager)

        join_payload = {
            'invite_code': team.invite_code
        }

        join_response = await client.post(f'/teams/{team.id}/join', headers=headers_member1, json=join_payload)

        assert join_response.status_code == 201

        payload = {
            'title': 'Test task',
            'description': 'Test description',
            'assignee_id': user_member1.id,
            'due_date': datetime.date.today()
        }

        task = await task_factory(user_manager, team, **payload)

        assert task.title == 'Test task'
        assert task.description == 'Test description'
        assert task.due_date == datetime.date.today()
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.assignee_id == user_member1.id


        headers_member2, user_member2 = await auth_headers_factory(role=UserRole.MEMBER)

        join_response2 = await client.post(f'/teams/{team.id}/join', headers=headers_member2, json=join_payload)
        assert join_response2.status_code == 201


        updated_payload = {
            'title': 'Updated Test task',
            'description': 'Updated description',
            'assignee_id': user_member2.id,
            'due_date': '2026-10-05',
        }


        update_response = await client.patch(f"tasks/{task.id}", headers=headers_manager, json=updated_payload)

        assert update_response.status_code == 200
        body = update_response.json()
        assert body['title'] == 'Updated Test task'
        assert body['description'] == 'Updated description'
        assert body['status'] == TaskStatus.IN_PROGRESS
        assert body['due_date'] == '2026-10-05'
        assert body['assignee_id'] == user_member2.id

    async def test_no_permission_returns_403(self, client, auth_headers_factory, team_factory, task_factory):
        headers_manager, user_manager = await auth_headers_factory(role=UserRole.MANAGER)
        headers_member, user_member = await auth_headers_factory(role=UserRole.MEMBER)

        team = await team_factory(user_manager)

        join_payload = {
            'invite_code': team.invite_code
        }

        join_response = await client.post(f'/teams/{team.id}/join', headers=headers_member, json=join_payload)
        assert join_response.status_code == 201

        task = await task_factory(user_manager, team)

        updated_payload = {
            'title': 'Updated Test task'
        }
        response = await client.patch(f"tasks/{task.id}", headers=headers_member, json=updated_payload)

        assert response.status_code == 403

    async def test_unauthorized_returns_401(self, client, auth_headers_factory, team_factory, task_factory):
        headers_manager, user_manager = await auth_headers_factory(role=UserRole.MANAGER)

        team = await team_factory(user_manager)

        task = await task_factory(user_manager, team)

        updated_payload = {
            'title': 'Updated Test task'
        }
        response = await client.patch(f"tasks/{task.id}",  json=updated_payload)

        assert response.status_code == 401

    async def test_another_manager_returns_403(self, client, auth_headers_factory, team_factory, task_factory):
        headers_manager, user_manager = await auth_headers_factory(role=UserRole.MANAGER)
        header_manager2, user_manager2 = await auth_headers_factory(role=UserRole.MANAGER)

        team = await team_factory(user_manager)

        task = await task_factory(user_manager, team)

        updated_payload = {
            'title': 'Updated Test task'
        }
        response = await client.patch(f"tasks/{task.id}", headers=header_manager2, json=updated_payload)

        assert team.owner_id != user_manager2.id
        assert response.status_code == 403
        assert response.json()['detail'] == 'Вы не являетесь создателем команды'

    async def test_empty_payload_nothing_change_returns_200(self, client, auth_headers_factory, team_factory, task_factory):
        headers, user = await auth_headers_factory(role=UserRole.MANAGER)

        team = await team_factory(user)

        task = await task_factory(user, team)

        updated_payload = {}

        response = await client.patch(f"tasks/{task.id}", headers=headers, json=updated_payload)

        assert response.status_code == 200
        body = response.json()
        assert body['id'] == task.id
        assert body['title'] == task.title
        assert body['description'] == task.description
        assert body['assignee_id'] == task.assignee_id
        assert body['assignee_name'] == task.assignee_name
        assert body['status'] == task.status

    async def test_wrong_team_id_returns_422(self, client, auth_headers_factory):
        headers, user = await auth_headers_factory(role=UserRole.MANAGER)

        updated_payload = {
            'title': 'Updated Test task'
        }

        response = await client.patch(f"tasks/s", headers=headers, json=updated_payload)

        assert response.status_code == 422

    async def test_another_team_id_returns_404(self, client, auth_headers_factory, team_factory, task_factory):
        headers, user = await auth_headers_factory(role=UserRole.MANAGER)

        team = await team_factory(user)

        task = await task_factory(user, team)

        updated_payload = {
            'title': 'Updated Test task'
        }

        response = await client.patch(f"tasks/{task.id+1}", headers=headers, json=updated_payload)

        assert response.status_code == 404

