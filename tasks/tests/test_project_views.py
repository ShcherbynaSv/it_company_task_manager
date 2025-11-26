from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Team, Project


class ProjectListViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:project-list")
        self.team1 = Team.objects.create(name="Alpha team")
        self.team2 = Team.objects.create(name="Beta team")

    def test_template_and_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/project_list.html")
        self.assertIn("project_list", response.context)
        self.assertIn("search_form", response.context)

    def test_queryset_no_filter_returns_all(self):
        Project.objects.create(
            name="Vacancies web-site",
            description="A new web-site with vacancies",
            team=self.team2
        )
        Project.objects.create(
            name="Online store",
            description="A perfect web-site fore a new online shop",
            team=self.team1
        )

        response = self.client.get(self.url)
        projects = Project.objects.all()
        self.assertEqual(
            list(response.context["project_list"]),
            list(projects)
        )

    def test_queryset_with_filter_returns_matching(self):
        Project.objects.create(
            name="Vacancies web-site",
            description="A new web-site with vacancies",
            team=self.team2
        )
        Project.objects.create(
            name="Online store",
            description="A perfect web-site fore a new online shop",
            team=self.team1
        )

        response = self.client.get(self.url, {"name": "vac"})
        projects = Project.objects.filter(name__icontains="vac")
        self.assertEqual(
            list(response.context["project_list"]),
            list(projects)
        )

    def test_queryset_with_filter_no_match(self):
        Project.objects.create(
            name="Online store",
            description="A perfect web-site fore a new online shop",
            team=self.team2
        )

        response = self.client.get(self.url, {"name": "vac"})
        self.assertEqual(list(response.context["project_list"]), [])

    def test_pagination_first_page(self):
        Project.objects.bulk_create(
            [Project(
                name=f"Project {i}",
                description=f"test-description {i}",
                team=self.team2
            ) for i in range(15)]
        )

        response = self.client.get(self.url)
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["project_list"]), 10)

    def test_pagination_second_page(self):
        Project.objects.bulk_create(
            [Project(
                name=f"Project {i}",
                description=f"test-description {i}",
                team=self.team2
            ) for i in range(15)]
        )

        response = self.client.get(self.url, {"page": 2})
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["project_list"]), 5)

    def test_empty_database(self):
        response = self.client.get(self.url)
        self.assertEqual(list(response.context["project_list"]), [])


class PublicProjectCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:project-create")
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
        self.url = reverse("tasks:project-create")
        self.team = Team.objects.create(name="Alpha team")
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/project_form.html")
        self.assertIn("form", response.context)

    def test_create_project_valid_post(self):
        data = {
            "name": "Test-project",
            "description": "Test-description",
            "team": self.team.id}
        response = self.client.post(self.url, data)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.first().name, "Test-project")
        self.assertEqual(
            Project.objects.first().description,
            "Test-description"
        )
        self.assertEqual(Project.objects.first().team, self.team)
        self.assertRedirects(response, reverse("tasks:project-list"))

    def test_create_project_invalid_post(self):
        response = self.client.post(
            self.url,
            {"name": "", "description": "", "team": ""}
        )
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("name", form.errors)
        self.assertIn("description", form.errors)
        self.assertEqual(form.errors["name"], ["This field is required."])
        self.assertEqual(
            form.errors["description"],
            ["This field is required."]
        )
        self.assertEqual(Project.objects.count(), 0)


class PublicProjectUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.team = Team.objects.create(name="Alpha team")
        self.project = Project.objects.create(
            name="Online store",
            description="A perfect web-site fore a new online shop",
            team=self.team
        )
        self.url = reverse(
            "tasks:project-update",
            args=[self.team.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivateProjectUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.client.force_login(self.user)
        self.team = Team.objects.create(name="Alpha team")
        self.project = Project.objects.create(
            name="Online store",
            description="A perfect web-site fore a new online shop",
            team=self.team
        )
        self.url = reverse(
            "tasks:project-update",
            args=[self.project.id]
        )

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/project_form.html")
        self.assertIn("form", response.context)
        self.assertEqual(
            response.context["form"].initial["name"],
            "Online store"
        )
        self.assertEqual(
            response.context["form"].initial["description"],
            "A perfect web-site fore a new online shop"
        )
        self.assertEqual(
            response.context["form"].initial["team"],
            self.team.id
        )

    def test_update_project_valid_post(self):
        response = self.client.post(self.url, {
            "name": "Vacancies web-site",
            "description": "A new web-site with vacancies"
        })
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Vacancies web-site")
        self.assertEqual(
            self.project.description,
            "A new web-site with vacancies"
        )
        self.assertRedirects(
            response,
            reverse(
                "tasks:project-detail",
                args=[self.project.id]
            )
        )

    def test_update_project_invalid_post(self):
        response = self.client.post(self.url, {"name": "", "description": ""})
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Online store")
        self.assertEqual(
            self.project.description,
            "A perfect web-site fore a new online shop"
        )

    def test_update_nonexistent_object_returns_404(self):
        bad_url = reverse("tasks:project-update", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class PublicProjectDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.team = Team.objects.create(name="Alpha team")
        self.project = Project.objects.create(
            name="Online store",
            description="A perfect web-site fore a new online shop",
            team=self.team
        )
        self.url = reverse(
            "tasks:project-delete",
            args=[self.project.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivateProjectDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)
        self.team = Team.objects.create(name="Alpha team")
        self.project = Project.objects.create(
            name="Online store",
            description="A perfect web-site fore a new online shop",
            team=self.team
        )
        self.url = reverse(
            "tasks:project-delete",
            args=[self.project.id]
        )

    def test_logged_in_user_can_access_confirmation_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "tasks/confirm_delete_project.html"
        )
        self.assertEqual(response.context["object"], self.project)

    def test_delete_project_valid_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("tasks:project-list"))
        self.assertFalse(
            Project.objects.filter(id=self.project.id).exists()
        )

    def test_get_request_does_not_delete_object(self):
        self.client.get(self.url)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_delete_nonexistent_object_returns_404(self):
        bad_url = reverse("tasks:project-delete", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)
