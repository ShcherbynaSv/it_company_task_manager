from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from tasks.models import Task, TaskType, Project, Tag
from tasks.forms import TaskSearchForm


class TaskListViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:task-list")
        self.task_type_1 = TaskType.objects.create(name="Bug")
        self.task_type_2 = TaskType.objects.create(name="New Feature")
        self.project_1 = Project.objects.create(name="Vacancies web site")
        self.project_2 = Project.objects.create(name="Online store")
        self.tag_1 = Tag.objects.create(name="Urgent")
        self.tag_2 = Tag.objects.create(name="Blocked")
        self.task_1 = Task.objects.create(
            name="Test-task-1",
            description="test-description",
            deadline=timezone.now() + timedelta(days=7),
            task_type=self.task_type_1,
            project=self.project_1
        )
        self.task_1.tags.add(self.tag_1)
        self.task_2 = Task.objects.create(
            name="Test-task-2",
            description="test-description",
            deadline=timezone.now() + timedelta(days=7),
            task_type=self.task_type_2,
            project=self.project_2
        )
        self.task_2.tags.add(self.tag_2)

    def test_template_and_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_list.html")
        self.assertIn("task_list", response.context)
        self.assertIn("search_form", response.context)
        self.assertIn("selected_task_type", response.context)
        self.assertIn("selected_tag", response.context)

    def test_queryset_no_filter_returns_all(self):
        response = self.client.get(self.url)
        self.assertEqual(
            list(response.context["task_list"]), [self.task_1, self.task_2])

    def test_filter_by_tag(self):
        response = self.client.get(
            self.url,
            {"tags": self.tag_1.id}
        )
        self.assertIn(self.task_1, response.context["task_list"])
        self.assertNotIn(self.task_2, response.context["task_list"])
        self.assertEqual(
            response.context["selected_tag"],
            self.tag_1
        )

    def test_filter_by_task_type(self):
        response = self.client.get(
            self.url,
            {"task_type": self.task_type_1.id}
        )
        self.assertIn(self.task_1, response.context["task_list"])
        self.assertNotIn(self.task_2, response.context["task_list"])
        self.assertEqual(
            response.context["selected_task_type"],
            self.task_type_1
        )

    def test_filter_by_name(self):
        response = self.client.get(self.url, {"name": "1"})
        self.assertIn(self.task_1, response.context["task_list"])
        self.assertNotIn(self.task_2, response.context["task_list"])
        self.assertIsInstance(response.context["search_form"], TaskSearchForm)
        self.assertEqual(
            response.context["search_form"].initial.get("name"), "1"
        )

    def test_combined_filters(self):
        response = self.client.get(
            self.url,
            {
                "task_type": self.task_type_1.id,
                "tags": self.tag_1.id,
                "name": "1"
            }
        )
        self.assertIn(self.task_1, response.context["task_list"])
        self.assertNotIn(self.task_2, response.context["task_list"])

    def test_pagination(self):
        [
            Task.objects.create(
                name=f"task {i}",
                description=f"test-description {i}",
                deadline=timezone.now() + timedelta(days=7),
                task_type=self.task_type_1,
                project=self.project_1
            )
            for i in range(15)
        ]
        response = self.client.get(self.url)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["task_list"]), 10)

        response = self.client.get(self.url, {"page": 2})
        self.assertEqual(len(response.context["task_list"]), 7)

    def test_empty_database(self):
        response = self.client.get(self.url)
        self.assertEqual(
            list(response.context["task_list"]),
            [self.task_1, self.task_2]
        )


class TaskDetailViewTests(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name="Bug")
        self.project = Project.objects.create(name="Vacancies web site")
        self.tag = Tag.objects.create(name="Urgent")
        self.worker = get_user_model().objects.create_user(
            username="chef",
            password="pass"
        )
        self.task = Task.objects.create(
            name="Test-task",
            description="Test-description",
            deadline=timezone.now() + timedelta(days=7),
            task_type=self.task_type,
            project=self.project
        )
        self.task.tags.add(self.tag)
        self.task.assignees.add(self.worker)
        self.url = reverse("tasks:task-detail", args=[self.task.id])

    def test_detail_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_detail.html")
        self.assertEqual(response.context["task"], self.task)

    def test_context_includes_related_objects(self):
        response = self.client.get(self.url)
        task = response.context["task"]
        self.assertEqual(task.task_type, self.task_type)
        self.assertIn(self.tag, task.tags.all())
        self.assertIn(self.worker, task.assignees.all())

    def test_nonexistent_task_returns_404(self):
        bad_url = reverse("tasks:task-detail", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class PublicTaskCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:task-create")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivateTaskCreateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user", password="password123"
        )
        self.client.force_login(self.user)
        self.task_type = TaskType.objects.create(name="Bug")
        self.project = Project.objects.create(name="Vacancies web site")
        self.tag = Tag.objects.create(name="Urgent")
        self.url = reverse("tasks:task-create")

    def test_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_form.html")
        self.assertIn("form", response.context)

    def test_create_valid_task(self):

        data = {
            "name": "Test-task-1",
            "description": "Test-description",
            "deadline": (
                    timezone.now() + timedelta(days=7)
            ).strftime("%Y-%m-%dT%H:%M"),
            "task_type": self.task_type.id,
            "project": self.project.id,
            "tags": [self.tag.id],
            "priority": "high",
            "assignees": [self.user.id],
        }

        response = self.client.post(self.url, data)
        task = Task.objects.get(name="Test-task-1")
        self.assertEqual(task.description, "Test-description")
        self.assertEqual(task.task_type, self.task_type)
        self.assertEqual(task.project, self.project)
        self.assertIn(self.tag, task.tags.all())
        self.assertRedirects(response, reverse("tasks:task-list"))

    def test_create_invalid_dish(self):
        response = self.client.post(self.url, {"name": ""})
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(Task.objects.count(), 0)


class PublicTaskUpdateViewTests(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name="Bug")
        self.project = Project.objects.create(name="Vacancies web site")
        self.tag = Tag.objects.create(name="Urgent")
        self.task = Task.objects.create(
            name="Test-task",
            description="Test-description",
            deadline=timezone.now() + timedelta(days=7),
            task_type=self.task_type,
            project=self.project
        )
        self.url = reverse("tasks:task-update", args=[self.task.id])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivateTaskUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user", password="password123"
        )
        self.client.force_login(self.user)

        self.task_type = TaskType.objects.create(name="Bug")
        self.new_task_type = TaskType.objects.create(name="New feature")

        self.project = Project.objects.create(name="Vacancies web site")

        self.tag = Tag.objects.create(name="Urgent")
        self.new_tag = Tag.objects.create(name="Blocked")

        self.task = Task.objects.create(
            name="Test-task",
            description="Test-description",
            deadline=timezone.now() + timedelta(days=7),
            task_type=self.task_type,
            project=self.project
        )
        self.task.tags.add(self.tag)

        self.url = reverse("tasks:task-update", args=[self.task.id])

    def test_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_form.html")
        self.assertIn("form", response.context)
        self.assertEqual(response.context["form"].initial["name"], "Test-task")

    def test_update_valid_task(self):
        data = {
            "name": "Test-task",
            "description": "Updated-description",
            "deadline": (
                    timezone.now() + timedelta(days=7)
            ).strftime("%Y-%m-%dT%H:%M"),
            "task_type": self.new_task_type.id,
            "project": self.task.project.id,
            "tags": [self.new_tag.id],
            "priority": self.task.priority,
            "assignees": [
                self.user.id for self.user in self.task.assignees.all()
            ] if self.task.assignees.exists() else [self.user.id],
            "is_completed": self.task.is_completed,
        }
        response = self.client.post(self.url, data)
        self.task.refresh_from_db()

        self.assertEqual(self.task.name, "Test-task")
        self.assertEqual(self.task.description, "Updated-description")
        self.assertEqual(self.task.task_type, self.new_task_type)
        self.assertIn(self.new_tag, self.task.tags.all())
        self.assertRedirects(
            response,
            reverse("tasks:task-detail", args=[self.task.id])
        )

    def test_update_invalid_task(self):
        response = self.client.post(
            self.url,
            {"name": "", "task_type": self.task_type.id}
        )
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, "Test-task")

    def test_update_nonexistent_task_returns_404(self):
        bad_url = reverse("tasks:task-update", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class PublicTaskDeleteViewTests(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name="Bug")
        self.project = Project.objects.create(name="Vacancies web site")
        self.tag = Tag.objects.create(name="Urgent")
        self.task = Task.objects.create(
            name="Test-task",
            description="Test-description",
            deadline=timezone.now() + timedelta(days=7),
            task_type=self.task_type,
            project=self.project
        )
        self.url = reverse("tasks:task-update", args=[self.task.id])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivateTaskDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user", password="password123"
        )
        self.client.force_login(self.user)

        self.task_type = TaskType.objects.create(name="Bug")
        self.project = Project.objects.create(name="Vacancies web site")
        self.tag = Tag.objects.create(name="Urgent")
        self.task = Task.objects.create(
            name="Test-task",
            description="Test-description",
            deadline=timezone.now() + timedelta(days=7),
            task_type=self.task_type,
            project=self.project
        )
        self.url = reverse("tasks:task-delete", args=[self.task.id])

    def test_access_delete_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/confirm_delete_task.html")
        self.assertIn("object", response.context)
        self.assertEqual(response.context["object"], self.task)

    def test_delete_task(self):
        response = self.client.post(self.url)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())
        self.assertRedirects(response, reverse("tasks:task-list"))

    def test_delete_nonexistent_task_returns_404(self):
        bad_url = reverse("tasks:task-delete", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)
