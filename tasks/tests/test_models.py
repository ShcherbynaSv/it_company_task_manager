from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Position, Team, TaskType, Tag, Project, Task


class ModelsTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="test-position")
        self.team = Team.objects.create(name="test-team")
        self.task_type = TaskType.objects.create(name="test-task_type")
        self.tag = Tag.objects.create(name="test-tag")
        self.project = Project.objects.create(
            name="Test Project",
            description="Test description",
            team=self.team
        )
        self.username = "test-username"
        self.password = "test-password"
        self.worker = get_user_model().objects.create_user(
            username=self.username,
            password=self.password
        )
        self.task = Task.objects.create(
            name="test-task",
            description="test-description",
            deadline="2025-09-25",
            task_type=self.task_type,
            project=self.project,
        )
        self.task.assignees.set([self.worker])
        self.task.tags.set([self.tag])

    def test_position_str(self):
        self.assertEqual(str(self.position), self.position.name)

    def test_team_str(self):
        self.assertEqual(str(self.team), self.team.name)

    def test_task_type_str(self):
        self.assertEqual(str(self.task_type), self.task_type.name)

    def test_tag_str(self):
        self.assertEqual(str(self.tag), self.tag.name)

    def test_project_str(self):
        self.assertEqual(str(self.project), self.project.name)

    def test_project_get_absolute_url(self):
        expected_url = reverse("tasks:project-detail", args=[self.project.id])
        self.assertEqual(self.project.get_absolute_url(), expected_url)

    def test_worker_with_position_and_team(self):
        self.worker.position = self.position
        self.worker.team = self.team
        self.worker.save()
        self.assertEqual(self.worker.username, self.username)
        self.assertTrue(self.worker.check_password(self.password))
        self.assertEqual(self.worker.position, self.position)
        self.assertEqual(self.worker.team, self.team)

    def test_worker_get_absolute_url(self):
        expected_url = reverse("tasks:worker-detail", args=[str(self.worker.id)])
        self.assertEqual(self.worker.get_absolute_url(), expected_url)

    def test_task_str(self):
        self.assertEqual(str(self.task), self.task.name)

    def test_task_get_absolute_url(self):
        expected_url = reverse("tasks:task-detail", args=[str(self.task.id)])
        self.assertEqual(self.task.get_absolute_url(), expected_url)