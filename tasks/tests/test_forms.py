from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from tasks.forms import (
    WorkerCreationForm,
    WorkerUpdateForm,
    TaskForm,
    PositionSearchForm,
    TeamSearchForm,
    TaskTypeSearchForm,
    TagSearchForm,
    ProjectSearchForm,
    WorkerSearchForm,
    TaskSearchForm
)
from tasks.models import Position, Team, TaskType, Project, Tag


class WorkerCreationFormTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.team = Team.objects.create(name="Backend")

    def test_worker_creation_form_valid(self):
        form = WorkerCreationForm(data={
            "username": "john",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "position": self.position.id,
            "team": self.team.id,
        })

        self.assertTrue(form.is_valid(), form.errors)
        worker = form.save()

        self.assertEqual(worker.username, "john")
        self.assertEqual(worker.position, self.position)
        self.assertEqual(worker.team, self.team)

    def test_worker_creation_password_mismatch(self):
        form = WorkerCreationForm(data={
            "username": "john",
            "password1": "StrongPass123!",
            "password2": "WrongPassword",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "position": self.position.id,
            "team": self.team.id,
        })

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)


class WorkerUpdateFormTests(TestCase):
    def setUp(self):
        self.worker = get_user_model().objects.create_user(
            username="john",
            password="test12345"
        )

    def test_update_worker(self):
        form = WorkerUpdateForm(
            data={
                "username": "newname",
                "first_name": "Updated",
                "last_name": "User",
                "email": "updated@example.com",
                "position": "",
                "team": ""
            },
            instance=self.worker
        )

        self.assertTrue(form.is_valid(), form.errors)
        updated = form.save()

        self.assertEqual(updated.username, "newname")
        self.assertEqual(updated.first_name, "Updated")


class TaskFormTests(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name="Bug")
        self.project = Project.objects.create(name="Website")
        self.worker = get_user_model().objects.create_user(
            username="john",
            password="test123"
        )
        self.tag = Tag.objects.create(name="urgent")

    def test_valid_task_form(self):
        form = TaskForm(data={
            "name": "Fix bug",
            "description": "Login issue",
            "deadline": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "is_completed": False,
            "priority": "medium",
            "task_type": self.task_type.id,
            "project": self.project.id,
            "assignees": [self.worker.id],
            "tags": [self.tag.id],
        })

        self.assertTrue(form.is_valid(), form.errors)

        task = form.save()
        self.assertEqual(task.name, "Fix bug")
        self.assertEqual(task.task_type, self.task_type)
        self.assertEqual(task.project, self.project)


class SearchFormsTests(TestCase):
    def test_position_search_form(self):
        form = PositionSearchForm(data={"name": "Dev"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "Dev")

    def test_team_search_form(self):
        form = TeamSearchForm(data={"name": "Backend"})
        self.assertTrue(form.is_valid())

    def test_task_type_search_form(self):
        form = TaskTypeSearchForm(data={"name": "Bug"})
        self.assertTrue(form.is_valid())

    def test_tag_search_form(self):
        form = TagSearchForm(data={"name": "urgent"})
        self.assertTrue(form.is_valid())

    def test_project_search_form(self):
        form = ProjectSearchForm(data={"name": "CRM"})
        self.assertTrue(form.is_valid())

    def test_worker_search_form(self):
        form = WorkerSearchForm(data={"full_name": "John Doe"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["full_name"], "John Doe")

    def test_task_search_form(self):
        form = TaskSearchForm(data={"name": "Login issue"})
        self.assertTrue(form.is_valid())
