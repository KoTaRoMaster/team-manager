import datetime

import pytest

from app.enums import UserRole

pytestmark = [pytest.mark.integration]


class TestCreateMeeting:
    async def test_success_returns_201(self, client, auth_headers_factory, test_team, team_join):
        headers_org, organizer = await auth_headers_factory(UserRole.MEMBER)
        headers_par, participant = await auth_headers_factory(UserRole.MEMBER, name='Participant_1')

        await team_join(headers_org, test_team)
        await team_join(headers_par, test_team)

        starts_at = datetime.datetime.now()
        ends_at = datetime.datetime.now() + datetime.timedelta(hours=1)
        payload = {
            'title': 'Test Meeting',
            'starts_at': starts_at.strftime('%Y-%m-%d %H:%M:%S'),
            'ends_at': ends_at.strftime('%Y-%m-%d %H:%M:%S'),
            'participant_ids': [participant.id],
        }

        response = await client.post(f'/teams/{test_team.id}/meetings', headers=headers_org, json=payload)

        assert response.status_code == 201
        body = response.json()
        assert body['title'] == 'Test Meeting'
        assert body['starts_at'] == starts_at.strftime('%Y-%m-%dT%H:%M:%S')
        assert body['ends_at'] == ends_at.strftime('%Y-%m-%dT%H:%M:%S')
        assert len(body['participants']) == 2

    async def test_empty_participants_returns_201(self, client, auth_headers_factory, test_team, team_join):
        headers_org, organizer = await auth_headers_factory(UserRole.MEMBER)

        await team_join(headers_org, test_team)

        starts_at = datetime.datetime.now()
        ends_at = datetime.datetime.now() + datetime.timedelta(hours=1)
        payload = {
            'title': 'Test Meeting',
            'starts_at': starts_at.strftime('%Y-%m-%d %H:%M:%S'),
            'ends_at': ends_at.strftime('%Y-%m-%d %H:%M:%S'),
            'participant_ids': [],
        }

        response = await client.post(f'/teams/{test_team.id}/meetings', headers=headers_org, json=payload)

        assert response.status_code == 201

    async def test_unauthorized_returns_401(self, client, test_team):
        starts_at = datetime.datetime.now()
        ends_at = datetime.datetime.now() + datetime.timedelta(hours=1)
        payload = {
            'title': 'Test Meeting',
            'starts_at': starts_at.strftime('%Y-%m-%d %H:%M:%S'),
            'ends_at': ends_at.strftime('%Y-%m-%d %H:%M:%S'),
            'participant_ids': [],
        }
        response = await client.post(f'/teams/{test_team.id}/meetings', json=payload)

        assert response.status_code == 401

    async def test_empty_payload_returns_422(self, client, auth_headers_factory, test_team):
        headers_org, organizer = await auth_headers_factory(UserRole.MEMBER)

        response = await client.post(f'/teams/{test_team.id}/meetings', headers=headers_org)

        assert response.status_code == 422
        body = response.json()
        assert body['detail'][0]['message'] == 'Field required'

    async def test_wrong_team_id_returns_422(self, client, auth_headers_factory, test_team):
        headers_org, organizer = await auth_headers_factory(UserRole.MEMBER)

        response = await client.post(f'/teams/s/meetings', headers=headers_org)

        assert response.status_code == 422
        body = response.json()
        assert body['detail'][0]['message'] == 'Input should be a valid integer, unable to parse string as an integer'

    async def test_not_found_returns_404(self, client, auth_headers_factory, test_team):
        headers_org, organizer = await auth_headers_factory(UserRole.MEMBER)

        starts_at = datetime.datetime.now()
        ends_at = datetime.datetime.now() + datetime.timedelta(hours=1)
        payload = {
            'title': 'Test Meeting',
            'starts_at': starts_at.strftime('%Y-%m-%d %H:%M:%S'),
            'ends_at': ends_at.strftime('%Y-%m-%d %H:%M:%S'),
            'participant_ids': [],
        }

        response = await client.post(f'/teams/{test_team.id + 1}/meetings', headers=headers_org, json=payload)

        assert response.status_code == 404
        body = response.json()
        assert body['detail'] == f'team_id с id={test_team.id + 1} не найден'

    async def test_organizer_not_in_team_returns_403(self, client, auth_headers_factory, test_team, team_join):
        headers_org, organizer = await auth_headers_factory(UserRole.MEMBER)
        headers_par, participant = await auth_headers_factory(UserRole.MEMBER, name='Participant_1')

        await team_join(headers_par, test_team)

        starts_at = datetime.datetime.now()
        ends_at = datetime.datetime.now() + datetime.timedelta(hours=1)
        payload = {
            'title': 'Test Meeting',
            'starts_at': starts_at.strftime('%Y-%m-%d %H:%M:%S'),
            'ends_at': ends_at.strftime('%Y-%m-%d %H:%M:%S'),
            'participant_ids': [participant.id],
        }

        response = await client.post(f'/teams/{test_team.id}/meetings', headers=headers_org, json=payload)

        assert response.status_code == 403
        body = response.json()
        assert body['detail'] == f'Пользователь с id={organizer.id} не является членом команды с id={test_team.id}'

    async def test_participant_not_in_team_returns_400(self, client, auth_headers_factory, test_team, team_join):
        headers_org, organizer = await auth_headers_factory(UserRole.MEMBER)
        headers_par, participant = await auth_headers_factory(UserRole.MEMBER, name='Participant_1')

        await team_join(headers_org, test_team)

        starts_at = datetime.datetime.now()
        ends_at = datetime.datetime.now() + datetime.timedelta(hours=1)
        payload = {
            'title': 'Test Meeting',
            'starts_at': starts_at.strftime('%Y-%m-%d %H:%M:%S'),
            'ends_at': ends_at.strftime('%Y-%m-%d %H:%M:%S'),
            'participant_ids': [participant.id],
        }

        response = await client.post(f'/teams/{test_team.id}/meetings', headers=headers_org, json=payload)

        assert response.status_code == 400
        body = response.json()
        assert body['detail'] == f'Пользователи не состоят в этой команде: {[participant.id]}'

    async def test_overlaps_meetings_returns_409(self, client, auth_headers_factory, test_team, team_join):
        headers_org, organizer = await auth_headers_factory(UserRole.MEMBER)
        headers_par, participant = await auth_headers_factory(UserRole.MEMBER, name='Participant_1')

        await team_join(headers_org, test_team)
        await team_join(headers_par, test_team)

        starts_at = datetime.datetime.now()
        ends_at = datetime.datetime.now() + datetime.timedelta(hours=1)
        payload = {
            'title': 'Test Meeting',
            'starts_at': starts_at.strftime('%Y-%m-%d %H:%M:%S'),
            'ends_at': ends_at.strftime('%Y-%m-%d %H:%M:%S'),
            'participant_ids': [participant.id],
        }

        response = await client.post(f'/teams/{test_team.id}/meetings', headers=headers_org, json=payload)
        assert response.status_code == 201
        update_payload = {
            'starts_at': (starts_at + datetime.timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S'),
            'ends_at': (ends_at + datetime.timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S'),
        }
        payload.update(**update_payload)
        response = await client.post(f'/teams/{test_team.id}/meetings', headers=headers_org, json=payload)

        assert response.status_code == 409
        body = response.json()
        assert body['detail'] == f'У сотрудников {[organizer.id, participant.id]} уже назначены встречи в это время'


class TestCancelMeeting:
    async def test_success_returns_204(self, client, auth_headers_factory, test_team, team_join, meeting_factory):
        headers_org, organizer = await auth_headers_factory(UserRole.MEMBER)
        headers_par, participant = await auth_headers_factory(UserRole.MEMBER)

        await team_join(headers_org, test_team)
        await team_join(headers_par, test_team)

        meeting = await meeting_factory(organizer, test_team, participant_ids=[participant.id])

        response = await client.delete(f'/teams/{test_team.id}/meetings/{meeting.id}', headers=headers_org)

        assert response.status_code == 204

        response = await client.get(f'/teams/{test_team.id}/meetings', headers=headers_org)

        assert response.status_code == 200
        body = response.json()
        assert body == []

    async def test_participant_returns_403(self, client, auth_headers_factory, test_team, team_join, meeting_factory):
        headers_org, organizer = await auth_headers_factory(UserRole.MEMBER)
        headers_par, participant = await auth_headers_factory(UserRole.MEMBER)

        await team_join(headers_org, test_team)
        await team_join(headers_par, test_team)

        meeting = await meeting_factory(organizer, test_team, participant_ids=[participant.id])

        response = await client.delete(f'/teams/{test_team.id}/meetings/{meeting.id}', headers=headers_par)

        assert response.status_code == 403

        response = await client.get(f'/teams/{test_team.id}/meetings', headers=headers_org)

        assert response.status_code == 200
        body = response.json()
        assert body != []

    async def test_no_permission_returns_403(self, client, auth_headers_factory, test_team, team_join, meeting_factory):
        headers_org, organizer = await auth_headers_factory(UserRole.MEMBER)
        headers_par, participant = await auth_headers_factory(UserRole.MEMBER)

        await team_join(headers_org, test_team)
        await team_join(headers_par, test_team)

        meeting = await meeting_factory(organizer, test_team, participant_ids=[participant.id])

        response = await client.delete(f'/teams/{test_team.id}/meetings/{meeting.id}', headers=headers_par)

        assert response.status_code == 403

        response = await client.get(f'/teams/{test_team.id}/meetings', headers=headers_org)

        assert response.status_code == 200
        body = response.json()
        assert body != []
