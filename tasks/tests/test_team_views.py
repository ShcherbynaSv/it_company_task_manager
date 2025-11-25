from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Team


class TeamListViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:team-list")

    def test_template_and_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/team_list.html")
        self.assertIn("team_list", response.context)
        self.assertIn("search_form", response.context)

    def test_queryset_no_filter_returns_all(self):
        Team.objects.create(name="Alpha team")
        Team.objects.create(name="Beta team")

        response = self.client.get(self.url)
        teams = Team.objects.all()
        self.assertEqual(
            list(response.context["team_list"]),
            list(teams)
        )

    def test_queryset_with_filter_returns_matching(self):
        Team.objects.create(name="Alpha team")
        Team.objects.create(name="Beta team")

        response = self.client.get(self.url, {"name": "lph"})
        teams = Team.objects.filter(name__icontains="lph")
        self.assertEqual(
            list(response.context["team_list"]),
            list(teams)
        )

    def test_queryset_with_filter_no_match(self):
        Team.objects.create(name="Alpha team")

        response = self.client.get(self.url, {"name": "bet"})
        self.assertEqual(list(response.context["team_list"]), [])

    def test_pagination_first_page(self):
        Team.objects.bulk_create(
            [Team(name=f"Team {i}") for i in range(15)]
        )

        response = self.client.get(self.url)
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["team_list"]), 10)

    def test_pagination_second_page(self):
        Team.objects.bulk_create(
            [Team(name=f"Team {i}") for i in range(15)]
        )

        response = self.client.get(self.url, {"page": 2})
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["team_list"]), 5)

    def test_empty_database(self):
        response = self.client.get(self.url)
        self.assertEqual(list(response.context["team_list"]), [])


class PublicTeamCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:team-create")
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivateTeamCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:team-create")
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/team_form.html")
        self.assertIn("form", response.context)

    def test_create_team_valid_post(self):
        data = {"name": "Alpha Team"}
        response = self.client.post(self.url, data)
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(Team.objects.first().name, "Alpha Team")
        self.assertRedirects(response, reverse("tasks:team-list"))

    def test_create_team_invalid_post(self):
        response = self.client.post(self.url, {"name": ""})
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("name", form.errors)
        self.assertEqual(form.errors["name"], ["This field is required."])
        self.assertEqual(Team.objects.count(), 0)


class PublicTeamUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.team = Team.objects.create(name="Alpha team")
        self.url = reverse(
            "tasks:team-update",
            args=[self.team.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivateTeamUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.client.force_login(self.user)
        self.team = Team.objects.create(name="Alpha team")
        self.url = reverse(
            "tasks:team-update",
            args=[self.team.id]
        )

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/team_form.html")
        self.assertIn("form", response.context)
        self.assertEqual(
            response.context["form"].initial["name"],
            "Alpha team"
        )

    def test_update_team_valid_post(self):
        response = self.client.post(self.url, {"name": "Beta team"})
        self.team.refresh_from_db()
        self.assertEqual(self.team.name, "Beta team")
        self.assertRedirects(response, reverse("tasks:team-list"))

    def test_update_team_invalid_post(self):
        response = self.client.post(self.url, {"name": ""})
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.team.refresh_from_db()
        self.assertEqual(self.team.name, "Alpha team")

    def test_update_nonexistent_object_returns_404(self):
        bad_url = reverse("tasks:team-update", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class PublicTeamDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.team = Team.objects.create(name="Alpha team")
        self.url = reverse(
            "tasks:team-delete",
            args=[self.team.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivateTeamDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)
        self.team = Team.objects.create(name="Alpha team")
        self.url = reverse(
            "tasks:team-delete",
            args=[self.team.id]
        )

    def test_logged_in_user_can_access_confirmation_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "tasks/confirm_delete_team.html"
        )
        self.assertEqual(response.context["object"], self.team)

    def test_delete_team_valid_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("tasks:team-list"))
        self.assertFalse(
            Team.objects.filter(id=self.team.id).exists()
        )

    def test_get_request_does_not_delete_object(self):
        self.client.get(self.url)
        self.assertTrue(Team.objects.filter(id=self.team.id).exists())

    def test_delete_nonexistent_object_returns_404(self):
        bad_url = reverse("tasks:team-delete", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)
