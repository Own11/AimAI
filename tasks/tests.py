from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Task, FailureLog
from focus.models import FocusSession
from django.test import override_settings
from .services import reschedule_overdue_tasks
from .parser import parse_task_text
from insights.models import Insight
from .models import Intervention
from rest_framework.authtoken.models import Token


class TaskFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='secret')
        self.client.force_login(self.user)
        self.task = Task.objects.create(owner=self.user, title='Спринт', due_at=timezone.now() + timedelta(hours=1), streak=2)

    def test_complete_increments_streak_and_best(self):
        self.client.post(reverse('task-complete', args=[self.task.pk]))
        self.task.refresh_from_db()
        self.assertEqual(self.task.streak, 3)
        self.assertEqual(self.task.best_streak, 3)

    def test_failure_resets_streak_and_stores_tags(self):
        response = self.client.post(reverse('failure-create', args=[self.task.pk]), {'tags': 'усталость, фокус', 'text': 'Слишком много встреч'})
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.streak, 0)
        self.assertEqual(FailureLog.objects.get().tags, ['усталость', 'фокус'])

    def test_second_failure_pauses_task(self):
        self.client.post(reverse('failure-create', args=[self.task.pk]), {'text': 'Первый пропуск'})
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.TODO)
        self.client.post(reverse('failure-create', args=[self.task.pk]), {'text': 'Второй пропуск'})
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.PAUSED)

    def test_task_api_is_scoped_to_current_user(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_analysis_creates_insight_and_intervention(self):
        FailureLog.objects.create(task=self.task, tags=['усталость'], text='Не было энергии')
        response = self.client.post(reverse('task-analyze', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Insight.objects.count(), 1)
        self.assertEqual(Intervention.objects.count(), 1)

    def test_owner_can_apply_intervention(self):
        intervention = Intervention.objects.create(task=self.task, title='Тест', description='Шаг')
        response = self.client.post(reverse('intervention-apply', args=[intervention.pk]))
        self.assertEqual(response.status_code, 302)
        intervention.refresh_from_db()
        self.assertTrue(intervention.is_applied)

    def test_focus_session_can_start_and_stop(self):
        response = self.client.post('/focus/start/', {'task_id': self.task.pk, 'duration': 25})
        self.assertEqual(response.status_code, 302)
        session = FocusSession.objects.get()
        self.assertIsNone(session.ended_at)
        response = self.client.post(f'/focus/{session.pk}/stop/')
        self.assertEqual(response.status_code, 302)
        session.refresh_from_db()
        self.assertIsNotNone(session.ended_at)

    def test_tasks_require_authentication(self):
        self.client.logout()
        response = self.client.get(reverse('task-list'))
        self.assertRedirects(response, '/accounts/login/?next=/tasks/')

    def test_overdue_task_moves_to_tomorrow(self):
        overdue = Task.objects.create(owner=self.user, title='Просрочена', due_at=timezone.now() - timedelta(hours=1))
        self.assertEqual(reschedule_overdue_tasks(self.user), 1)
        overdue.refresh_from_db()
        self.assertGreater(overdue.due_at, timezone.now())

    def test_day_plan_renders(self):
        response = self.client.get(reverse('day-plan'))
        self.assertEqual(response.status_code, 200)

    def test_parser_extracts_multiple_tasks(self):
        items = parse_task_text('сделать отчёт через 2 дня\nпозвонить через 3 часа')
        self.assertEqual(len(items), 2)
        self.assertIn('отчёт', items[0]['title'])

    def test_token_api_is_scoped_to_user(self):
        token = Token.objects.create(user=self.user)
        response = self.client.get('/api/tasks/', HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_token_api_can_complete_task(self):
        token = Token.objects.create(user=self.user)
        response = self.client.post(f'/api/tasks/{self.task.pk}/complete/', HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.DONE)


# Create your tests here.
