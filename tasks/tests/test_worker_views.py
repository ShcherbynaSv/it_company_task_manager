from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Worker, Position, Team


class WorkerListViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:worker-list")

    def test_template_and_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/worker_list.html")
        self.assertIn("worker_list", response.context)
        self.assertIn("search_form", response.context)

    def test_no_filter_returns_all_workers(self):
        worker1 = get_user_model().objects.create_user(
            first_name="Jane",
            last_name="Doe",
            username="jane",
            password="password1234"
        )
        worker2 = get_user_model().objects.create_user(
            first_name="John",
            last_name="Smith",
            username="john",
            password="password1234"
        )

        response = self.client.get(self.url)
        self.assertEqual(
            list(response.context["worker_list"]),
            [worker1, worker2]
        )

    def test_filter_by_first_name(self):
        worker = get_user_model().objects.create_user(
            first_name="Alice",
            last_name="Brown",
            username="alice",
            password="password1234"
        )
        get_user_model().objects.create_user(
            first_name="Bob",
            last_name="Green",
            username="bob",
            password="password1234"
        )

        response = self.client.get(self.url, {"full_name": "alice"})
        self.assertEqual(list(response.context["worker_list"]), [worker])

    def test_filter_by_last_name(self):
        worker = get_user_model().objects.create_user(
            first_name="Charlie",
            last_name="Jones",
            username="charlie",
            password="password1234"
        )
        get_user_model().objects.create_user(
            first_name="David",
            last_name="White",
            username="david",
            password="password1234"
        )

        response = self.client.get(self.url, {"full_name": "jones"})
        self.assertEqual(list(response.context["worker_list"]), [worker])

    def test_filter_by_full_name_in_order(self):
        worker = get_user_model().objects.create_user(
            first_name="Eve",
            last_name="Stone",
            username="eve",
            password="password1234"
        )
        response = self.client.get(self.url, {"full_name": "Eve Stone"})
        self.assertEqual(list(response.context["worker_list"]), [worker])

    def test_filter_by_full_name_reversed(self):
        worker = get_user_model().objects.create_user(
            first_name="Frank",
            last_name="Taylor",
            username="frank",
            password="password1234"
        )
        response = self.client.get(self.url, {"full_name": "Taylor Frank"})
        self.assertEqual(list(response.context["worker_list"]), [worker])

    def test_filter_case_insensitive(self):
        worker = get_user_model().objects.create_user(
            first_name="Grace",
            last_name="Hill",
            username="grace",
            password="password1234"
        )
        response = self.client.get(self.url, {"full_name": "grace"})
        self.assertEqual(list(response.context["worker_list"]), [worker])

    def test_filter_no_match_returns_empty(self):
        get_user_model().objects.create_user(
            first_name="Henry",
            last_name="Ford",
            username="henry",
            password="password1234"
        )
        response = self.client.get(self.url, {"full_name": "Unknown"})
        self.assertEqual(list(response.context["worker_list"]), [])

    def test_filter_with_extra_spaces(self):
        worker = get_user_model().objects.create_user(
            first_name="Ivy",
            last_name="Brown",
            username="ivy",
            password="password1234"
        )
        response = self.client.get(self.url, {"full_name": "   Ivy   "})
        self.assertEqual(list(response.context["worker_list"]), [worker])

    def test_empty_query_param_returns_all(self):
        worker = get_user_model().objects.create_user(
            first_name="Kate",
            last_name="Green",
            username="kate",
            password="password1234"
        )
        response = self.client.get(self.url, {"full_name": ""})
        self.assertIn(worker, list(response.context["worker_list"]))

    def test_pagination_first_page(self):
        Worker.objects.bulk_create(
            [
                Worker(
                    first_name=f"First{i}",
                    last_name=f"Last{i}",
                    username=f"user{i}"
                )
                for i in range(15)
            ]
        )
        response = self.client.get(self.url)
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["worker_list"]), 10)

    def test_pagination_second_page(self):
        Worker.objects.bulk_create(
            [
                Worker(
                    first_name=f"First{i}",
                    last_name=f"Last{i}",
                    username=f"user{i}"
                )
                for i in range(15)
            ]
        )
        response = self.client.get(self.url, {"page": 2})
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["worker_list"]), 5)

    def test_empty_database(self):
        response = self.client.get(self.url)
        self.assertEqual(list(response.context["worker_list"]), [])


class WorkerDetailViewTests(TestCase):
    def setUp(self):
        self.worker = get_user_model().objects.create_user(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            password="password1234"
        )
        self.url = reverse("tasks:worker-detail", args=[self.worker.id])

    def test_view_uses_correct_template_and_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/worker_detail.html")
        self.assertEqual(response.context["object"], self.worker)
        self.assertEqual(response.context["worker"], self.worker)

    def test_nonexistent_worker_returns_404(self):
        bad_url = reverse("tasks:worker-detail", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class PublicWorkerCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:worker-create")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivateWorkerCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:worker-create")
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/worker_form.html")
        self.assertIn("form", response.context)

    def test_create_worker_valid_post(self):
        data = {
            "username": "jane",
            "first_name": "Jane",
            "last_name": "Doe",
            "password1": "password_4321",
            "password2": "password_4321"
        }
        response = self.client.post(self.url, data)

        user = get_user_model().objects.get(username="jane")
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "Doe")
        self.assertTrue(user.check_password("password_4321"))
        self.assertRedirects(response, reverse("tasks:worker-list"))

    def test_create_worker_invalid_post_missing_fields(self):
        data = {
            "username": "",
            "first_name": "",
            "last_name": "",
            "password1": "",
            "password2": ""
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_create_worker_invalid_post_password_mismatch(self):
        data = {
            "username": "jane",
            "first_name": "Jane",
            "last_name": "Doe",
            "password1": "password_4321",
            "password2": "wrongpassword"
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertEqual(
            get_user_model().objects.filter(username="jane").count(),
            0
        )


class PublicWorkerUpdateViewTests(TestCase):
    def setUp(self):
        self.worker = get_user_model().objects.create_user(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            password="password1234"
        )
        self.url = reverse(
            "tasks:worker-update",
            args=[self.worker.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivateWorkerUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.client.force_login(self.user)
        self.worker = get_user_model().objects.create_user(
            first_name="Jane",
            last_name="Doe",
            username="janendoe",
            password="password_4321"
        )
        self.url = reverse(
            "tasks:worker-update",
            args=[self.worker.id]
        )

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/worker_form.html")
        self.assertIn("form", response.context)

    def test_update_worker_valid_post(self):
        data = {
            "username": "jane",
            "first_name": "Janet",
            "last_name": "Doe",
        }
        response = self.client.post(self.url, data)
        self.worker.refresh_from_db()
        self.assertEqual(self.worker.first_name, "Janet")
        self.assertRedirects(
            response,
            reverse("tasks:worker-detail", kwargs={"pk": self.worker.id})
        )

    def test_update_worker_invalid_post_missing_fields(self):
        data = {"username": "", "first_name": "", "last_name": ""}
        response = self.client.post(self.url, data)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.worker.refresh_from_db()
        self.assertEqual(self.worker.first_name, "Jane")

    def test_update_nonexistent_object_returns_404(self):
        bad_url = reverse("tasks:worker-update", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class PublicWorkerDeleteViewTests(TestCase):
    def setUp(self):
        self.cook = get_user_model().objects.create_user(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            password="password1234"
        )
        self.url = reverse(
            "tasks:worker-delete",
            args=[self.cook.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivateWorkerDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)
        self.worker = get_user_model().objects.create_user(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            password="password1234"
        )
        self.url = reverse(
            "tasks:worker-delete",
            args=[self.worker.id]
        )

    def test_logged_in_user_can_access_confirmation_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "tasks/confirm_delete_worker.html"
        )
        self.assertEqual(response.context["object"], self.worker)

    def test_delete_worker_valid_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("tasks:worker-list"))
        self.assertFalse(
            get_user_model().objects.filter(id=self.worker.id).exists()
        )

    def test_get_request_does_not_delete_object(self):
        self.client.get(self.url)
        self.assertTrue(
            get_user_model().objects.filter(id=self.worker.id).exists()
        )

    def test_delete_nonexistent_object_returns_404(self):
        bad_url = reverse("tasks:worker-delete", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)
