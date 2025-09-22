
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib import admin
from django.utils.formats import date_format

from django.utils import timezone

from tasks.admin import ProjectAdmin, WorkerAdmin
from tasks.models import Project, Team, Task, TaskType, Position, Worker


class AdmitSiteTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            password="admin1234"
        )
        self.client.force_login(self.admin_user)
        self.team = Team.objects.create(name="test-team")
        self.position = Position.objects.create(name="test-position")
        self.worker = get_user_model().objects.create_user(
            username="test-user",
            password="user1234",
            position=self.position,
            team = self.team
        )

        self.project = Project.objects.create(
            name="test-project",
            description="test-description",
            team=self.team
        )
        self.task_type = TaskType.objects.create(name="test-task_type")
        self.task = Task.objects.create(
            name="test-task",
            description="test-description",
            deadline=timezone.now() + timezone.timedelta(days=5),
            task_type=self.task_type,
            project=self.project
        )

    def test_project_list_display(self):
        url = reverse("admin:tasks_project_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.project.name)
        self.assertContains(res, self.project.created_at.strftime("%Y-%m-%d"))
        self.assertContains(res, self.project.description)
        self.assertContains(res, str(self.project.team))

    def test_project_list_filter(self):
        model_admin = ProjectAdmin(Project, admin.site)
        self.assertEqual(model_admin.list_filter, ["name", "created_at", "team"])

    def test_project_search_fields(self):
        model_admin = ProjectAdmin(Project, admin.site)
        self.assertEqual(model_admin.search_fields, ["name"])

    def test_worker_list_display(self):
        url = reverse("admin:tasks_worker_changelist")
        res = self.client.get(url)

        self.assertContains(res, str(self.worker.team))
        self.assertContains(res, str(self.worker.position))

    def test_worker_list_filter(self):
        model_admin = WorkerAdmin(Worker, admin.site)
        self.assertEqual(
            model_admin.list_filter,
            ("is_staff", "is_superuser", "is_active", "groups", "position", "team")
        )

    def test_worker_fieldsets_contains_additional_info(self):
        model_admin = WorkerAdmin(Worker, admin.site)
        fieldsets = dict(model_admin.fieldsets)
        self.assertIn("Additional info", fieldsets)
        self.assertIn("position", fieldsets["Additional info"]["fields"])
        self.assertIn("team", fieldsets["Additional info"]["fields"])

    def test_worker_add_fieldsets_contains_additional_info(self):
        model_admin = WorkerAdmin(Worker, admin.site)
        add_fieldsets = dict(model_admin.add_fieldsets)
        self.assertIn("Additional info", add_fieldsets)
        self.assertIn("first_name", add_fieldsets["Additional info"]["fields"])
        self.assertIn("last_name", add_fieldsets["Additional info"]["fields"])
        self.assertIn("position", add_fieldsets["Additional info"]["fields"])
        self.assertIn("team", add_fieldsets["Additional info"]["fields"])

    def test_task_list_display(self):
        url = reverse("admin:tasks_task_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.task.name)
        self.assertContains(res, date_format(self.task.created_at, "DATETIME_FORMAT"))
        self.assertContains(res, date_format(self.task.deadline, "DATETIME_FORMAT"))
        self.assertContains(res, str(self.task.project))
        expected_icon = 'alt="True"' if self.task.is_completed else 'alt="False"'
        self.assertContains(res, expected_icon)
        self.assertContains(res, self.task.get_priority_display())
        self.assertContains(res, str(self.task.task_type))
