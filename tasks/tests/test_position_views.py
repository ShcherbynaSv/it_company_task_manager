from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Position


class PositionListViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:position-list")

    def test_template_and_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/position_list.html")
        self.assertIn("position_list", response.context)
        self.assertIn("search_form", response.context)

    def test_queryset_no_filter_returns_all(self):
        Position.objects.create(name="Developer")
        Position.objects.create(name="Designer")

        response = self.client.get(self.url)
        positions = Position.objects.all()
        self.assertEqual(
            list(response.context["position_list"]),
            list(positions)
        )

    def test_queryset_with_filter_returns_matching(self):
        Position.objects.create(name="Developer")
        Position.objects.create(name="Designer")

        response = self.client.get(self.url, {"name": "dev"})
        positions = Position.objects.filter(name__icontains="dev")
        self.assertEqual(
            list(response.context["position_list"]),
            list(positions)
        )

    def test_queryset_with_filter_no_match(self):
        Position.objects.create(name="Developer")

        response = self.client.get(self.url, {"name": "designer"})
        self.assertEqual(list(response.context["position_list"]), [])

    def test_pagination_first_page(self):
        Position.objects.bulk_create(
            [Position(name=f"Position {i}") for i in range(15)]
        )

        response = self.client.get(self.url)
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["position_list"]), 10)

    def test_pagination_second_page(self):
        Position.objects.bulk_create(
            [Position(name=f"Position {i}") for i in range(15)]
        )

        response = self.client.get(self.url, {"page": 2})
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["position_list"]), 5)

    def test_empty_database(self):
        response = self.client.get(self.url)
        self.assertEqual(list(response.context["position_list"]), [])


class PublicPositionCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:position-create")
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivatePositionCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:position-create")
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/position_form.html")
        self.assertIn("form", response.context)

    def test_create_position_valid_post(self):
        data = {"name": "Designer"}
        response = self.client.post(self.url, data)
        self.assertEqual(Position.objects.count(), 1)
        self.assertEqual(Position.objects.first().name, "Designer")
        self.assertRedirects(response, reverse("tasks:position-list"))

    def test_create_position_invalid_post(self):
        response = self.client.post(self.url, {"name": ""})
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("name", form.errors)
        self.assertEqual(form.errors["name"], ["This field is required."])
        self.assertEqual(Position.objects.count(), 0)


class PublicPositionUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.position = Position.objects.create(name="Designer")
        self.url = reverse(
            "tasks:position-update",
            args=[self.position.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivatePositionUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.client.force_login(self.user)
        self.position = Position.objects.create(name="Designer")
        self.url = reverse(
            "tasks:position-update",
            args=[self.position.id]
        )

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/position_form.html")
        self.assertIn("form", response.context)
        self.assertEqual(response.context["form"].initial["name"], "Designer")

    def test_update_position_valid_post(self):
        response = self.client.post(self.url, {"name": "Developer"})
        self.position.refresh_from_db()
        self.assertEqual(self.position.name, "Developer")
        self.assertRedirects(response, reverse("tasks:position-list"))

    def test_update_position_invalid_post(self):
        response = self.client.post(self.url, {"name": ""})
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.position.refresh_from_db()
        self.assertEqual(self.position.name, "Designer")

    def test_update_nonexistent_object_returns_404(self):
        bad_url = reverse("tasks:position-update", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class PublicPositionDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.position = Position.objects.create(name="Designer")
        self.url = reverse(
            "tasks:position-delete",
            args=[self.position.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivatePositionDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)
        self.position = Position.objects.create(name="Designer")
        self.url = reverse(
            "tasks:position-delete",
            args=[self.position.id]
        )

    def test_logged_in_user_can_access_confirmation_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "tasks/confirm_delete_position.html"
        )
        self.assertEqual(response.context["object"], self.position)

    def test_delete_position_valid_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("tasks:position-list"))
        self.assertFalse(
            Position.objects.filter(id=self.position.id).exists()
        )

    def test_get_request_does_not_delete_object(self):
        self.client.get(self.url)
        self.assertTrue(Position.objects.filter(id=self.position.id).exists())

    def test_delete_nonexistent_object_returns_404(self):
        bad_url = reverse("tasks:position-delete", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)
