import datetime

from app.enums import UserRole, TaskStatus


class TestGetCalendar:
    async def test_success_returns_200(self, client, auth_headers_factory, team_factory, task_factory, team_join,
                                       meeting_factory, db_session):
        headers_manager, manager = await auth_headers_factory(UserRole.MANAGER, name='manager')
        headers_member, member = await auth_headers_factory(UserRole.MEMBER, name='member')

        team = await team_factory(manager)

        await team_join(headers_member, team)

        task_data = {
            'assignee_id': member.id,
            'due_date': datetime.date.today() + datetime.timedelta(days=1),
        }

        task = await task_factory(manager, team, **task_data)
        meeting = await meeting_factory(manager, team, [member.id])

        from_ = datetime.date.today()
        to_ = datetime.date.today() + datetime.timedelta(days=1)

        response = await client.get(f"/calendar?from={from_}&to={to_}", headers=headers_member)
        assert response.status_code == 200
        body = response.json()
        assert body['from_date'] == from_.strftime('%Y-%m-%d')
        assert body['to_date'] == to_.strftime('%Y-%m-%d')

        assert len(body['tasks']) == 1
        assert body['tasks'][0]['id'] == task.id
        assert body['tasks'][0]['title'] == task.title
        assert body['tasks'][0]['status'] == TaskStatus.IN_PROGRESS

        assert len(body['meetings']) == 1
        assert body['meetings'][0]['id'] == meeting.id
        assert body['meetings'][0]['title'] == meeting.title

    async def test_date_incorrect_returns_404(self, client, auth_headers_factory, team_factory, task_factory):
        headers, user = await auth_headers_factory(UserRole.MANAGER)
        from_ = datetime.date.today()
        to_ = datetime.date.today() - datetime.timedelta(days=1)
        response = await client.get(f"/calendar?from={from_}&to={to_}", headers=headers)

        assert response.status_code == 404
        body = response.json()
        assert body['detail'] == "'from' не может быть позже 'to'"
