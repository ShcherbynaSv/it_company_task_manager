from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import TaskType


class TaskTypeListViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:task-type-list")

    def test_template_and_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_type_list.html")
        self.assertIn("task_type_list", response.context)
        self.assertIn("search_form", response.context)

    def test_queryset_no_filter_returns_all(self):
        TaskType.objects.create(name="Bug")
        TaskType.objects.create(name="New feature")

        response = self.client.get(self.url)
        task_types = TaskType.objects.all()
        self.assertEqual(
            list(response.context["task_type_list"]),
            list(task_types)
        )

    def test_queryset_with_filter_returns_matching(self):
        TaskType.objects.create(name="Bug")
        TaskType.objects.create(name="New feature")

        response = self.client.get(self.url, {"name": "bu"})
        task_types = TaskType.objects.filter(name__icontains="bu")
        self.assertEqual(
            list(response.context["task_type_list"]),
            list(task_types)
        )

    def test_queryset_with_filter_no_match(self):
        TaskType.objects.create(name="Bug")

        response = self.client.get(self.url, {"name": "new"})
        self.assertEqual(list(response.context["task_type_list"]), [])

    def test_pagination_first_page(self):
        TaskType.objects.bulk_create(
            [TaskType(name=f"Task type {i}") for i in range(15)]
        )

        response = self.client.get(self.url)
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["task_type_list"]), 10)

    def test_pagination_second_page(self):
        TaskType.objects.bulk_create(
            [TaskType(name=f"Task type {i}") for i in range(15)]
        )

        response = self.client.get(self.url, {"page": 2})
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["task_type_list"]), 5)

    def test_empty_database(self):
        response = self.client.get(self.url)
        self.assertEqual(list(response.context["task_type_list"]), [])


class PublicTuskTypeCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:task-type-create")
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivateTaskTypeCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:task-type-create")
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_type_form.html")
        self.assertIn("form", response.context)

    def test_create_task_type_valid_post(self):
        data = {"name": "Bug"}
        response = self.client.post(self.url, data)
        self.assertEqual(TaskType.objects.count(), 1)
        self.assertEqual(TaskType.objects.first().name, "Bug")
        self.assertRedirects(response, reverse("tasks:task-type-list"))

    def test_create_task_type_invalid_post(self):
        response = self.client.post(self.url, {"name": ""})
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("name", form.errors)
        self.assertEqual(form.errors["name"], ["This field is required."])
        self.assertEqual(TaskType.objects.count(), 0)


class PublicTaskTypeUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.task_type = TaskType.objects.create(name="Bug")
        self.url = reverse(
            "tasks:task-type-update",
            args=[self.task_type.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivateTaskTypeUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.client.force_login(self.user)
        self.task_type = TaskType.objects.create(name="Bug")
        self.url = reverse(
            "tasks:task-type-update",
            args=[self.task_type.id]
        )

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_type_form.html")
        self.assertIn("form", response.context)
        self.assertEqual(
            response.context["form"].initial["name"],
            "Bug"
        )

    def test_update_task_type_valid_post(self):
        response = self.client.post(self.url, {"name": "New feature"})
        self.task_type.refresh_from_db()
        self.assertEqual(self.task_type.name, "New feature")
        self.assertRedirects(response, reverse("tasks:task-type-list"))

    def test_update_task_type_invalid_post(self):
        response = self.client.post(self.url, {"name": ""})
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.task_type.refresh_from_db()
        self.assertEqual(self.task_type.name, "Bug")

    def test_update_nonexistent_object_returns_404(self):
        bad_url = reverse("tasks:task-type-update", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class PublicTaskTypeDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.task_type = TaskType.objects.create(name="Bug")
        self.url = reverse(
            "tasks:task-type-delete",
            args=[self.task_type.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivateTaskTypeDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)
        self.task_type = TaskType.objects.create(name="Bug")
        self.url = reverse(
            "tasks:task-type-delete",
            args=[self.task_type.id]
        )

    def test_logged_in_user_can_access_confirmation_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "tasks/confirm_delete_task_type.html"
        )
        self.assertEqual(response.context["object"], self.task_type)

    def test_delete_task_type_valid_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("tasks:task-type-list"))
        self.assertFalse(
            TaskType.objects.filter(id=self.task_type.id).exists()
        )

    def test_get_request_does_not_delete_object(self):
        self.client.get(self.url)
        self.assertTrue(TaskType.objects.filter(id=self.task_type.id).exists())

    def test_delete_nonexistent_object_returns_404(self):
        bad_url = reverse("tasks:task-type-delete", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)
